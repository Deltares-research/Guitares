/**
 * MapLibre GL Terrain Control
 *
 * Toggleable 3D terrain with exaggeration control.
 * Terrain sources are configured via ``window.terrainSources`` (set in
 * defaults.js by Python).  Falls back to AWS Terrain Tiles if no
 * sources are configured.
 *
 * Usage from Python:
 *   map.runjs("/js/terrain_control.js", "setTerrainSource", source="gebco_2024")
 *   map.runjs("/js/terrain_control.js", "setExaggeration", exaggeration=2.0)
 */

// ── Module state ────────────────────────────────────────────────────

let terrainActive = false;
let currentSourceId = null;
let currentExaggeration = 1.5;
let terrainMap = null;
let terrainButton = null;
let exaggerationSlider = null;
let sourceSelect = null;
let sliderContainer = null;

// ── Default terrain source ──────────────────────────────────────────

const DEFAULT_SOURCE = {
  id: "aws-terrain",
  name: "AWS Terrain",
  tiles: ["https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"],
  encoding: "terrarium",
  tileSize: 256,
  maxzoom: 15,
};

/**
 * Get the list of available terrain sources.
 * Merges user-configured sources (from defaults.js) with the default.
 */
function getTerrainSources() {
  var sources = [];

  // Add AWS default
  sources.push(DEFAULT_SOURCE);

  // Add user-configured sources from Python
  if (window.terrainSources && Array.isArray(window.terrainSources)) {
    for (var src of window.terrainSources) {
      sources.push(src);
    }
  }

  return sources;
}

// ── Control class ───────────────────────────────────────────────────

/**
 * A MapLibre GL control that toggles 3D terrain rendering.
 * Shows a mountain icon button. When active, adds an exaggeration
 * slider below the button.
 */
export class TerrainControl {
  constructor() {
    this._active = false;
  }

  /**
   * Called by MapLibre when the control is added to the map.
   * @param {Object} map - The MapLibre map instance.
   * @returns {HTMLElement} The control container element.
   */
  onAdd(map) {
    terrainMap = map;

    this._container = document.createElement("div");
    this._container.className = "maplibregl-ctrl maplibregl-ctrl-group";

    // Toggle button with mountain icon
    const button = document.createElement("button");
    button.type = "button";
    button.title = "Toggle 3D terrain";
    button.setAttribute("aria-label", "Toggle 3D terrain");
    button.innerHTML = `<svg viewBox="0 0 24 24" width="22" height="22" style="fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;">
      <path d="M2 20 L8 8 L12 14 L16 6 L22 20 Z"/>
    </svg>`;
    button.addEventListener("click", () => this._toggle());
    terrainButton = button;
    this._container.appendChild(button);

    // Exaggeration panel (hidden initially)
    sliderContainer = document.createElement("div");
    sliderContainer.style.display = "none";
    sliderContainer.style.padding = "4px 6px";
    sliderContainer.style.background = "#fff";
    sliderContainer.style.borderTop = "1px solid #ccc";
    sliderContainer.style.width = "30px";

    exaggerationSlider = document.createElement("input");
    exaggerationSlider.type = "range";
    exaggerationSlider.min = "0.5";
    exaggerationSlider.max = "5";
    exaggerationSlider.step = "0.5";
    exaggerationSlider.value = String(currentExaggeration);
    exaggerationSlider.style.width = "100%";
    exaggerationSlider.style.writingMode = "vertical-lr";
    exaggerationSlider.style.direction = "rtl";
    exaggerationSlider.style.height = "80px";
    exaggerationSlider.title = "Vertical exaggeration: " + currentExaggeration + "x";
    exaggerationSlider.addEventListener("input", (e) => {
      currentExaggeration = parseFloat(e.target.value);
      exaggerationSlider.title = "Vertical exaggeration: " + currentExaggeration + "x";
      if (terrainActive) {
        terrainMap.setTerrain({
          source: currentSourceId,
          exaggeration: currentExaggeration,
        });
      }
    });

    sliderContainer.appendChild(exaggerationSlider);
    this._container.appendChild(sliderContainer);

    // Add DEM source and sky layer once map is loaded
    map.on("load", () => {
      _ensureSourceAndSky(map);
    });

    // If map is already loaded
    if (map.loaded()) {
      _ensureSourceAndSky(map);
    }

    return this._container;
  }

