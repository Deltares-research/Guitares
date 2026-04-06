/**
 * Circle layer with optional selection and hover popups.
 *
 * When selector mode is enabled (options.selector=true), the layer
 * supports hover popups, single/multiple click selection, and
 * feature state management (hovered, selected).
 *
 * Also supports custom paint dicts (options.paintDict) for
 * data-driven styling (choropleth-style circles).
 *
 * @module circle_layer
 */

import { findBeforeId } from './utils.js';

// ── Module state (for selector mode) ─────────────────────────────────

let hoverProperty = null;
let hoveredId = null;
let activeLayerId = null;
let selectedIndex = null;
let popup = null;
let selectedFeatures = [];

// ── Main entry point ─────────────────────────────────────────────────

/**
 * Add a circle layer to the map.
 *
 * @param {string} id - Layer/source identifier.
 * @param {Object} data - GeoJSON FeatureCollection.
 * @param {Object} pp - Paint properties dict:
 *   lineColor, lineWidth, lineOpacity, fillColor, fillOpacity, circleRadius.
 *   For selector mode also: lineColorSelected, fillColorSelected, circleRadiusSelected.
 * @param {Object} [options] - Additional options:
 *   selector (bool), index (int), hoverProperty (string), unit (string),
 *   selectionOption ("single"|"multiple"), minZoom (number),
 *   paintDict (object - custom MapLibre paint), legendItems (array),
 *   legendTitle (string), legendPosition (string).
 */
export function addLayer(id, data, pp, options) {
  const opts = options || {};
  const selector = opts.selector || false;
  const minZoom = opts.minZoom || 0;

  // Clean up
  if (map.getLayer(id)) map.removeLayer(id);
  if (map.getSource(id)) map.removeSource(id);
  const legend = document.getElementById('legend' + id);
  if (legend) legend.remove();

  const sourceConfig = { type: 'geojson', data: data };
  if (selector) sourceConfig.promoteId = 'index';

  map.addSource(id, sourceConfig);

  // ── Circle layer paint ─────────────────────────────────────────

  let paint;

  if (opts.paintDict) {
    // Custom paint dict (for data-driven coloring)
    paint = opts.paintDict;
  } else if (selector) {
    // Selector mode: feature-state-driven styling
    paint = {
      'circle-stroke-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.lineColorSelected || pp.lineColor,
        ['boolean', ['feature-state', 'hovered'], false], pp.lineColorSelected || pp.lineColor,
        pp.lineColor,
      ],
      'circle-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.fillColorSelected || pp.fillColor,
        ['boolean', ['feature-state', 'hovered'], false], pp.fillColorSelected || pp.fillColor,
        pp.fillColor,
      ],
      'circle-stroke-width': pp.lineWidth,
      'circle-radius': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], pp.circleRadiusSelected || pp.circleRadius,
        ['boolean', ['feature-state', 'hovered'], false], pp.circleRadiusSelected || pp.circleRadius,
        pp.circleRadius,
      ],
      'circle-opacity': pp.fillOpacity,
    };
  } else {
    // Simple static paint
    paint = {
      'circle-color': pp.fillColor,
      'circle-stroke-width': pp.lineWidth,
      'circle-stroke-color': pp.lineColor,
      'circle-stroke-opacity': pp.lineOpacity,
      'circle-radius': pp.circleRadius,
      'circle-opacity': pp.fillOpacity,
    };
  }

  map.addLayer({
    id: id,
    type: 'circle',
    source: id,
    minzoom: minZoom,
    layout: { visibility: 'visible' },
    paint: paint,
  }, findBeforeId(map, opts.beforeIds) || 'dummy_layer_1');

  // ── Hover popup (non-selector simple mode) ─────────────────────

  if (!selector && opts.hoverProperty) {
    const hoverPopup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
    });
    const unit = opts.unit || '';

    map.on('mouseenter', id, function(e) {
      map.getCanvas().style.cursor = 'pointer';
      const val = e.features[0].properties[opts.hoverProperty];
      let text = opts.hoverProperty + ': ' + val;
      if (unit) text += ' ' + unit;
      hoverPopup.setLngLat(e.lngLat).setText(text).addTo(map);
    });

    map.on('mouseleave', id, function() {
      map.getCanvas().style.cursor = window.currentCursor || '';
      hoverPopup.remove();
    });
  }

  // ── Legend (optional, for custom paint mode) ───────────────────

  if (opts.legendItems && opts.legendItems.length > 0) {
    const legendDiv = document.createElement('div');
    legendDiv.id = 'legend' + id;
    legendDiv.className = 'legend ' + (opts.legendPosition || 'bottom-right');
    if (opts.legendTitle) {
      const t = document.createElement('div');
      t.innerHTML = '<strong>' + opts.legendTitle + '</strong>';
      legendDiv.appendChild(t);
    }
    for (let i = 0; i < opts.legendItems.length; i++) {
      const item = document.createElement('div');
      item.innerHTML =
        '<i style="' + opts.legendItems[i].style + '; width:18px; height:18px; display:inline-block; margin-right:5px;"></i>' +
        '<span>' + opts.legendItems[i].label + '</span>';
      legendDiv.appendChild(item);
    }
    document.body.appendChild(legendDiv);
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

    const index = opts.index || 0;
    if (index >= 0) {
      select(id, [index]);
      selectedIndex = index;
    }
  }
}

