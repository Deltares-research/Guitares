/**
 * Line layer with optional circle vertices and optional selection.
 *
 * When selector mode is enabled (options.selector=true), the layer
 * supports hover popups, single/multiple click selection, and
 * feature state management (hovered, selected).
 *
 * @module line_layer
 */

import { findBeforeId, getDashArray } from './utils.js';

// ── Module state (for selector mode) ─────────────────────────────────

let hoverProperty = null;
let hoveredId = null;
let activeLayerId = null;
let selectedIndex = null;
let popup = null;
let selectedFeatures = [];

// ── Main entry point ─────────────────────────────────────────────────

/**
 * Add a line layer to the map.
 *
 * @param {string} id - Layer/source identifier.
 * @param {Object} data - GeoJSON FeatureCollection.
 * @param {Object} pp - Paint properties dict:
 *   lineColor, lineWidth, lineOpacity, lineStyle,
 *   fillColor, fillOpacity, circleRadius,
 *   lineColorSelected, lineWidthSelected (for selector mode).
 * @param {Object} [options] - Additional options:
 *   selector (bool), index (int), hoverProperty (string),
 *   selectionOption ("single"|"multiple").
 */
export function addLayer(id, data, pp, options) {
  const opts = options || {};
  const selector = opts.selector || false;
  const lineId = id + '.line';
  const circleId = id + '.circle';

  // Clean up
  if (map.getLayer(lineId)) map.removeLayer(lineId);
  if (map.getLayer(circleId)) map.removeLayer(circleId);
  if (map.getSource(id)) map.removeSource(id);

  const sourceConfig = { type: 'geojson', data: data };

  map.addSource(id, sourceConfig);

  // ── Line sub-layer ─────────────────────────────────────────────

  const linePaint = {
    'line-color': pp.lineColor,
    'line-width': pp.lineWidth,
    'line-opacity': pp.lineOpacity,
  };

  if (selector && pp.lineColorSelected) {
    linePaint['line-color'] = [
      'case',
      ['boolean', ['get', '_selected'], false], pp.lineColorSelected,
      pp.lineColor,
    ];
    linePaint['line-width'] = [
      'case',
      ['boolean', ['get', '_selected'], false], pp.lineWidthSelected || pp.lineWidth,
      pp.lineWidth,
    ];
  }

  if (pp.lineStyle) {
    linePaint['line-dasharray'] = getDashArray(pp.lineStyle);
  }

  const beforeId = findBeforeId(map, opts.beforeIds) || 'dummy_layer_1';

  map.addLayer({
    id: lineId,
    type: 'line',
    source: id,
    layout: { visibility: 'visible', 'line-cap': 'round', 'line-join': 'round' },
    paint: linePaint,
  }, beforeId);

  // ── Circle sub-layer (optional) ────────────────────────────────

  const circleRadius = pp.circleRadius || 0;
  if (circleRadius > 0) {
    map.addLayer({
      id: circleId,
      type: 'circle',
      source: id,
      paint: {
        'circle-color': pp.fillColor || pp.lineColor,
        'circle-stroke-width': pp.lineWidth,
        'circle-stroke-color': pp.lineColor,
        'circle-stroke-opacity': pp.lineOpacity,
        'circle-radius': circleRadius,
        'circle-opacity': pp.fillOpacity || 1,
      },
    }, beforeId);
  }

  // ── Selector mode setup ────────────────────────────────────────

  if (selector) {
    hoverProperty = opts.hoverProperty || null;
    const selectionOption = opts.selectionOption || 'single';

    layers[id] = {
      data: data,
      mode: 'active',
      selectionOption: selectionOption,
    };

    popup = new maplibregl.Popup({
      offset: 10,
      closeButton: false,
      closeOnClick: false,
    });

    map.on('mouseenter', lineId, mouseEnter);
    map.on('mouseleave', lineId, mouseLeave);

    if (selectionOption === 'single') {
      map.on('click', lineId, clickSingle);
    } else {
      map.on('click', lineId, clickMultiple);
    }

    map.once('idle', () => {
      layerAdded(id);
    });

    if (opts.index !== undefined && opts.index >= 0) {
      selectedIndex = opts.index;
      select(id, [selectedIndex]);
    }
  }
}

// ── Paint property updates ───────────────────────────────────────────

/**
 * Update paint properties for an existing line (and circle) layer.
 * @param {string} id - Base layer identifier.
 * @param {Object} pp - Paint properties dict.
 */
