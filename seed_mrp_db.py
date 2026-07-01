#!/usr/bin/env python3
"""
Seed MRP database from MRP Master JSON.
Clears existing data, inserts from MRP_Master.json.
"""
import json
import sys
from pathlib import Path

import psycopg2

MASTER_PATH = Path(__file__).parent / "mrp_master_output" / "MRP_Master.json"
DB_DSN = "host=localhost port=5434 dbname=mrp user=mrp password=mrp_secret_2026"

def load_master():
    with open(MASTER_PATH) as f:
        return json.load(f)

def get_state_map(cur):
    """abbreviation -> id"""
    cur.execute("SELECT id, abbreviation FROM states")
    return {row[1]: row[0] for row in cur.fetchall()}

def seed_repeaters(cur, records, state_map):
    cur.execute("DELETE FROM repeaters")
    inserted = 0
    for r in records:
        st = state_map.get(r.get("state"))
        lat = r.get("latitude")
        lon = r.get("longitude")
        geog = f"SRID=4326;POINT({lon} {lat})" if lat and lon else None

        callsign = r.get("callsign", "")
        notes = r.get("notes", "")
        name = f"{callsign} — {notes.split('.')[0][:80]}" if callsign else "Unknown"

        # Derive duplex from offset if not set
        duplex = r.get("duplex")
        if not duplex:
            off = r.get("offset_mhz")
            if off is None or off == 0:
                duplex = "simplex"
            elif off > 0:
                duplex = "plus"
            else:
                duplex = "minus"

        cur.execute("""
            INSERT INTO repeaters (
                id, name, callsign, rx_freq, tx_freq, "offset", offset_dir,
                tone, tone_type, dcs_code, bandwidth, mode, duplex, power,
                latitude, longitude, altitude, coverage_radius,
                state_id, country, category, status, last_verified, source, notes,
                geog_point
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                CASE WHEN %s IS NOT NULL THEN ST_GeogFromText(%s) ELSE NULL END
            )
            ON CONFLICT (callsign) DO UPDATE SET
                rx_freq=EXCLUDED.rx_freq, tx_freq=EXCLUDED.tx_freq,
                "offset"=EXCLUDED."offset", tone=EXCLUDED.tone,
                status=EXCLUDED.status, notes=EXCLUDED.notes,
                updated_at=NOW()
        """, (
            r["uuid"], name, callsign,
            r["rx_freq_mhz"], r["tx_freq_mhz"],
            r.get("offset_mhz"), r.get("offset_dir"),
            r.get("tone_hz"), r.get("tone_type"),
            r.get("dcs_code"),
            r.get("bandwidth"), r.get("mode"), duplex,
            r.get("power_watts"),
            lat, lon,
            r.get("altitude_m"), r.get("coverage_radius_km"),
            st, r.get("country", "MYS"),
            r.get("category", "Repeater"),
            r.get("status", "active"),
            r.get("last_verified"), r.get("source"),
            r.get("notes"),
            geog, geog,  # two params for CASE WHEN %s ... ST_GeogFromText(%s)
        ))
        inserted += 1
    return inserted

def seed_simplex(cur, records):
    cur.execute("DELETE FROM simplex_channels")
    inserted = 0
    for r in records:
        freq = r["rx_freq_mhz"]
        band = "VHF" if freq < 200 else "UHF"
        name = r.get("notes", "Simplex").split(":")[0].strip()[:100] if r.get("notes") else f"Simplex {freq}"
        cur.execute("""
            INSERT INTO simplex_channels (name, frequency, band, mode, notes, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (frequency) DO UPDATE SET name=EXCLUDED.name, notes=EXCLUDED.notes
        """, (name, freq, band, r.get("mode", "fm"), r.get("notes"), r.get("subcategory")))
        inserted += 1
    return inserted

def seed_marine(cur, records):
    cur.execute("DELETE FROM marine_channels")
    inserted = 0
    for r in records:
        notes = r.get("notes", "")
        # Try to extract channel number from notes like "Ch 16: ..."
        ch = r.get("channel_no", "")
        if notes.startswith("Ch "):
            parts = notes.split(":")
            ch = parts[0].replace("Ch ", "").strip()

        name = notes.split("—")[0].split(":")[0].strip()[:100] if notes else f"Marine {ch}"
        tx = r.get("tx_freq_mhz", r["rx_freq_mhz"])

        cur.execute("""
            INSERT INTO marine_channels (channel_number, name, tx_freq, rx_freq, mode, description, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (channel_number) DO UPDATE SET
                tx_freq=EXCLUDED.tx_freq, rx_freq=EXCLUDED.rx_freq, description=EXCLUDED.description
        """, (ch, name, tx, r["rx_freq_mhz"], r.get("mode", "fm"), notes, r.get("subcategory")))
        inserted += 1
    return inserted

def seed_aviation(cur, records):
    cur.execute("DELETE FROM aviation_freqs")
    inserted = 0
    for r in records:
        notes = r.get("notes", "")
        # Extract airport name
        airport = ""
        service = r.get("subcategory", "")
        if "—" in notes:
            parts = notes.split("—")
            airport = parts[0].replace("RX ONLY", "").strip()[:100]
        name = notes.replace("RX ONLY — ", "").replace("RX ONLY—", "").strip()[:100] or f"Aviation {r['rx_freq_mhz']}"

        cur.execute("""
            INSERT INTO aviation_freqs (name, frequency, airport, service_type, latitude, longitude, notes, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET frequency=EXCLUDED.frequency, notes=EXCLUDED.notes
        """, (name, r["rx_freq_mhz"], airport, service,
              r.get("latitude"), r.get("longitude"),
              notes, service))
        inserted += 1
    return inserted

