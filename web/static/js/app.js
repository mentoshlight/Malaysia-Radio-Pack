/**
 * Malaysia Radio Pack v2.0 — Main Application
 */

const API_BASE = '/api/v1';

// ---- State ----
let map, markerClusterGroup, coverageLayerGroup;
let allRepeaters = [];
let filteredRepeaters = [];
let currentPage = 1;
const PAGE_SIZE = 25;
let sortColumn = null;
let sortDirection = 'asc';
let searchDebounceTimer = null;
let charts = { states: null, modes: null, bands: null };

// ---- DOM Ready ----
document.addEventListener('DOMContentLoaded', () => {
  initMap();
  setupNavigation();
  setupSearch();
  setupTableSorting();
  setupScrollAnimations();
  loadInitialData();
});

// ============================================================
//  MAP
// ============================================================
function initMap() {
  map = L.map('leafletMap', {
    center: [4.2105, 101.9758],
    zoom: 7,
    zoomControl: true,
    attributionControl: true,
  });

  // Default base layer: CartoDB Dark
  MapLayers.baseLayers['CartoDB Dark'].addTo(map);

  // Marker cluster group
  markerClusterGroup = L.markerClusterGroup({
    maxClusterRadius: 50,
    spiderfyOnMaxZoom: true,
    showCoverageOnHover: false,
    chunkedLoading: true,
    iconCreateFunction: function (cluster) {
      const count = cluster.getChildCount();
      let size = 'small';
      if (count >= 50) size = 'large';
      else if (count >= 10) size = 'medium';
      return L.divIcon({
        html: `<div><span>${count}</span></div>`,
        className: `marker-cluster marker-cluster-${size}`,
        iconSize: L.point(40, 40),
      });
    },
  });

  // Coverage circles layer
  coverageLayerGroup = L.layerGroup();

  // Overlay layers
  const overlays = {
    'Repeaters': markerClusterGroup,
    'Coverage Circles': coverageLayerGroup,
  };

  // Layer control
  L.control.layers(MapLayers.baseLayers, overlays, { position: 'topright', collapsed: true }).addTo(map);

  // Legend
  MapLayers.createLegendControl().addTo(map);

  map.addLayer(markerClusterGroup);
  map.addLayer(coverageLayerGroup);
}

function addRepeaterMarker(repeater) {
  if (!repeater.latitude || !repeater.longitude) return;

  const lat = parseFloat(repeater.latitude);
  const lng = parseFloat(repeater.longitude);
  if (isNaN(lat) || isNaN(lng)) return;

  const icon = MapLayers.createMarkerIcon(repeater.mode || 'FM');
  const marker = L.marker([lat, lng], { icon });

  // Bind popup
  marker.bindPopup(MapLayers.buildPopup(repeater), { maxWidth: 320 });

  // On popup open, add coverage circle
  marker.on('popupopen', () => {
    const radiusKm = parseFloat(repeater.coverage_radius) || 30;
    const circle = L.circle([lat, lng], {
      radius: radiusKm * 1000,
      color: '#3b82f6',
      fillColor: '#3b82f6',
      fillOpacity: 0.06,
      weight: 1,
      dashArray: '6 4',
    });
    circle._coverageId = repeater.callsign || repeater.id;
    coverageLayerGroup.addLayer(circle);
    marker._coverageCircle = circle;
  });

  marker.on('popupclose', () => {
    if (marker._coverageCircle) {
      coverageLayerGroup.removeLayer(marker._coverageCircle);
      marker._coverageCircle = null;
    }
  });

  markerClusterGroup.addLayer(marker);
}

function updateMapMarkers(repeaters) {
  markerClusterGroup.clearLayers();
  coverageLayerGroup.clearLayers();
  repeaters.forEach(r => addRepeaterMarker(r));
  document.getElementById('mapMarkerCount').textContent = repeaters.length;
}

// ============================================================
//  DATA LOADING
// ============================================================
async function loadInitialData() {
  showLoading();
  try {
    await Promise.all([loadRepeaters(), loadStats(), populateFilters()]);
  } catch (err) {
    showToast('Failed to load data. Is the API running?', 'error');
    console.error(err);
  } finally {
    hideLoading();
  }
}

