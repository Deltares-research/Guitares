/**
 * Circle selector layer — interactive circles with hover/click/selection.
 * Follows the same pattern as polygon_selector_layer.js:
 * uses direct setFeatureState for selection with 'hovered' state name.
 * @module circle_selector_layer
 */

// ── Module state ─────────────────────────────────────────────────────

let hoverProperty = null;
let hoveredId = null;
let activeLayerId = null;
let selectedIndex = null;
let popup = null;
let selectedFeatures = [];

// ── Exported functions ───────────────────────────────────────────────

/**
 * Add a circle selector layer to the map.
 * @param {string} id - Layer identifier.
 * @param {Object} data - GeoJSON FeatureCollection.
 * @param {number} index - Initially selected feature index.
 * @param {string} hovprop - Property name for hover popup text.
 * @param {string} lineColor - Default stroke color.
 * @param {number} lineWidth - Stroke width.
 * @param {string} lineStyle - Dash style (unused for circles).
 * @param {number} lineOpacity - Stroke opacity.
 * @param {string} fillColor - Default fill color.
 * @param {number} fillOpacity - Fill opacity.
 * @param {number} circleRadius - Default radius in pixels.
 * @param {string} lineColorActive - Stroke color when selected/hovered.
 * @param {string} fillColorActive - Fill color when selected/hovered.
 * @param {number} circleRadiusActive - Radius when selected/hovered.
 * @param {string} selectionOption - "single" or "multiple".
 */
export function addLayer(id, data, index, hovprop,
  lineColor, lineWidth, lineStyle, lineOpacity,
  fillColor, fillOpacity, circleRadius,
  lineColorActive, fillColorActive, circleRadiusActive,
  selectionOption) {

  hoverProperty = hovprop;

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
    type: 'circle',
    source: id,
    layout: { visibility: 'visible' },
    paint: {
      'circle-stroke-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], lineColorActive,
        ['boolean', ['feature-state', 'hovered'], false], lineColorActive,
        lineColor,
      ],
      'circle-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], fillColorActive,
        ['boolean', ['feature-state', 'hovered'], false], fillColorActive,
        fillColor,
      ],
      'circle-stroke-width': lineWidth,
      'circle-radius': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], circleRadiusActive,
        ['boolean', ['feature-state', 'hovered'], false], circleRadiusActive,
        circleRadius,
      ],
      'circle-opacity': fillOpacity,
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
 * @param {string} layerId - Layer identifier.
 * @param {number} index - Feature index to select.
 */
export function selectByIndex(layerId, index) {
  deselectAll(layerId);
  select(layerId, [index]);
  selectedIndex = index;
}

/**
 * Set the layer to active mode with specified paint properties.
 */
export function activate(id,
  lineColor, lineWidth, lineStyle, lineOpacity,
  fillColor, fillOpacity, circleRadius,
  lineColorSelected, fillColorSelected, circleRadiusSelected) {

  layers[id].mode = 'active';
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], lineColorSelected,
      ['boolean', ['feature-state', 'hovered'], false], lineColorSelected,
      lineColor,
    ]);
    map.setPaintProperty(id, 'circle-color', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], fillColorSelected,
      ['boolean', ['feature-state', 'hovered'], false], fillColorSelected,
      fillColor,
    ]);
    map.setPaintProperty(id, 'circle-radius', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], circleRadiusSelected,
      ['boolean', ['feature-state', 'hovered'], false], circleRadiusSelected,
      circleRadius,
    ]);
  }
}

/**
 * Set the layer to inactive mode with specified paint properties.
 */
export function deactivate(id,
  lineColor, lineWidth, lineStyle, lineOpacity,
  fillColor, fillOpacity, circleRadius,
  lineColorSelected, fillColorSelected, circleRadiusSelected) {

  layers[id].mode = 'inactive';
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], lineColorSelected,
      ['boolean', ['feature-state', 'hovered'], false], lineColorSelected,
      lineColor,
    ]);
    map.setPaintProperty(id, 'circle-color', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], fillColorSelected,
      ['boolean', ['feature-state', 'hovered'], false], fillColorSelected,
      fillColor,
    ]);
    map.setPaintProperty(id, 'circle-radius', [
      'case',
      ['boolean', ['feature-state', 'selected'], false], circleRadiusSelected,
      ['boolean', ['feature-state', 'hovered'], false], circleRadiusSelected,
      circleRadius,
    ]);
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
    const coords = feature.geometry.coordinates.slice();
    while (Math.abs(e.lngLat.lng - coords[0]) > 180) {
      coords[0] += e.lngLat.lng > coords[0] ? 360 : -360;
    }
    popup.setLngLat(coords).setText(feature.properties[hoverProperty]).addTo(map);
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
