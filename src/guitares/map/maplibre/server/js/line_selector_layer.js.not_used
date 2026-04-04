/**
 * Line selector layer — interactive lines with hover/click/selection.
 * Follows the same pattern as polygon_selector_layer.js:
 * uses direct setFeatureState for selection with 'hovered' state name.
 * @module line_selector_layer
 */

// ── Module state ─────────────────────────────────────────────────────

let hoverProperty = null;
let hoveredId = null;
let activeLayerId = null;
let selectedIndex = null;
let popup = null;
let selectedFeatures = [];

// ── Utility ──────────────────────────────────────────────────────────

/**
 * Convert a dash style string to a MapLibre line-dasharray value.
 * @param {string} lineStyle - "-" (solid), "--" (dashed), or ".." (dotted).
 * @returns {number[]} Dash array.
 */
function getLineDashArray(lineStyle) {
  if (lineStyle === '-') return [1];
  if (lineStyle === '--') return [2, 1];
  if (lineStyle === '..') return [0.5, 1];
  return [1];
}

// ── Exported functions ───────────────────────────────────────────────

/**
 * Add a line selector layer to the map.
 * @param {string} id - Layer identifier.
 * @param {Object} data - GeoJSON FeatureCollection.
 * @param {number} index - Initially selected feature index.
 * @param {string} lineColor - Default line color.
 * @param {number} lineWidth - Default line width.
 * @param {string} lineStyle - Dash style ("-", "--", "..").
 * @param {number} lineOpacity - Default line opacity.
 * @param {string} lineColorSelected - Color when selected/hovered.
 * @param {number} lineWidthSelected - Width when selected/hovered.
 * @param {string} lineStyleSelected - Dash style when selected.
 * @param {number} lineOpacitySelected - Opacity when selected.
 * @param {string} hoverParam - Property name for hover popup text.
 * @param {string} selectionOption - "single" or "multiple".
 */
export function addLayer(id, data, index,
  lineColor, lineWidth, lineStyle, lineOpacity,
  lineColorSelected, lineWidthSelected, lineStyleSelected, lineOpacitySelected,
  hoverParam, selectionOption) {

  hoverProperty = hoverParam;

  // Remove old layer and source
  if (map.getLayer(id)) map.removeLayer(id);
  if (map.getSource(id)) map.removeSource(id);

  popup = new maplibregl.Popup({
    offset: 10,
    closeButton: false,
    closeOnClick: false,
  });

  layers[id] = {
    data: data,
    mode: 'active',
    selectionOption: selectionOption,
  };

  map.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: 'index',
  });

  map.addLayer({
    id: id,
    type: 'line',
    source: id,
    layout: {
      visibility: 'visible',
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], lineColorSelected,
        ['boolean', ['feature-state', 'hovered'], false], lineColorSelected,
        lineColor,
      ],
      'line-width': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], lineWidthSelected,
        ['boolean', ['feature-state', 'hovered'], false], lineWidthSelected,
        lineWidth,
      ],
      'line-dasharray': getLineDashArray(lineStyle),
      'line-opacity': lineOpacity,
    },
  });

  // Event handlers
  map.on('mouseenter', id, mouseEnter);
  map.on('mouseleave', id, mouseLeave);

  if (selectionOption === 'single') {
    map.on('click', id, clickSingle);
  } else {
    map.on('click', id, clickMultiple);
  }

  map.once('idle', () => {
    deselectAll(id);
    layerAdded(id);
  });

  // Apply initial selection
  if (index >= 0) {
    select(id, [index]);
    selectedIndex = index;
  }
}

/**
 * Select a feature by index, deselecting all others first.
 * @param {string} id - Layer identifier.
 * @param {number} index - Feature index to select.
 */
export function setSelectedIndex(id, index) {
  deselectAll(id);
  select(id, [index]);
  selectedIndex = index;
}

/**
 * Set the layer to active mode with specified paint properties.
 */