async function loadRepeaters() {
  try {
    const resp = await fetch(`${API_BASE}/repeaters?limit=5000`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const data = await resp.json();
    allRepeaters = data.repeaters || data.data || data || [];
    if (!Array.isArray(allRepeaters)) allRepeaters = [];
    filteredRepeaters = [...allRepeaters];
    updateMapMarkers(allRepeaters);
    renderTable();
    showToast(`Loaded ${allRepeaters.length} repeaters`, 'success');
  } catch (err) {
    console.error('loadRepeaters error:', err);
    allRepeaters = [];
    filteredRepeaters = [];
    renderTable();
  }
}

async function loadStats() {
  try {
    const resp = await fetch(`${API_BASE}/stats`);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
    const stats = await resp.json();

    // Update hero cards
    const total = stats.total_repeaters ?? stats.total ?? allRepeaters.length;
    document.getElementById('statTotal').textContent = total.toLocaleString();
    document.getElementById('statStates').textContent = stats.states_covered ?? stats.states ?? '—';
    document.getElementById('statModes').textContent = stats.modes ?? '—';
    document.getElementById('statCategories').textContent = stats.categories ?? '—';
    document.getElementById('statActiveCount').textContent = (stats.active ?? '—') + ' active';

    // Build charts
    initCharts(stats);
  } catch (err) {
    console.error('loadStats error:', err);
    // Fallback: compute stats from repeater data
    computeStatsFromData();
  }
}

function computeStatsFromData() {
  if (!allRepeaters.length) return;

  const total = allRepeaters.length;
  const states = new Set(allRepeaters.map(r => r.state).filter(Boolean));
  const modes = new Set(allRepeaters.map(r => r.mode).filter(Boolean));
  const categories = new Set(allRepeaters.map(r => r.category).filter(Boolean));
  const active = allRepeaters.filter(r => (r.status || '').toLowerCase() === 'active').length;

  document.getElementById('statTotal').textContent = total.toLocaleString();
  document.getElementById('statStates').textContent = states.size;
  document.getElementById('statModes').textContent = modes.size;
  document.getElementById('statCategories').textContent = categories.size;
  document.getElementById('statActiveCount').textContent = active + ' active';

  // Build charts from data
  const stateCounts = {};
  const modeCounts = {};
  const bandCounts = {};

  allRepeaters.forEach(r => {
    if (r.state) stateCounts[r.state] = (stateCounts[r.state] || 0) + 1;
    if (r.mode) modeCounts[r.mode] = (modeCounts[r.mode] || 0) + 1;
    const band = getBand(r.rx_freq);
    if (band) bandCounts[band] = (bandCounts[band] || 0) + 1;
  });

  initCharts({
    by_state: stateCounts,
    by_mode: modeCounts,
    by_band: bandCounts,
  });
}

function getBand(freq) {
  if (!freq) return null;
  const f = parseFloat(freq);
  if (f >= 144 && f <= 148) return 'VHF';
  if (f >= 420 && f <= 470) return 'UHF';
  if (f >= 136 && f <= 174) return 'VHF';
  if (f >= 400 && f <= 520) return 'UHF';
  return f < 300 ? 'VHF' : 'UHF';
}

// ============================================================
//  CHARTS
// ============================================================
function initCharts(stats) {
  const chartDefaults = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#9ca3af', font: { family: 'Inter', size: 11 }, padding: 12, usePointStyle: true, pointStyleWidth: 8 },
      },
    },
  };

  // States bar chart
  const stateData = stats.by_state || {};
  const stateLabels = Object.keys(stateData).sort((a, b) => stateData[b] - stateData[a]);
  const stateValues = stateLabels.map(k => stateData[k]);

  if (charts.states) charts.states.destroy();
  charts.states = new Chart(document.getElementById('chartStates'), {
    type: 'bar',
    data: {
      labels: stateLabels.map(s => s.length > 8 ? s.slice(0, 8) + '…' : s),
      datasets: [{
        label: 'Repeaters',
        data: stateValues,
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
        borderRadius: 4,
        hoverBackgroundColor: 'rgba(59, 130, 246, 0.8)',
      }],
    },
    options: {
      ...chartDefaults,
      indexAxis: 'y',
      scales: {
        x: { ticks: { color: '#6b7280', font: { size: 10 } }, grid: { color: 'rgba(42,42,62,0.5)' } },
        y: { ticks: { color: '#9ca3af', font: { size: 10 } }, grid: { display: false } },
      },
    },
  });

  // Modes doughnut chart
  const modeData = stats.by_mode || {};
  const modeLabels = Object.keys(modeData);
  const modeValues = modeLabels.map(k => modeData[k]);
  const modeColors = modeLabels.map(m => {
    const mc = m.toUpperCase();
    if (mc.includes('DMR')) return '#10b981';
    if (mc.includes('C4FM')) return '#8b5cf6';
    if (mc.includes('D-STAR') || mc.includes('DSTAR')) return '#f59e0b';
    if (mc.includes('MIX')) return '#06b6d4';
    return '#3b82f6';
  });

  if (charts.modes) charts.modes.destroy();
  charts.modes = new Chart(document.getElementById('chartModes'), {
    type: 'doughnut',
    data: {
      labels: modeLabels,
      datasets: [{
        data: modeValues,
        backgroundColor: modeColors.map(c => c + 'cc'),
        borderColor: modeColors,
        borderWidth: 2,
        hoverBorderWidth: 3,
      }],
    },
    options: {
      ...chartDefaults,
      cutout: '65%',
      plugins: {
        ...chartDefaults.plugins,
        legend: { ...chartDefaults.plugins.legend, position: 'bottom' },
      },
    },
  });

  // Bands pie chart
  const bandData = stats.by_band || {};
  const bandLabels = Object.keys(bandData);
  const bandValues = bandLabels.map(k => bandData[k]);
  const bandColors = bandLabels.map(b => b === 'VHF' ? '#3b82f6' : b === 'UHF' ? '#10b981' : '#f59e0b');

  if (charts.bands) charts.bands.destroy();
  charts.bands = new Chart(document.getElementById('chartBands'), {
    type: 'pie',
    data: {
      labels: bandLabels,
      datasets: [{
        data: bandValues,
        backgroundColor: bandColors.map(c => c + 'cc'),
        borderColor: bandColors,
        borderWidth: 2,
      }],
    },
    options: {
      ...chartDefaults,
      plugins: {
        ...chartDefaults.plugins,
        legend: { ...chartDefaults.plugins.legend, position: 'bottom' },
      },
    },
  });
}

