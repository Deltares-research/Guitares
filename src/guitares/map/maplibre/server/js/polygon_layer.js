/**
 * Unified polygon layer for MapLibre GL.
 *
 * Handles simple outlines, filled polygons, choropleths, custom paint
 * expressions, and interactive selection. Consistent API with
 * line_layer.js and circle_layer.js: addLayer(id, data, pp, options).
 *
 * @module polygon_layer
 */

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

function getMap(side) {
  if (side === 'a') return window.mapA || map;
  if (side === 'b') return window.mapB || map;
  return map;
}

function cleanUp(mp, id) {
  for (var suffix of ['.line', '.fill']) {
    if (mp.getLayer(id + suffix)) mp.removeLayer(id + suffix);
  }
  if (mp.getSource(id)) mp.removeSource(id);
  var legend = document.getElementById('legend' + id);
  if (legend) legend.remove();
}

function getDashArray(style) {
  if (style === '--') return [2, 1];
  if (style === '..') return [0.5, 1];
  return [1];
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
  var opts = options || {};
  var mp = getMap(opts.side);
  var selector = opts.selector || false;

  cleanUp(mp, id);

  var lineColor   = pp.lineColor || 'black';
  var lineWidth   = pp.lineWidth !== undefined ? pp.lineWidth : 1;
  var lineOpacity = pp.lineOpacity !== undefined ? pp.lineOpacity : 1;
  var lineStyle   = pp.lineStyle || opts.lineStyle || '-';
  var fillColor   = pp.fillColor || 'transparent';
  var fillOpacity = pp.fillOpacity !== undefined ? pp.fillOpacity : 0.5;
  var minZoom     = opts.minZoom || 0;

  layers[id] = { data: data, mode: 'active', selectionOption: opts.selectionOption || 'single' };

  mp.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: selector ? 'index' : (opts.hoverProperty || 'index'),
    generateId: !selector,
  });

  // ── Fill layer ─────────────────────────────────────────────────

  var hasFill = false;

  if (opts.paintDict) {
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: opts.paintDict,
    });
    hasFill = true;

  } else if (opts.bins && opts.colors && opts.colorProperty) {
    var expr = ['step', ['get', opts.colorProperty], opts.colors[0]];
    for (var i = 0; i < opts.bins.length; i++) {
      expr.push(opts.bins[i], opts.colors[i + 1]);
    }
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: { 'fill-color': expr, 'fill-opacity': fillOpacity },
    });
    hasFill = true;

  } else if (selector) {
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: {
        'fill-color': [
          'case',
          ['boolean', ['feature-state', 'selected'], false], opts.fillColorSelected || fillColor,
          ['boolean', ['feature-state', 'hovered'], false], opts.fillColorHover || fillColor,
          fillColor,
        ],
        'fill-opacity': [
          'case',
          ['boolean', ['feature-state', 'selected'], false], opts.fillOpacitySelected || fillOpacity,
          ['boolean', ['feature-state', 'hovered'], false], opts.fillOpacityHover || fillOpacity,
          fillOpacity,
        ],
        'fill-outline-color': 'transparent',
      },
    });
    hasFill = true;

  } else if (fillColor && fillColor !== 'transparent') {
    mp.addLayer({
      id: id + '.fill', type: 'fill', source: id,
      minzoom: minZoom, layout: { visibility: 'visible' },
      paint: { 'fill-color': fillColor, 'fill-opacity': fillOpacity },
    });
    hasFill = true;
  }

  // ── Line layer ─────────────────────────────────────────────────

  var linePaint = {
    'line-color': lineColor,
    'line-width': lineWidth,
    'line-opacity': lineOpacity,
    'line-dasharray': getDashArray(lineStyle),
  };

  if (selector) {
    linePaint['line-color'] = [
      'case',
      ['boolean', ['feature-state', 'selected'], false], opts.lineColorSelected || lineColor,
      lineColor,
    ];
    linePaint['line-opacity'] = [
      'case',
      ['boolean', ['feature-state', 'selected'], false], opts.lineOpacitySelected || lineOpacity,
      lineOpacity,
    ];
    linePaint['line-width'] = [
      'case',
      ['boolean', ['feature-state', 'selected'], false], opts.lineWidthSelected || lineWidth,
      ['boolean', ['feature-state', 'hovered'], false], opts.lineWidthHover || lineWidth,
      lineWidth,
    ];
  }

  mp.addLayer({
    id: id + '.line', type: 'line', source: id,
    minzoom: minZoom, layout: { visibility: 'visible' },
    paint: linePaint,
  });

  // ── Hover popup (non-selector) ─────────────────────────────────

  if (!selector && opts.hoverProperty) {
    var hoverLayerId = hasFill ? id + '.fill' : id + '.line';
    var hoverPopup = new maplibregl.Popup({ closeButton: false, closeOnClick: false });

    mp.on('mouseenter', hoverLayerId, function(e) {
      mp.getCanvas().style.cursor = 'pointer';
      var val = e.features[0].properties[opts.hoverProperty];
      var text = opts.hoverProperty + ': ' + numberWithCommas(val);
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
    var fillId = id + '.fill';
    var selectionOption = opts.selectionOption || 'single';

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
      deselectAll(id);
      layerAdded(id);
    });

    var index = opts.index;
    if (index !== undefined && index !== null) {
      var indices = Array.isArray(index) ? index : [index];
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
  var mp = side ? getMap(side) : map;
  var fillId = id + '.fill';
  mp.off('mousemove', fillId, mouseEnter);
  mp.off('mouseleave', fillId, mouseLeave);
  mp.off('click', fillId, clickSingle);
  mp.off('click', fillId, clickMultiple);
  cleanUp(mp, id);
}

export function updateData(id, data, side) {
  var mp = side ? getMap(side) : map;
  var source = mp.getSource(id);
  if (source) source.setData(data);
}

export function setLegendPosition(id, position) {
  var el = document.getElementById('legend' + id);
  if (el) el.className = 'legend ' + position;
}

export function showLegend(id) {
  var el = document.getElementById('legend' + id);
  if (el) el.style.display = 'block';
}

export function hideLegend(id) {
  var el = document.getElementById('legend' + id);
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
  var feature = e.features[0];
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
  var layerId = e.features[0].source;
  if (selectedIndex !== null) deselect(layerId, [selectedIndex]);
  selectedIndex = e.features[0].id;
  select(layerId, [selectedIndex]);
  featureClicked(layerId, e.features[0]);
}

function clickMultiple(e) {
  if (!e.features || e.features.length === 0) return;
  var layerId = e.features[0].source;
  var index = e.features[0].id;
  var state = map.getFeatureState({ source: layerId, id: index });
  if (state.selected) {
    deselect(layerId, [index]);
  } else {
    select(layerId, [index]);
  }
  selectedFeatures = [];
  for (var i = 0; i < layers[layerId].data.features.length; i++) {
    var fs = map.getFeatureState({ source: layerId, id: i });
    if (fs.selected) selectedFeatures.push(layers[layerId].data.features[i]);
  }
  featureClicked(layerId, selectedFeatures);
}

// ── Selector: selection helpers ──────────────────────────────────────

function select(layerId, indices) {
  for (var idx of indices) {
    map.setFeatureState({ source: layerId, id: idx }, { selected: true });
  }
}

function deselect(layerId, indices) {
  for (var idx of indices) {
    map.setFeatureState({ source: layerId, id: idx }, { selected: false });
  }
}

function deselectAll(layerId) {
  var features = layers[layerId]?.data?.features;
  if (!features) return;
  for (var i = 0; i < features.length; i++) {
    map.setFeatureState({ source: layerId, id: i }, { selected: false });
  }
}

// ── Legend builders ──────────────────────────────────────────────────

function buildLegend(id, title, position, colors, labels) {
  var old = document.getElementById('legend' + id);
  if (old) old.remove();
  var el = document.createElement('div');
  el.id = 'legend' + id;
  el.className = 'legend ' + (position || 'bottom-right');
  if (title) { var t = document.createElement('div'); t.innerHTML = '<strong>' + title + '</strong>'; el.appendChild(t); }
  for (var i = 0; i < labels.length; i++) {
    var item = document.createElement('div');
    item.innerHTML = '<i style="background:' + colors[i] + '; width:18px; height:18px; display:inline-block; margin-right:5px;"></i><span>' + labels[i] + '</span>';
    el.appendChild(item);
  }
  document.body.appendChild(el);
}

function buildLegendFromItems(id, title, position, items) {
  var old = document.getElementById('legend' + id);
  if (old) old.remove();
  var el = document.createElement('div');
  el.id = 'legend' + id;
  el.className = 'legend ' + (position || 'bottom-right');
  if (title) { var t = document.createElement('div'); t.innerHTML = '<strong>' + title + '</strong>'; el.appendChild(t); }
  for (var i = 0; i < items.length; i++) {
    var item = document.createElement('div');
    item.innerHTML = '<i style="' + items[i].style + '; width:18px; height:18px; display:inline-block; margin-right:5px;"></i><span>' + items[i].label + '</span>';
    el.appendChild(item);
  }
  document.body.appendChild(el);
}