def seed_aprs(cur, records, state_map):
    cur.execute("DELETE FROM aprs_objects")
    inserted = 0
    for r in records:
        st = state_map.get(r.get("state"))
        notes = r.get("notes", "")
        # Try to get callsign from notes or channel_no
        callsign = r.get("channel_no", "APRS")
        if notes and notes[0:2].isalpha():
            callsign = notes.split(" ")[0].strip()[:20]

        name = notes.split("—")[0].strip()[:100] if notes else "APRS"
        aprs_type = r.get("subcategory", "digi").lower()

        cur.execute("""
            INSERT INTO aprs_objects (callsign, name, frequency, type, latitude, longitude,
                                      state_id, status, notes, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (callsign) DO UPDATE SET
                frequency=EXCLUDED.frequency, notes=EXCLUDED.notes
        """, (callsign, name, r["rx_freq_mhz"], aprs_type,
              r.get("latitude"), r.get("longitude"),
              st, "active", notes, r.get("subcategory")))
        inserted += 1
    return inserted

def seed_satellites(cur, records):
    cur.execute("DELETE FROM satellites")
    inserted = 0
    for r in records:
        notes = r.get("notes", "")
        name = notes.split("—")[0].split("(")[0].strip()[:100] if notes else r.get("channel_no", "Sat")
        # Skip if name is empty
        if not name:
            name = f"Sat-{r['rx_freq_mhz']}"

        cur.execute("""
            INSERT INTO satellites (name, uplink, downlink, mode, status, notes, category)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET
                uplink=EXCLUDED.uplink, downlink=EXCLUDED.downlink
        """, (name, r.get("tx_freq_mhz"), r.get("rx_freq_mhz"),
              r.get("mode", "fm"), "active", notes, r.get("subcategory")))
        inserted += 1
    return inserted

def seed_calling(cur, records):
    cur.execute("DELETE FROM calling_freqs")
    inserted = 0
    for r in records:
        freq = r["rx_freq_mhz"]
        notes = r.get("notes", "")
        name = notes.split("—")[0].strip()[:100] if notes else f"Calling {freq}"
        band = "HF" if freq < 30 else ("VHF" if freq < 300 else "UHF")

        cur.execute("""
            INSERT INTO calling_freqs (name, frequency, band, mode, description, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET frequency=EXCLUDED.frequency, description=EXCLUDED.description
        """, (name, freq, band, r.get("mode", "fm"), notes, r.get("subcategory")))
        inserted += 1
    return inserted

def seed_emergency(cur, records):
    cur.execute("DELETE FROM emergency_freqs")
    inserted = 0
    for r in records:
        notes = r.get("notes", "")
        name = notes.split("—")[0].strip()[:100] if notes else f"Emergency {r['rx_freq_mhz']}"
        service = r.get("subcategory", "Emergency")

        cur.execute("""
            INSERT INTO emergency_freqs (name, frequency, service, mode, notes, category)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (name) DO UPDATE SET frequency=EXCLUDED.frequency, notes=EXCLUDED.notes
        """, (name, r["rx_freq_mhz"], service, r.get("mode", "fm"), notes, service))
        inserted += 1
    return inserted

def main():
    print("Loading MRP Master...")
    master = load_master()
    sheets = master["sheets"]

    print("Connecting to database...")
    conn = psycopg2.connect(DB_DSN)
    conn.autocommit = False
    cur = conn.cursor()

    state_map = get_state_map(cur)
    print(f"States loaded: {len(state_map)}")

    counts = {}

    try:
        print("\nSeeding tables...")
        counts["repeaters"] = seed_repeaters(cur, sheets["01_Repeaters"], state_map)
        print(f"  ✓ repeaters: {counts['repeaters']}")

        counts["simplex"] = seed_simplex(cur, sheets["02_VHF_Simplex"] + sheets["03_UHF_Simplex"])
        print(f"  ✓ simplex_channels: {counts['simplex']}")

        counts["marine"] = seed_marine(cur, sheets["04_Marine"])
        print(f"  ✓ marine_channels: {counts['marine']}")

        counts["aviation"] = seed_aviation(cur, sheets["05_Aviation"])
        print(f"  ✓ aviation_freqs: {counts['aviation']}")

        counts["aprs"] = seed_aprs(cur, sheets["06_APRS"], state_map)
        print(f"  ✓ aprs_objects: {counts['aprs']}")

        counts["satellites"] = seed_satellites(cur, sheets["07_Satellites"])
        print(f"  ✓ satellites: {counts['satellites']}")

        counts["calling"] = seed_calling(cur, sheets["08_Calling"])
        print(f"  ✓ calling_freqs: {counts['calling']}")

        counts["emergency"] = seed_emergency(cur, sheets["09_Emergency"])
        print(f"  ✓ emergency_freqs: {counts['emergency']}")

        conn.commit()
        print(f"\n{'='*50}")
        print("DATABASE SEEDED SUCCESSFULLY")
        print(f"{'='*50}")
        total = sum(counts.values())
        print(f"Total records inserted: {total}")
        for table, count in counts.items():
            print(f"  {table}: {count}")

    except Exception as e:
        conn.rollback()
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    main()