  onRemove() {
    if (terrainActive) {
      terrainMap.setTerrain(null);
    }
    this._container.parentNode.removeChild(this._container);
    terrainMap = null;
  }

  _toggle() {
    if (terrainActive) {
      _disableTerrain();
    } else {
      _enableTerrain();
    }
  }
}

// ── Internal helpers ────────────────────────────────────────────────

function _ensureSourceAndSky(map) {
  // Add the default terrain source if not already present
  var sources = getTerrainSources();
  for (var src of sources) {
    if (!map.getSource(src.id)) {
      map.addSource(src.id, {
        type: "raster-dem",
        tiles: src.tiles,
        tileSize: src.tileSize || 256,
        maxzoom: src.maxzoom || 15,
        encoding: src.encoding || "terrarium",
      });
    }
  }

  // Set current source to the first one
  if (!currentSourceId) {
    currentSourceId = sources[0].id;
  }

  // MapLibre uses style-level sky config (not a layer type like Mapbox)
}

function _enableTerrain() {
  if (!terrainMap || !currentSourceId) return;

  terrainMap.setTerrain({
    source: currentSourceId,
    exaggeration: currentExaggeration,
  });

  // Enable sky atmosphere
  if (typeof terrainMap.setSky === 'function') {
    terrainMap.setSky({
      "sky-color": "#88C6FC",
      "sky-horizon-blend": 0.3,
      "horizon-color": "#f0f0f0",
      "horizon-fog-blend": 0.8,
      "fog-color": "#cccccc",
      "fog-ground-blend": 0.5,
      "atmosphere-blend": ["interpolate", ["linear"], ["zoom"], 0, 1, 12, 0],
    });
  }

  terrainActive = true;
  terrainButton.classList.add("active");
  sliderContainer.style.display = "block";
}

function _disableTerrain() {
  if (!terrainMap) return;

  terrainMap.setTerrain(null);

  // Disable sky
  if (typeof terrainMap.setSky === 'function') {
    terrainMap.setSky({});
  }

  terrainActive = false;
  terrainButton.classList.remove("active");
  sliderContainer.style.display = "none";
}

// ── Public API (callable from Python via runjs) ─────────────────────

/**
 * Switch to a different terrain DEM source.
 * @param {object} options
 * @param {string} options.source - Source ID (must be in terrainSources or "aws-terrain").
 */
export function setTerrainSource({ source = "aws-terrain" } = {}) {
  var sources = getTerrainSources();
  var found = sources.find((s) => s.id === source);
  if (!found) {
    console.warn("Terrain source not found: " + source);
    return;
  }

  // Add source if not yet on map
  if (terrainMap && !terrainMap.getSource(found.id)) {
    terrainMap.addSource(found.id, {
      type: "raster-dem",
      tiles: found.tiles,
      tileSize: found.tileSize || 256,
      maxzoom: found.maxzoom || 15,
      encoding: found.encoding || "terrarium",
    });
  }

  currentSourceId = found.id;

  // Sync dropdown
  if (sourceSelect) {
    sourceSelect.value = found.id;
  }

  // Update active terrain if enabled
  if (terrainActive && terrainMap) {
    terrainMap.setTerrain({
      source: currentSourceId,
      exaggeration: currentExaggeration,
    });
  }
}

/**
 * Set the vertical exaggeration factor.
 * @param {object} options
 * @param {number} options.exaggeration - Exaggeration factor (default 1.5).
 */
export function setExaggeration({ exaggeration = 1.5 } = {}) {
  currentExaggeration = exaggeration;
  if (exaggerationSlider) {
    exaggerationSlider.value = String(exaggeration);
    exaggerationSlider.title = "Vertical exaggeration: " + exaggeration + "x";
  }
  if (terrainActive && terrainMap) {
    terrainMap.setTerrain({
      source: currentSourceId,
      exaggeration: currentExaggeration,
    });
  }
}

/**
 * Enable or disable terrain from Python.
 * @param {object} options
 * @param {boolean} options.enabled - True to enable, false to disable.
 */
export function setTerrain({ enabled = true } = {}) {
  if (enabled) {
    _enableTerrain();
  } else {
    _disableTerrain();
  }
}