// ============================================================
//  SEARCH & FILTERS
// ============================================================
function setupSearch() {
  const input = document.getElementById('searchInput');
  const btn = document.getElementById('searchBtn');

  input.addEventListener('input', () => {
    clearTimeout(searchDebounceTimer);
    searchDebounceTimer = setTimeout(() => searchRepeaters(), 300);
  });

  btn.addEventListener('click', () => searchRepeaters());
  input.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') searchRepeaters();
  });

  // Filter dropdowns
  ['filterState', 'filterBand', 'filterMode', 'filterCategory'].forEach(id => {
    document.getElementById(id).addEventListener('change', () => searchRepeaters());
  });
}

function searchRepeaters() {
  const query = (document.getElementById('searchInput').value || '').toLowerCase().trim();
  const stateFilter = document.getElementById('filterState').value;
  const bandFilter = document.getElementById('filterBand').value;
  const modeFilter = document.getElementById('filterMode').value;
  const catFilter = document.getElementById('filterCategory').value;

  filteredRepeaters = allRepeaters.filter(r => {
    // Text search
    if (query) {
      const searchable = [r.name, r.callsign, r.rx_freq, r.tx_freq, r.state, r.mode, r.location]
        .filter(Boolean).join(' ').toLowerCase();
      if (!searchable.includes(query)) return false;
    }
    // State filter
    if (stateFilter && r.state !== stateFilter) return false;
    // Band filter
    if (bandFilter) {
      const band = getBand(r.rx_freq);
      if (band !== bandFilter) return false;
    }
    // Mode filter
    if (modeFilter && !(r.mode || '').toLowerCase().includes(modeFilter.toLowerCase())) return false;
    // Category filter
    if (catFilter && r.category !== catFilter) return false;

    return true;
  });

  currentPage = 1;
  renderTable();
  updateMapMarkers(filteredRepeaters);
}

