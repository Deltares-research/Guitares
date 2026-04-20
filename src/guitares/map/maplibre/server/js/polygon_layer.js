/**
 * Unified polygon layer for MapLibre GL.
 *
 * Handles simple outlines, filled polygons, choropleths, custom paint
 * expressions, and interactive selection. Consistent API with
 * line_layer.js and circle_layer.js: addLayer(id, data, pp, options).
 *
 * @module polygon_layer
 */

import { getMap, findBeforeId, getDashArray, cleanUp } from './utils.js';

// ── Module state (for selector mode) ─────────────────────────────────

let hoverProperty = null;
let hoveredId = null;
let activeLayerId = null;
let selectedIndex = null;
let popup = null;
let selectedFeatures = [];

// ── Helpers ──────────────────────────────────────────────────────────

function numberWithCommas(x) {
  if (x === null || x === undefined) return '';
  return x.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ',');
}

// ── Main entry point ─────────────────────────────────────────────────

/**
 * Add a polygon layer to the map.
 *
 * @param {string} id - Layer identifier.
 * @param {Object} data - GeoJSON FeatureCollection.
 * @param {Object} pp - Paint properties from get_paint_props():
 *   lineColor, lineWidth, lineOpacity, fillColor, fillOpacity, circleRadius.
 * @param {Object} [options] - Behaviour and extra rendering options:
 *   lineStyle, minZoom, side,
 *   paintDict, colorProperty, bins, colors, colorLabels,
 *   hoverProperty, unit,
 *   legendTitle, legendPosition, legendItems,
 *   selector (bool), index (int/array), selectionOption,
 *   lineColorSelected, lineWidthSelected, lineOpacitySelected,
 *   fillColorSelected, fillOpacitySelected,
 *   lineWidthHover, fillColorHover, fillOpacityHover.
 */