// ── Paint property updates ───────────────────────────────────────────

/**
 * Update paint properties for an existing circle layer.
 * @param {string} id - Layer identifier.
 * @param {Object} pp - Paint properties dict.
 */
export function setPaintProperties(id, pp) {
  if (!map.getLayer(id)) return;
  map.setPaintProperty(id, 'circle-stroke-color', pp.lineColor);
  map.setPaintProperty(id, 'circle-stroke-width', pp.lineWidth);
  map.setPaintProperty(id, 'circle-stroke-opacity', pp.lineOpacity);
  map.setPaintProperty(id, 'circle-color', pp.fillColor);
  map.setPaintProperty(id, 'circle-opacity', pp.fillOpacity);
  map.setPaintProperty(id, 'circle-radius', pp.circleRadius);
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
export function selectByIndex(id, index) {
  deselectAll(id);
  select(id, [index]);
  selectedIndex = index;
}

/**
 * Set the layer to active mode.
 * @param {string} id - Layer identifier.
 * @param {Object} pp - Active paint properties.
 */
export function activate(id, pp) {
  if (layers[id]) layers[id].mode = 'active';
  setPaintProperties(id, pp);
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
 * Remove the layer, source, legend, and event listeners.
 * @param {string} id - Layer identifier.
 */
export function remove(id) {
  const opt = layers[id] ? layers[id].selectionOption : null;
  if (map.getLayer(id)) map.removeLayer(id);
  if (map.getSource(id)) map.removeSource(id);
  const legend = document.getElementById('legend' + id);
  if (legend) legend.remove();
  map.off('mouseenter', id, mouseEnter);
  map.off('mouseleave', id, mouseLeave);
  if (opt === 'single') {
    map.off('click', id, clickSingle);
  } else {
    map.off('click', id, clickMultiple);
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
    const coords = feature.geometry.coordinates.slice();
    while (Math.abs(e.lngLat.lng - coords[0]) > 180) {
      coords[0] += e.lngLat.lng > coords[0] ? 360 : -360;
    }
    popup.setLngLat(coords).setText(feature.properties[hoverProperty]).addTo(map);
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
  if (selectedIndex !== null) deselect(layerId, [selectedIndex]);
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
    if (fs.selected) selectedFeatures.push(layers[layerId].data.features[i]);
  }
  featureClicked(layerId, selectedFeatures);
}

// ── Selector: selection helpers ──────────────────────────────────────

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