async function populateFilters() {
  try {
    // Populate states
    const stateResp = await fetch(`${API_BASE}/states`);
    if (stateResp.ok) {
      const stateData = await stateResp.json();
      const states = stateData.states || stateData.data || stateData || [];
      const sel = document.getElementById('filterState');
      (Array.isArray(states) ? states : []).forEach(s => {
        const name = typeof s === 'string' ? s : s.name || s.state;
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        sel.appendChild(opt);
      });
    }
  } catch (e) {
    // Fallback: extract from data
    const states = [...new Set(allRepeaters.map(r => r.state).filter(Boolean))].sort();
    const sel = document.getElementById('filterState');
    states.forEach(s => {
      const opt = document.createElement('option');
      opt.value = s;
      opt.textContent = s;
      sel.appendChild(opt);
    });
  }

  try {
    const catResp = await fetch(`${API_BASE}/categories`);
    if (catResp.ok) {
      const catData = await catResp.json();
      const cats = catData.categories || catData.data || catData || [];
      const sel = document.getElementById('filterCategory');
      (Array.isArray(cats) ? cats : []).forEach(c => {
        const name = typeof c === 'string' ? c : c.name || c.category;
        const opt = document.createElement('option');
        opt.value = name;
        opt.textContent = name;
        sel.appendChild(opt);
      });
    }
  } catch (e) {
    const categories = [...new Set(allRepeaters.map(r => r.category).filter(Boolean))].sort();
    const sel = document.getElementById('filterCategory');
    categories.forEach(c => {
      const opt = document.createElement('option');
      opt.value = c;
      opt.textContent = c;
      sel.appendChild(opt);
    });
  }
}

// ============================================================
//  TABLE
// ============================================================
function setupTableSorting() {
  document.querySelectorAll('.th-cell[data-sort]').forEach(th => {
    th.addEventListener('click', () => {
      const col = th.dataset.sort;
      if (sortColumn === col) {
        sortDirection = sortDirection === 'asc' ? 'desc' : 'asc';
      } else {
        sortColumn = col;
        sortDirection = 'asc';
      }

      // Update UI
      document.querySelectorAll('.th-cell').forEach(el => el.classList.remove('sorted-asc', 'sorted-desc'));
      th.classList.add(sortDirection === 'asc' ? 'sorted-asc' : 'sorted-desc');

      sortAndRender();
    });
  });
}

function sortAndRender() {
  if (sortColumn) {
    filteredRepeaters.sort((a, b) => {
      let va = a[sortColumn] ?? '';
      let vb = b[sortColumn] ?? '';
      // Numeric sort for frequencies
      if (sortColumn.includes('freq')) {
        va = parseFloat(va) || 0;
        vb = parseFloat(vb) || 0;
      } else {
        va = String(va).toLowerCase();
        vb = String(vb).toLowerCase();
      }
      if (va < vb) return sortDirection === 'asc' ? -1 : 1;
      if (va > vb) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }
  currentPage = 1;
  renderTable();
}

function renderTable() {
  const tbody = document.getElementById('resultsBody');
  const total = filteredRepeaters.length;
  const totalPages = Math.max(1, Math.ceil(total / PAGE_SIZE));
  if (currentPage > totalPages) currentPage = totalPages;

  const start = (currentPage - 1) * PAGE_SIZE;
  const end = Math.min(start + PAGE_SIZE, total);
  const pageData = filteredRepeaters.slice(start, end);

  if (pageData.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-12 text-gray-500">No repeaters found</td></tr>`;
  } else {
    tbody.innerHTML = pageData.map(r => {
      const modeClass = (r.mode || 'FM').toLowerCase().replace('-', '').replace('dstar', 'dstar');
      const statusClass = (r.status || 'active').toLowerCase();
      return `
        <tr class="table-row">
          <td class="td-cell font-medium text-white">${escapeHtml(r.name || '—')}</td>
          <td class="td-cell font-mono text-accent-blue">${escapeHtml(r.callsign || '—')}</td>
          <td class="td-cell font-mono">${formatFreq(r.rx_freq)}</td>
          <td class="td-cell font-mono">${formatFreq(r.tx_freq)}</td>
          <td class="td-cell"><span class="mode-tag ${modeClass}">${escapeHtml(r.mode || '—')}</span></td>
          <td class="td-cell">${escapeHtml(r.state || '—')}</td>
          <td class="td-cell"><span class="status-dot ${statusClass === 'active' ? 'active' : statusClass === 'inactive' ? 'inactive' : 'unknown'}"></span>${escapeHtml(r.status || '—')}</td>
        </tr>
      `;
    }).join('');
  }

  // Pagination info
  document.getElementById('paginationInfo').textContent =
    total > 0 ? `Showing ${start + 1}–${end} of ${total}` : 'No results';

  // Pagination controls
  const controls = document.getElementById('paginationControls');
  let pagesHtml = '';
  if (totalPages > 1) {
    const maxVisible = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisible / 2));
    let endPage = Math.min(totalPages, startPage + maxVisible - 1);
    if (endPage - startPage < maxVisible - 1) startPage = Math.max(1, endPage - maxVisible + 1);

    if (currentPage > 1) {
      pagesHtml += `<button class="page-btn" onclick="goToPage(${currentPage - 1})">‹</button>`;
    }
    for (let i = startPage; i <= endPage; i++) {
      pagesHtml += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
    }
    if (currentPage < totalPages) {
      pagesHtml += `<button class="page-btn" onclick="goToPage(${currentPage + 1})">›</button>`;
    }
  }
  controls.innerHTML = pagesHtml;
}

