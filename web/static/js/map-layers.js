/**
 * Malaysia Radio Pack v2.0 — Map Layer Management
 * Base layers, overlays, custom marker icons, and legend
 */

const MapLayers = (() => {
  // ---- Base tile layers ----
  const baseLayers = {
    'CartoDB Dark': L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: 'abcd',
      maxZoom: 19,
    }),
    'OpenStreetMap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }),
    'Satellite': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
      attribution: '&copy; Esri',
      maxZoom: 18,
    }),
  };

  // ---- Custom marker icon factory ----
  function createMarkerIcon(mode) {
    const colors = {
      'FM':     { bg: '#3b82f6', shadow: 'rgba(59,130,246,0.4)' },
      'DMR':    { bg: '#10b981', shadow: 'rgba(16,185,129,0.4)' },
      'C4FM':   { bg: '#8b5cf6', shadow: 'rgba(139,92,246,0.4)' },
      'D-Star': { bg: '#f59e0b', shadow: 'rgba(245,158,11,0.4)' },
      'D-STAR': { bg: '#f59e0b', shadow: 'rgba(245,158,11,0.4)' },
      'Mixed':  { bg: '#06b6d4', shadow: 'rgba(6,182,212,0.4)' },
    };
    const c = colors[mode] || colors['FM'];

    return L.divIcon({
      className: 'custom-marker',
      html: `<div style="
        width: 14px; height: 14px;
        background: ${c.bg};
        border: 2px solid rgba(255,255,255,0.8);
        border-radius: 50%;
        box-shadow: 0 0 12px ${c.shadow}, 0 2px 6px rgba(0,0,0,0.3);
        transition: transform 0.2s;
      "></div>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7],
      popupAnchor: [0, -10],
    });
  }

  // ---- Legend control ----
  function createLegendControl() {
    const legend = L.control({ position: 'bottomright' });
    legend.onAdd = function () {
      const div = L.DomUtil.create('div', 'map-legend');
      div.innerHTML = `
        <h4>Modes</h4>
        <div class="legend-item"><span class="legend-dot" style="background:#3b82f6;color:#3b82f6"></span> FM</div>
        <div class="legend-item"><span class="legend-dot" style="background:#10b981;color:#10b981"></span> DMR</div>
        <div class="legend-item"><span class="legend-dot" style="background:#8b5cf6;color:#8b5cf6"></span> C4FM</div>
        <div class="legend-item"><span class="legend-dot" style="background:#f59e0b;color:#f59e0b"></span> D-Star</div>
        <div class="legend-item"><span class="legend-dot" style="background:#06b6d4;color:#06b6d4"></span> Mixed</div>
      `;
      return div;
    };
    return legend;
  }

  // ---- Build popup HTML ----
  function buildPopup(repeater) {
    const modeClass = (repeater.mode || 'FM').toLowerCase().replace('-', '');
    const statusClass = (repeater.status || 'active').toLowerCase();
    const statusDot = statusClass === 'active' ? 'active' : statusClass === 'inactive' ? 'inactive' : 'unknown';

    return `
      <div class="popup-name">${escapeHtml(repeater.name || 'Unknown')}</div>
      <div class="popup-callsign">${escapeHtml(repeater.callsign || '—')}</div>
      <div class="popup-grid">
        <span class="popup-label">RX</span>
        <span class="popup-value">${formatFreq(repeater.rx_freq)}</span>
        <span class="popup-label">TX</span>
        <span class="popup-value">${formatFreq(repeater.tx_freq)}</span>
        <span class="popup-label">Mode</span>
        <span><span class="popup-mode-badge ${modeClass}">${escapeHtml(repeater.mode || 'FM')}</span></span>
        <span class="popup-label">State</span>
        <span class="popup-value">${escapeHtml(repeater.state || '—')}</span>
        <span class="popup-label">Status</span>
        <span><span class="status-dot ${statusDot}"></span>${escapeHtml(repeater.status || 'unknown')}</span>
      </div>
    `;
  }

  // ---- Helpers ----
  function formatFreq(freq) {
    if (!freq && freq !== 0) return '—';
    return parseFloat(freq).toFixed(4) + ' MHz';
  }

  function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  }

  return {
    baseLayers,
    createMarkerIcon,
    createLegendControl,
    buildPopup,
    formatFreq,
  };
})();