export function activate(id,
  lineColor, lineWidth, lineStyle, lineOpacity,
  lineColorSelected, lineWidthSelected, lineStyleSelected, lineOpacitySelected) {

  layers[id].mode = 'active';
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'line-color', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], lineColorSelected,
      ['boolean', ['feature-state', 'hovered'], false], lineColorSelected,
      lineColor,
    ]);
    map.setPaintProperty(id, 'line-width', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], lineWidthSelected,
      ['boolean', ['feature-state', 'hovered'], false], lineWidthSelected,
      lineWidth,
    ]);
  }
}

/**
 * Set the layer to inactive mode with specified paint properties.
 */
export function deactivate(id,
  lineColor, lineWidth, lineStyle, lineOpacity) {

  layers[id].mode = 'inactive';
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'line-color', lineColor);
    map.setPaintProperty(id, 'line-width', lineWidth);
  }
}

/**
 * Remove the layer, source, and all event listeners.
 * @param {string} id - Layer identifier.
 */
export function remove(id) {
  var opt = layers[id] ? layers[id].selectionOption : null;
  if (map.getLayer(id)) map.removeLayer(id);
  if (map.getSource(id)) map.removeSource(id);
  map.off('mouseenter', id, mouseEnter);
  map.off('mouseleave', id, mouseLeave);
  if (opt === 'single') {
    map.off('click', id, clickSingle);
  } else {
    map.off('click', id, clickMultiple);
  }
}

// ── Internal hover handlers ──────────────────────────────────────────

function mouseEnter(e) {
  if (!e.features || e.features.length === 0) return;
  map.getCanvas().style.cursor = 'pointer';

  const feature = e.features[0];
  if (feature.properties.hover_popup_width) {
    popup.setMaxWidth(feature.properties.hover_popup_width);
  }

  if (hoverProperty && feature.properties[hoverProperty]) {
    popup.setLngLat(e.lngLat).setText(feature.properties[hoverProperty]).addTo(map);
  }

  if (hoveredId !== null) {
    map.setFeatureState(
      { source: activeLayerId, id: hoveredId },
      { hovered: false }
    );
  }

  map.setFeatureState(
    { source: feature.source, id: feature.id },
    { hovered: true }
  );
  hoveredId = feature.id;
  activeLayerId = feature.source;
}

function mouseLeave() {
  map.getCanvas().style.cursor = window.currentCursor || '';
  if (popup) popup.remove();
  if (hoveredId !== null) {
    map.setFeatureState(
      { source: activeLayerId, id: hoveredId },
      { hovered: false }
    );
  }
  hoveredId = null;
}

// ── Internal click handlers ──────────────────────────────────────────

function clickSingle(e) {
  if (!e.features || e.features.length === 0) return;
  const layerId = e.features[0].source;

  if (selectedIndex !== null) {
    deselect(layerId, [selectedIndex]);
  }
  selectedIndex = e.features[0].id;
  select(layerId, [selectedIndex]);
  featureClicked(layerId, e.features[0]);
}

function clickMultiple(e) {
  if (!e.features || e.features.length === 0) return;
  const layerId = e.features[0].source;
  const index = e.features[0].id;
  const state = map.getFeatureState({ source: layerId, id: index });

  if (state.selected) {
    deselect(layerId, [index]);
  } else {
    select(layerId, [index]);
  }

  selectedFeatures = [];
  for (let i = 0; i < layers[layerId].data.features.length; i++) {
    const fs = map.getFeatureState({ source: layerId, id: i });
    if (fs.selected) {
      selectedFeatures.push(layers[layerId].data.features[i]);
    }
  }
  featureClicked(layerId, selectedFeatures);
}

// ── Internal selection helpers ───────────────────────────────────────

function select(layerId, indices) {
  for (const idx of indices) {
    map.setFeatureState({ source: layerId, id: idx }, { selected: true });
  }
}

function deselect(layerId, indices) {
  for (const idx of indices) {
    map.setFeatureState({ source: layerId, id: idx }, { selected: false });
  }
}

function deselectAll(layerId) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (let i = 0; i < features.length; i++) {
    map.setFeatureState({ source: layerId, id: i }, { selected: false });
  }
}