function goToPage(page) {
  currentPage = page;
  renderTable();
  document.getElementById('search').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ============================================================
//  EXPORT
// ============================================================
async function exportData(format) {
  const stateFilter = document.getElementById('filterState').value;
  const bandFilter = document.getElementById('filterBand').value;
  const modeFilter = document.getElementById('filterMode').value;
  const catFilter = document.getElementById('filterCategory').value;

  let url = `${API_BASE}/export/${format}`;
  const params = new URLSearchParams();
  if (stateFilter) params.set('state', stateFilter);
  if (bandFilter) params.set('band', bandFilter);
  if (modeFilter) params.set('mode', modeFilter);
  if (catFilter) params.set('category', catFilter);

  if (params.toString()) url += '?' + params.toString();

  showToast(`Preparing ${format.toUpperCase()} export...`, 'info');

  try {
    const resp = await fetch(url);
    if (!resp.ok) throw new Error(`HTTP ${resp.status}`);

    const blob = await resp.blob();
    const ext = { chirp: 'csv', baofeng: 'csv', quansheng: 'csv', anytone: 'csv', json: 'json', csv: 'csv', yaml: 'yaml' }[format] || 'txt';
    const filename = `mrp_export_${format}_${Date.now()}.${ext}`;

    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = filename;
    a.click();
    URL.revokeObjectURL(a.href);

    showToast(`${format.toUpperCase()} exported successfully!`, 'success');
  } catch (err) {
    console.error('Export error:', err);
    showToast(`Export failed: ${err.message}`, 'error');
  }
}

// ============================================================
//  NAVIGATION
// ============================================================
function setupNavigation() {
  // Hamburger toggle
  const toggle = document.getElementById('menuToggle');
  const drawer = document.getElementById('mobileDrawer');
  const icon = document.getElementById('menuIcon');

  toggle.addEventListener('click', () => {
    drawer.classList.toggle('hidden');
    if (!drawer.classList.contains('hidden')) {
      icon.setAttribute('d', 'M6 18L18 6M6 6l12 12');
    } else {
      icon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
    }
  });

  // Close drawer on link click
  drawer.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => {
      drawer.classList.add('hidden');
      icon.setAttribute('d', 'M4 6h16M4 12h16M4 18h16');
    });
  });

  // Active nav tracking on scroll
  const sections = ['dashboard', 'map', 'search', 'charts', 'export'];
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const id = entry.target.id;
        document.querySelectorAll('.nav-link, .mobile-nav-link').forEach(el => {
          el.classList.toggle('active', el.dataset.section === id);
        });
      }
    });
  }, { threshold: 0.3, rootMargin: '-80px 0px 0px 0px' });

  sections.forEach(id => {
    const el = document.getElementById(id);
    if (el) observer.observe(el);
  });
}

// ============================================================
//  SCROLL ANIMATIONS
// ============================================================
function setupScrollAnimations() {
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const delay = entry.target.dataset.animateDelay || 0;
        setTimeout(() => {
          entry.target.classList.add('visible');
        }, parseInt(delay));
        observer.unobserve(entry.target);
      }
    });
  }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });

  document.querySelectorAll('[data-animate]').forEach(el => observer.observe(el));
}

// ============================================================
//  UTILITIES
// ============================================================
function formatFreq(freq) {
  if (!freq && freq !== 0) return '—';
  return parseFloat(freq).toFixed(4);
}

function escapeHtml(str) {
  if (!str) return '';
  const div = document.createElement('div');
  div.textContent = str;
  return div.innerHTML;
}

function showLoading() {
  document.getElementById('loadingOverlay').classList.remove('hidden');
}

function hideLoading() {
  document.getElementById('loadingOverlay').classList.add('hidden');
}

function showToast(message, type = 'info') {
  const container = document.getElementById('toastContainer');
  const toast = document.createElement('div');
  toast.className = `toast ${type}`;
  toast.textContent = message;
  container.appendChild(toast);

  setTimeout(() => {
    toast.style.animation = 'toastOut 0.3s ease-in forwards';
    setTimeout(() => toast.remove(), 300);
  }, 3500);
}
