/**
 * Polygon selector layer — interactive polygons with hover/click/selection.
 * Uses fill + line sub-layers. Hover state uses 'hovered' (not 'hover')
 * because polygons use mousemove rather than mouseenter for detection.
 *
 * Note: this layer uses direct setFeatureState calls rather than the
 * data-array pattern from selectable_layer_base, because polygon
 * selection works with index arrays rather than single indices.
 *
 * @module polygon_selector_layer
 */

import {
  initPopup,
  removeLayerAndSource,
} from './selectable_layer_base.js';

// ── Module state ─────────────────────────────────────────────────────

let hoverProperty = null;
let hoveredId = null;
let activeLayerId = null;
let selectedIndex = null;
let popup = null;
let selectedFeatures = [];

// ── Exported functions ───────────────────────────────────────────────

/**
 * Add a polygon selector layer to the map (fill + line sub-layers).
 * @param {string} id - Layer identifier.
 * @param {Object} data - GeoJSON FeatureCollection.
 * @param {number[]} index - Initially selected feature indices.
 * @param {string} hovprop - Property name for hover popup text.
 * @param {Object} pp - Paint properties for normal/selected/hover states.
 * @param {string} selectionOption - "single" or "multiple".
 */
export function addLayer(id, data, index, hovprop, pp, selectionOption) {
  hoverProperty = hovprop;

  const fillId = id + '.fill';
  const lineId = id + '.line';

  // Remove old layers and source
  removeLayerAndSource(id, ['.fill', '.line']);

  // Popup
  popup = new maplibregl.Popup({
    offset: 10,
    closeButton: false,
    closeOnClick: false,
  });

  // Store layer state
  layers[id] = {
    data: data,
    mode: 'active',
    selectionOption: selectionOption,
  };

  // Add source with promoted feature id
  map.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: 'index',
  });

  // Add line sub-layer
  map.addLayer({
    id: lineId,
    type: 'line',
    source: id,
    layout: { visibility: 'visible' },
    paint: {
      'line-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.lineColorSelected,
        pp.lineColor,
      ],
      'line-opacity': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.lineOpacitySelected,
        pp.lineOpacity,
      ],
      'line-width': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.lineWidthSelected,
        ['boolean', ['feature-state', 'hovered'], false], pp.lineWidthHover,
        pp.lineWidth,
      ],
    },
  });

  // Add fill sub-layer
  map.addLayer({
    id: fillId,
    type: 'fill',
    source: id,
    layout: { visibility: 'visible' },
    paint: {
      'fill-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.fillColorSelected,
        ['boolean', ['feature-state', 'hovered'], false], pp.fillColorHover,
        pp.fillColor,
      ],
      'fill-opacity': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.fillOpacitySelected,
        ['boolean', ['feature-state', 'hovered'], false], pp.fillOpacityHover,
        pp.fillOpacity,
      ],
      'fill-outline-color': 'transparent',
    },
  });

  // Event handlers — polygon uses mousemove on fill layer
  map.on('mousemove', fillId, mouseEnter);
  map.on('mouseleave', fillId, mouseLeave);

  if (selectionOption === 'single') {
    map.off('click', fillId, clickSingle);
    map.on('click', fillId, clickSingle);
  } else {
    map.off('click', fillId, clickMultiple);
    map.on('click', fillId, clickMultiple);
  }

  map.once('idle', () => {
    deselectAll(id);
    layerAdded(id);
  });

  // Apply initial selection
  if (index.length > 0) {
    select(id, index);
  }
}

/**
 * Select features by index, deselecting all others first.
 * @param {string} layerId - Layer identifier.
 * @param {number[]} indices - Feature indices to select.
 */
export function selectByIndex(layerId, indices) {
  deselectAll(layerId);
  select(layerId, indices);
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

  // Clear previous hover
  if (hoveredId !== null) {
    map.setFeatureState(
      { source: activeLayerId, id: hoveredId },
      { hovered: false }
    );
  }

  // Set new hover
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

  // Rebuild selected features list
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