export function setPaintProperties(id, pp) {
  if (map.getLayer(id + '.line')) {
    map.setPaintProperty(id + '.line', 'line-color', pp.lineColor);
    map.setPaintProperty(id + '.line', 'line-width', pp.lineWidth);
  }
  if (map.getLayer(id + '.circle')) {
    map.setPaintProperty(id + '.circle', 'circle-stroke-color', pp.lineColor);
    map.setPaintProperty(id + '.circle', 'circle-stroke-width', pp.lineWidth);
    map.setPaintProperty(id + '.circle', 'circle-stroke-opacity', pp.lineOpacity);
    map.setPaintProperty(id + '.circle', 'circle-color', pp.fillColor || pp.lineColor);
    map.setPaintProperty(id + '.circle', 'circle-opacity', pp.fillOpacity || 1);
    map.setPaintProperty(id + '.circle', 'circle-radius', pp.circleRadius || 0);
  }
}

/**
 * Update the GeoJSON data for an existing source.
 * @param {string} id - Layer/source identifier.
 * @param {Object} data - New GeoJSON data.
 */
export function setData(id, data) {
  const source = map.getSource(id);
  if (source) source.setData(data);
}

// ── Selector: selection ──────────────────────────────────────────────

/**
 * Select a feature by index, deselecting all others.
 * @param {string} id - Layer identifier.
 * @param {number} index - Feature index to select.
 */
export function setSelectedIndex(id, index) {
  deselectAll(id);
  selectedIndex = index;
  select(id, [index]);
}

/**
 * Set the layer to active mode.
 * @param {string} id - Layer identifier.
 * @param {Object} pp - Active paint properties.
 */
export function activate(id, pp) {
  if (layers[id]) layers[id].mode = 'active';
  if (layers[id]?.selectionOption && pp.lineColorSelected) {
    map.setPaintProperty(id + '.line', 'line-color', [
      'case',
      ['boolean', ['get', '_selected'], false], pp.lineColorSelected,
      pp.lineColor,
    ]);
    map.setPaintProperty(id + '.line', 'line-width', [
      'case',
      ['boolean', ['get', '_selected'], false], pp.lineWidthSelected || pp.lineWidth,
      pp.lineWidth,
    ]);
  } else {
    setPaintProperties(id, pp);
  }
}

/**
 * Set the layer to inactive mode.
 * @param {string} id - Layer identifier.
 * @param {Object} pp - Inactive paint properties.
 */
export function deactivate(id, pp) {
  if (layers[id]) layers[id].mode = 'inactive';
  setPaintProperties(id, pp);
}

/**
 * Remove the layer, source, and event listeners.
 * @param {string} id - Layer identifier.
 */
export function remove(id) {
  const opt = layers[id] ? layers[id].selectionOption : null;
  if (map.getLayer(id + '.line')) map.removeLayer(id + '.line');
  if (map.getLayer(id + '.circle')) map.removeLayer(id + '.circle');
  if (map.getSource(id)) map.removeSource(id);
  map.off('mouseenter', id + '.line', mouseEnter);
  map.off('mouseleave', id + '.line', mouseLeave);
  if (opt === 'single') {
    map.off('click', id + '.line', clickSingle);
  } else {
    map.off('click', id + '.line', clickMultiple);
  }
}

// ── Selector: hover handlers ─────────────────────────────────────────

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
    map.setFeatureState({ source: activeLayerId, id: hoveredId }, { hovered: false });
  }
  map.setFeatureState({ source: feature.source, id: feature.id }, { hovered: true });
  hoveredId = feature.id;
  activeLayerId = feature.source;
}

function mouseLeave() {
  map.getCanvas().style.cursor = window.currentCursor || '';
  if (popup) popup.remove();
  if (hoveredId !== null) {
    map.setFeatureState({ source: activeLayerId, id: hoveredId }, { hovered: false });
  }
  hoveredId = null;
}

// ── Selector: click handlers ─────────────────────────────────────────

function clickSingle(e) {
  if (!e.features || e.features.length === 0) return;
  const layerId = e.features[0].source;
  const clickedIndex = e.features[0].properties.index;
  deselectAll(layerId);
  selectedIndex = clickedIndex;
  select(layerId, [clickedIndex]);
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
    if (fs.selected) selectedFeatures.push(layers[layerId].data.features[i]);
  }
  featureClicked(layerId, selectedFeatures);
}

// ── Selector: selection helpers ──────────────────────────────────────

function select(layerId, indices) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (const idx of indices) {
    const f = features.find(f => f.properties.index === idx);
    if (f) f.properties._selected = true;
  }
  const src = map.getSource(layerId);
  if (src && layers[layerId]?.data) src.setData(layers[layerId].data);
}

function deselect(layerId, indices) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (const idx of indices) {
    const f = features.find(f => f.properties.index === idx);
    if (f) f.properties._selected = false;
  }
  const src = map.getSource(layerId);
  if (src && layers[layerId]?.data) src.setData(layers[layerId].data);
}

function deselectAll(layerId) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (let i = 0; i < features.length; i++) {
    features[i].properties._selected = false;
  }
}