export function addLayer(id, data, pp, options) {
  const opts = options || {};
  const mp = getMap(opts.side);
  const selector = opts.selector || false;

  cleanUp(mp, id);

  const lineColor   = pp.lineColor || 'black';
  const lineWidth   = pp.lineWidth !== undefined ? pp.lineWidth : 1;
  const lineOpacity = pp.lineOpacity !== undefined ? pp.lineOpacity : 1;
  const lineStyle   = pp.lineStyle || opts.lineStyle || '-';
  const fillColor   = pp.fillColor || 'transparent';
  const fillOpacity = pp.fillOpacity !== undefined ? pp.fillOpacity : 0.5;
  const minZoom     = opts.minZoom || 0;

  layers[id] = { data: data, mode: 'active', selectionOption: opts.selectionOption || 'single' };

  mp.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: 'index',
  });

  const beforeId = findBeforeId(mp, opts.beforeIds) || 'dummy_layer_1';

  // ── Fill layer ─────────────────────────────────────────────────

  let hasFill = false;

  if (opts.paintDict) {
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: opts.paintDict,
    }, beforeId);
    hasFill = true;

  } else if (opts.bins && opts.colors && opts.colorProperty) {
    const expr = ['step', ['get', opts.colorProperty], opts.colors[0]];
    for (let i = 0; i < opts.bins.length; i++) {
      expr.push(opts.bins[i], opts.colors[i + 1]);
    }
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: { 'fill-color': expr, 'fill-opacity': fillOpacity },
    }, beforeId);
    hasFill = true;

  } else if (selector) {
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: {
        'fill-color': [
          'case',
          ['boolean', ['feature-state', 'selected'], false], opts.fillColorSelected || fillColor,
          ['boolean', ['get', '_selected'], false], opts.fillColorSelected || fillColor,
          ['boolean', ['feature-state', 'hovered'], false], opts.fillColorHover || fillColor,
          fillColor,
        ],
        'fill-opacity': [
          'case',
          ['boolean', ['feature-state', 'selected'], false], opts.fillOpacitySelected || fillOpacity,
          ['boolean', ['get', '_selected'], false], opts.fillOpacitySelected || fillOpacity,
          ['boolean', ['feature-state', 'hovered'], false], opts.fillOpacityHover || fillOpacity,
          fillOpacity,
        ],
        'fill-outline-color': 'transparent',
      },
    }, beforeId);
    hasFill = true;

  } else if (fillColor && fillColor !== 'transparent') {
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: { 'fill-color': fillColor, 'fill-opacity': fillOpacity },
    }, beforeId);
    hasFill = true;
  }

  // ── Line layer ─────────────────────────────────────────────────

  const linePaint = {
    'line-color': lineColor,
    'line-width': lineWidth,
    'line-opacity': lineOpacity,
    'line-dasharray': getDashArray(lineStyle),
  };

  if (selector) {
    linePaint['line-color'] = [
      'case',
      ['boolean', ['feature-state', 'selected'], false], opts.lineColorSelected || lineColor,
      ['boolean', ['get', '_selected'], false], opts.lineColorSelected || lineColor,
      lineColor,
    ];
    linePaint['line-opacity'] = [
      'case',
      ['boolean', ['feature-state', 'selected'], false], opts.lineOpacitySelected || lineOpacity,
      ['boolean', ['get', '_selected'], false], opts.lineOpacitySelected || lineOpacity,
      lineOpacity,
    ];
    linePaint['line-width'] = [
      'case',
      ['boolean', ['feature-state', 'selected'], false], opts.lineWidthSelected || lineWidth,
      ['boolean', ['get', '_selected'], false], opts.lineWidthSelected || lineWidth,
      ['boolean', ['feature-state', 'hovered'], false], opts.lineWidthHover || lineWidth,
      lineWidth,
    ];
  }

  mp.addLayer({
    id: id + '.line', type: 'line', source: id,
    minzoom: minZoom, layout: { visibility: 'visible' },
    paint: linePaint,
  }, beforeId);

  // ── Hover popup (non-selector) ─────────────────────────────────

  if (!selector && opts.hoverProperty) {
    const hoverLayerId = hasFill ? id + '.fill' : id + '.line';
    const hoverPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

    mp.on('mouseenter', hoverLayerId, function(e) {
      mp.getCanvas().style.cursor = 'pointer';
      const val = e.features[0].properties[opts.hoverProperty];
      let text = opts.hoverProperty + ': ' + numberWithCommas(val);
      if (opts.unit) text += ' ' + opts.unit;
      hoverPopup.setLngLat(e.lngLat).setText(text).addTo(mp);
    });
    mp.on('mouseleave', hoverLayerId, function() {
      mp.getCanvas().style.cursor = window.currentCursor || '';
      hoverPopup.remove();
    });
  }

  // ── Legend ──────────────────────────────────────────────────────

  if (opts.legendItems && opts.legendItems.length > 0) {
    buildLegendFromItems(id, opts.legendTitle, opts.legendPosition, opts.legendItems);
  } else if (opts.colorLabels && opts.colors) {
    buildLegend(id, opts.legendTitle, opts.legendPosition, opts.colors, opts.colorLabels);
  }

  // ── Selector mode setup ────────────────────────────────────────

  if (selector) {
    hoverProperty = opts.hoverProperty || null;
    const fillId = id + '.fill';
    const selectionOption = opts.selectionOption || 'single';

    popup = new maplibregl.Popup({ offset: 10, closeButton: false, closeOnClick: false });

    mp.on('mousemove', fillId, mouseEnter);
    mp.on('mouseleave', fillId, mouseLeave);

    if (selectionOption === 'single') {
      mp.off('click', fillId, clickSingle);
      mp.on('click', fillId, clickSingle);
    } else {
      mp.off('click', fillId, clickMultiple);
      mp.on('click', fillId, clickMultiple);
    }

    mp.once('idle', () => {
      layerAdded(id);
    });

    const index = opts.index;
    if (index !== undefined && index !== null) {
      const indices = Array.isArray(index) ? index : [index];
      if (indices.length > 0) select(id, indices);
    }
  } else {
    mp.once('idle', () => { layerAdded(id); });
  }
}

// ── Layer operations ─────────────────────────────────────────────────

export function activate(id, lineColor) {
  if (layers[id]) layers[id].mode = 'active';
  if (map.getLayer(id + '.line')) {
    map.setPaintProperty(id + '.line', 'line-color', lineColor);
  }
}

export function deactivate(id, lineColor) {
  if (layers[id]) layers[id].mode = 'inactive';
  if (map.getLayer(id + '.line')) {
    map.setPaintProperty(id + '.line', 'line-color', lineColor);
  }
}

export function remove(id, side) {
  const mp = side ? getMap(side) : map;
  const fillId = id + '.fill';
  mp.off('mousemove', fillId, mouseEnter);
  mp.off('mouseleave', fillId, mouseLeave);
  mp.off('click', fillId, clickSingle);
  mp.off('click', fillId, clickMultiple);
  cleanUp(mp, id);
}

export function updateData(id, data, side) {
  const mp = side ? getMap(side) : map;
  const source = mp.getSource(id);
  if (source) source.setData(data);
}

export function setLegendPosition(id, position) {
  const el = document.getElementById('legend' + id);
  if (el) el.className = 'legend ' + position;
}

export function showLegend(id) {
  const el = document.getElementById('legend' + id);
  if (el) el.style.display = 'block';
}

export function hideLegend(id) {
  const el = document.getElementById('legend' + id);
  if (el) el.style.display = 'none';
}

// ── Selector: exported selection functions ───────────────────────────

export function selectByIndex(id, indices) {
  deselectAll(id);
  if (!Array.isArray(indices)) indices = [indices];
  select(id, indices);
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
  // Defer Python callback so the render frame completes first (instant visual feedback)
  const feature = e.features[0];
  setTimeout(() => featureClicked(layerId, feature), 0);
}

function clickMultiple(e) {
  if (!e.features || e.features.length === 0) return;
  const layerId = e.features[0].source;
  const clickedIndex = e.features[0].properties.index;
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  const f = features.find(f => f.properties.index === clickedIndex);
  if (f) {
    f.properties._selected = !f.properties._selected;
  }
  const src = map.getSource(layerId);
  if (src && layers[layerId]?.data) src.setData(layers[layerId].data);
  selectedFeatures = features.filter(f => f.properties._selected);
  featureClicked(layerId, selectedFeatures);
}

// ── Selector: selection helpers ──────────────────────────────────────

function select(layerId, indices) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (const idx of indices) {
    // Instant visual via feature-state
    map.setFeatureState({ source: layerId, id: idx }, { selected: true });
    // Keep data property in sync for activate/deactivate
    const f = features.find(f => f.properties.index === idx);
    if (f) f.properties._selected = true;
  }
}

function deselect(layerId, indices) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (const idx of indices) {
    map.setFeatureState({ source: layerId, id: idx }, { selected: false });
    const f = features.find(f => f.properties.index === idx);
    if (f) f.properties._selected = false;
  }
}

function deselectAll(layerId) {
  const features = layers[layerId]?.data?.features;
  if (!features) return;
  for (let i = 0; i < features.length; i++) {
    if (features[i].properties._selected) {
      map.setFeatureState({ source: layerId, id: features[i].properties.index }, { selected: false });
      features[i].properties._selected = false;
    }
  }
}

// ── Legend builders ──────────────────────────────────────────────────

function buildLegend(id, title, position, colors, labels) {
  const old = document.getElementById('legend' + id);
  if (old) old.remove();
  const el = document.createElement('div');
  el.id = 'legend' + id;
  el.className = 'legend ' + (position || 'bottom-right');
  if (title) { const t = document.createElement('div'); t.innerHTML = '<strong>' + title + '</strong>'; el.appendChild(t); }
  for (let i = 0; i < labels.length; i++) {
    const item = document.createElement('div');
    item.innerHTML = '<i style="background:' + colors[i] + '; width:18px; height:18px; display:inline-block; margin-right:5px;"></i><span>' + labels[i] + '</span>';
    el.appendChild(item);
  }
  document.body.appendChild(el);
}

function buildLegendFromItems(id, title, position, items) {
  const old = document.getElementById('legend' + id);
  if (old) old.remove();
  const el = document.createElement('div');
  el.id = 'legend' + id;
  el.className = 'legend ' + (position || 'bottom-right');
  if (title) { const t = document.createElement('div'); t.innerHTML = '<strong>' + title + '</strong>'; el.appendChild(t); }
  for (let i = 0; i < items.length; i++) {
    const item = document.createElement('div');
    // Defaults first; caller-supplied style wins on the CSS cascade.
    item.innerHTML = '<i style="display:inline-block; margin-right:5px; width:18px; height:18px; ' + items[i].style + '"></i><span>' + items[i].label + '</span>';
    el.appendChild(item);
  }
  document.body.appendChild(el);
}
