/**
 * draw_layer.js
 *
 * Manages interactive drawing layers on the MapLibre map using MapboxDraw.
 * Supports polygon, polyline, and rectangle shapes. Each shape type has
 * create / update / selection-change handlers that notify the host
 * application via featureDrawn, featureSelected, featureModified, and
 * featureDeselected callbacks (defined in main.js and exposed globally).
 *
 * Features belong to named layers. A layer can be in "active" mode
 * (editable via MapboxDraw) or "inactive" mode (rendered as static
 * GeoJSON sources so they remain visible but are not interactive).
 */

import { DrawRectangle } from '/js/mapbox-gl-draw-rectangle-mode.js';
import { drawStyles } from '/js/draw_styles.js';
import { SRMode, SRCenter } from '/js/mapbox_gl_draw_scale_rotate_mode.js';

// ── Module state ──────────────────────────────────────────────────────

/** Listener swapped in/out when the draw-create event fires. */
let createListener = dummyFunction;

/** All features currently managed by draw layers. */
var featureList = [];

/** All registered draw layers and their properties. */
var layerList = [];

/** Check if a layer has show_endpoints enabled (handles bool/string from Python). */
function hasEndpoints(layerIdOrProps) {
  var props = (typeof layerIdOrProps === 'string') ? getLayerProps(layerIdOrProps) : layerIdOrProps;
  if (!props) return false;
  var pp = props.paintProps || props;
  var v = pp.show_endpoints;
  return v === true || v === "True" || v === "true";
}

/** The layer that is currently receiving draw interactions. */
let activeLayerId;

/** MapboxDraw modes (extended with custom rectangle and scale/rotate). */
let modes;

/** ID of the feature currently selected on the map. */
let selectedFeatureId;

// ── MapboxDraw initialisation ─────────────────────────────────────────

modes = MapboxDraw.modes;
modes.draw_rectangle = DrawRectangle;
modes.scale_rotate_mode = SRMode;

draw = new MapboxDraw({
  displayControlsDefault: false,
  userProperties: true,
  styles: drawStyles,
  modes: modes,
});

// ── Event wiring ──────────────────────────────────────────────────────

/**
 * Attach all MapboxDraw event listeners to the map.
 * Safe to call multiple times; the create-listener is swapped per shape.
 */
function setDrawEvents() {
  map.on('draw.create', createListener);
  map.on('draw.modechange', modeChanged);
  map.on('draw.selectionchange', selectionChanged);
  map.on('draw.update', featureUpdated);
  // Reset to simple_select on right-click so drawing can be cancelled
  map.on("mousedown", (e) => {
    if (e.originalEvent.button === 2) {
      draw.changeMode('simple_select', { featureIds: [] });
    }
  });
}

/** No-op placeholder used as the initial createListener. */
function dummyFunction(e) {
}

/**
 * Called when MapboxDraw's internal mode changes.
 * Forces back to simple_select to keep our state machine in control.
 */
function modeChanged(e) {
  draw.changeMode('simple_select', { featureIds: [] });
}

/**
 * Dispatches selection events to the appropriate shape handler.
 * If no feature is selected, notifies the host of a deselection.
 * @param {Object} e - MapboxDraw selectionchange event.
 */
function selectionChanged(e) {
  var feature = e.features[0];
  if (feature) {
    var featureId = feature["id"];
    selectedFeatureId = featureId;
    var featureProps = getFeatureProps(featureId);
    if (featureProps.shape == "polygon") {
      polygonSelectionChanged(e);
    }
    if (featureProps.shape == "polyline") {
      polylineSelectionChanged(e);
    }
    if (featureProps.shape == "rectangle") {
      rectangleSelectionChanged(e);
    }
  } else {
    featureDeselected(activeLayerId);
  }
}

/**
 * Dispatches update events to the appropriate shape handler.
 * @param {Object} e - MapboxDraw update event.
 */
function featureUpdated(e) {
  var feature = e.features[0];
  if (feature) {
    var featureId = feature["id"];
    var featureProps = getFeatureProps(featureId);
    if (featureProps.shape == "polygon") {
      polygonUpdated(e);
    }
    if (featureProps.shape == "rectangle") {
      rectangleUpdated(e);
    }
    if (featureProps.shape == "polyline") {
      polylineUpdated(e);
    }
  }
}

// ── Mode activation helpers ───────────────────────────────────────────

/**
 * Enter scale/rotate mode for a rectangle feature.
 * @param {string} featureId - The MapboxDraw feature ID.
 */
function activateScaleRotateMode(featureId) {
  draw.changeMode('scale_rotate_mode', {
    featureId: featureId,
    canScale: true,
    canRotate: getLayerProps(activeLayerId).paintProps.rotate,
    canTrash: false,
    rotatePivot: SRCenter.Center,
    scaleCenter: SRCenter.Opposite,
    singleRotationPoint: true,
    rotationPointRadius: 1.2,
    canSelectFeatures: true,
  });
}

/**
 * Enter direct_select mode for polygon/polyline vertex editing.
 * @param {string} featureId - The MapboxDraw feature ID.
 */
function activateDirectSelectMode(featureId) {
  draw.changeMode('direct_select', { featureId: featureId });
  // Hide endpoints while editing vertices
  if (activeLayerId && hasEndpoints(activeLayerId)) _hideEndpoints(activeLayerId);
}

// ══════════════════════════════════════════════════════════════════════
//  POLYGON
// ══════════════════════════════════════════════════════════════════════

/**
 * Start interactive polygon drawing on the given layer.
 * @param {string} layerId - Target draw layer ID.
 */
export function drawPolygon(layerId) {
  map.getCanvas().style.cursor = "crosshair";
  setDrawEvents();
  activeLayerId = layerId;
  setLayerMode(layerId, 'active');
  draw.changeMode('draw_polygon');
  map.off('draw.create', createListener);
  createListener = polygonCreated;
  map.on('draw.create', createListener);
}

/**
 * Handler fired when a polygon is finished being drawn.
 * Applies paint properties, registers the feature, and notifies the host.
 */
function polygonCreated(e) {
  map.getCanvas().style.cursor = '';
  var feature = e.features[0];
  var featureId = feature["id"];
  var layerProps = getLayerProps(activeLayerId);
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(featureId, key, value);
  }
  addToFeatureList(feature, featureId, "name_polygon", activeLayerId, "polygon", feature.geometry);
  updateInactiveLayerGeometry(activeLayerId);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  featureDrawn(JSON.stringify(featureCollection), featureId, activeLayerId);
}

/** Handler for when an existing polygon's vertices are moved. */
function polygonUpdated(e) {
  var feature = e.features[0];
  var featureId = feature["id"];
  setGeometryInFeatureList(featureId, feature.geometry);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  updateInactiveLayerGeometry(activeLayerId);
  featureModified(JSON.stringify(featureCollection), featureId, activeLayerId);
}

/** Handler for when a polygon is clicked/selected on the map. */
function polygonSelectionChanged(e) {
  var feature = e.features[0];
  if (feature) {
    var featureId = feature["id"];
    activateDirectSelectMode(featureId);
    activeLayerId = getFeatureProps(featureId).layerId;
    var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
    featureSelected(JSON.stringify(featureCollection), featureId, activeLayerId);
  }
}

// ══════════════════════════════════════════════════════════════════════
//  POLYLINE
// ══════════════════════════════════════════════════════════════════════

/**
 * Start interactive polyline drawing on the given layer.
 * @param {string} id - Target draw layer ID.
 */
export function drawPolyline(id) {
  map.getCanvas().style.cursor = "crosshair";
  setDrawEvents();
  activeLayerId = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_line_string');
  // Hide endpoints while drawing
  if (hasEndpoints(id)) _hideEndpoints(id);
  map.off('draw.create', createListener);
  createListener = polylineCreated;
  map.on('draw.create', createListener);
}

/** Handler fired when a polyline is finished being drawn. */
function polylineCreated(e) {
  map.getCanvas().style.cursor = '';
  var feature = e.features[0];
  var id = feature["id"];
  var layerProps = getLayerProps(activeLayerId);
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(feature, id, "name_polyline", activeLayerId, 'polyline', feature.geometry);
  updateInactiveLayerGeometry(activeLayerId);
  // Show endpoints again after drawing finishes
  if (hasEndpoints(activeLayerId)) _showEndpoints(activeLayerId);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  featureDrawn(JSON.stringify(featureCollection), id, activeLayerId);
}

/** Handler for when an existing polyline's vertices are moved. */
function polylineUpdated(e) {
  var feature = e.features[0];
  var featureId = feature["id"];
  setGeometryInFeatureList(featureId, feature.geometry);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  updateInactiveLayerGeometry(activeLayerId);
  // Show updated endpoints after edit
  if (hasEndpoints(activeLayerId)) _showEndpoints(activeLayerId);
  featureModified(JSON.stringify(featureCollection), featureId, activeLayerId);
}

/** Handler for when a polyline is clicked/selected on the map. */
function polylineSelectionChanged(e) {
  var feature = e.features[0];
  if (feature) {
    var id = feature["id"];
    activateDirectSelectMode(id);
    activeLayerId = getFeatureProps(id).layerId;
    var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
    featureSelected(JSON.stringify(featureCollection), id, activeLayerId);
  }
}

// ══════════════════════════════════════════════════════════════════════
//  RECTANGLE
// ══════════════════════════════════════════════════════════════════════

/**
 * Start interactive rectangle drawing on the given layer.
 * @param {string} id - Target draw layer ID.
 */
export function drawRectangle(id) {
  map.getCanvas().style.cursor = "crosshair";
  setDrawEvents();
  activeLayerId = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_rectangle');
  map.off('draw.create', createListener);
  createListener = rectangleCreated;
  map.on('draw.create', createListener);
}

/** Handler fired when a rectangle is finished being drawn. */
function rectangleCreated(e) {
  map.getCanvas().style.cursor = '';
  var feature = e.features[0];
  var id = feature["id"];
  var layerProps = getLayerProps(activeLayerId);
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(feature, id, "name_rectangle", activeLayerId, 'rectangle', feature.geometry);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  featureDrawn(JSON.stringify(featureCollection), id, activeLayerId);
}

/** Handler for when an existing rectangle is moved or resized. */
function rectangleUpdated(e) {
  var feature = e.features[0];
  var featureId = feature["id"];
  setGeometryInFeatureList(featureId, feature.geometry);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  updateInactiveLayerGeometry(activeLayerId);
  featureModified(JSON.stringify(featureCollection), featureId, activeLayerId);
}

/** Handler for when a rectangle is clicked/selected on the map. */
function rectangleSelectionChanged(e) {
  var feature = e.features[0];
  if (feature) {
    var id = feature["id"];
    activateScaleRotateMode(id);
    activeLayerId = getFeatureProps(id).layerId;
    var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
    featureSelected(JSON.stringify(featureCollection), id, activeLayerId);
  }
}

// ══════════════════════════════════════════════════════════════════════
//  FEATURE MANAGEMENT
// ══════════════════════════════════════════════════════════════════════

/**
 * Add a feature (received as a GeoJSON FeatureCollection) to a draw layer.
 * The feature is plotted on the map and registered in the internal list.
 * @param {Object} featureCollection - GeoJSON FeatureCollection with one feature.
 * @param {string} layerId - Target draw layer ID.
 * @param {string} featureId - Unique ID to assign to the feature.
 */
export function addFeature(featureCollection, layerId, featureId) {
  setDrawEvents();
  activeLayerId = layerId;
  var geometry = featureCollection.features[0].geometry;
  if (featureCollection.features[0].properties.name == null) {
    var featureName = geometry.type;
  } else {
    var featureName = featureCollection.features[0].properties.name;
  }
  var layerProps = getLayerProps(layerId);
  if (layerProps == null) {
    console.log("No draw layer found with ID " + layerId);
    return;
  }
  var feature = plotFeature(featureId, geometry, layerProps.paintProps);
  addToFeatureList(feature, featureId, featureName, layerId, layerProps.shape, geometry);
  updateInactiveLayerGeometry(layerId);
  setLayerMode(layerId, layerProps.mode);
}

/**
 * Plot a single feature on the MapboxDraw canvas and apply paint properties.
 * @param {string} featureId - Unique feature ID.
 * @param {Object} geometry - GeoJSON geometry object.
 * @param {Object} paintProps - Key/value paint properties to set.
 * @returns {Object} The constructed GeoJSON Feature.
 */
function plotFeature(featureId, geometry, paintProps) {
  var feature = {
    id: featureId,
    type: 'Feature',
    properties: {},
    geometry: geometry
  };
  draw.add(feature);
  for (const [key, value] of Object.entries(paintProps)) {
    draw.setFeatureProperty(featureId, key, value);
  }
  return feature;
}

/**
 * Remove a feature from the map and the internal feature list.
 * @param {string} featureId - ID of the feature to delete.
 */
export function deleteFeature(featureId) {
  var featureProps = featureList.find(v => v.featureId === featureId) || null;
  if (featureProps == null) {
    console.log('Feature ' + featureId + ' not found in feature list !');
    return;
  }
  var layerId = featureProps.layerId;
  draw.delete(featureId);
  removeFromFeatureList(featureId);
  updateInactiveLayerGeometry(layerId);
}

/**
 * Programmatically select and activate a feature on the map.
 * Enters direct_select for polygons/polylines or scale_rotate for rectangles.
 * @param {string} featureId - ID of the feature to activate.
 */
export function activateFeature(featureId) {
  draw.changeMode('simple_select', { featureIds: [featureId] });
  selectedFeatureId = featureId;
  activeLayerId = getFeatureProps(featureId).layerId;
  var featureProps = getFeatureProps(featureId);
  if (featureProps.shape == "polygon" || featureProps.shape == "polyline") {
    activateDirectSelectMode(featureId);
  }
  if (featureProps.shape == "rectangle") {
    activateScaleRotateMode(featureId);
  }
}

// ── Feature list helpers ──────────────────────────────────────────────

/** Register a feature in the internal tracking list. */
function addToFeatureList(feature, featureId, featureName, layerId, shape, geometry) {
  featureList.push({
    feature: feature,
    featureId: featureId,
    name: featureName,
    shape: shape,
    layerId: layerId,
    geometry: geometry
  });
}

/** Update the cached geometry for a tracked feature. */
function setGeometryInFeatureList(featureId, geometry) {
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].featureId == featureId) {
      featureList[i].geometry = geometry;
    }
  }
}

/**
 * Replace a feature's geometry on the map and in the internal list.
 * Deletes and re-adds the feature to MapboxDraw to apply new coordinates.
 * @param {string} layerId - The layer the feature belongs to.
 * @param {string} featureId - The feature to update.
 * @param {Object} geometry - New GeoJSON geometry.
 */
export function setFeatureGeometry(layerId, featureId, geometry) {
  setGeometryInFeatureList(featureId, geometry);
  // Update in MapboxDraw if the feature is currently in draw
  var feature = draw.get(featureId);
  if (feature) {
    var properties = feature.properties;
    draw.delete(featureId);
    draw.add({
      id: featureId,
      type: 'Feature',
      properties: properties,
      geometry: geometry,
    });
  }
  // Always update the inactive backing source
  updateInactiveLayerGeometry(layerId);
}

/** Remove a feature from the internal tracking list by ID. */
function removeFromFeatureList(featureId) {
  featureList.splice(featureList.findIndex(v => v.featureId === featureId), 1);
}

/**
 * Look up a feature's properties (shape, layerId, geometry, etc.) by ID.
 * @param {string} featureId - The feature ID to search for.
 * @returns {Object|null} The feature entry or null if not found.
 */
function getFeatureProps(featureId) {
  return featureList.find(v => v.featureId === featureId) || null;
}

/**
 * Build a GeoJSON FeatureCollection from all features in a given layer.
 * Used both for active-layer reporting and inactive-layer rendering.
 * @param {string} layerId - The layer to collect features from.
 * @returns {Object} A GeoJSON FeatureCollection.
 */
function getFeatureCollectionInActiveLayer(layerId) {
  var featureCollection = {};
  featureCollection.type = "FeatureCollection";
  featureCollection.features = [];
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layerId == layerId) {
      var feature = {};
      feature.type = "Feature";
      feature.properties = {};
      feature.properties["id"] = featureList[i].featureId;
      feature.id = featureList[i].featureId;
      feature.name = featureList[i].name;
      feature.geometry = featureList[i].geometry;
      featureCollection.features.push(feature);
    }
  }
  return featureCollection;
}

/**
 * Build a GeoJSON FeatureCollection for an inactive layer.
 * @param {string} layerId - The layer to collect features from.
 * @returns {Object} A GeoJSON FeatureCollection.
 */

// ══════════════════════════════════════════════════════════════════════
//  LAYER MANAGEMENT
// ══════════════════════════════════════════════════════════════════════

/**
 * Register a new draw layer and create its backing GeoJSON source/layers.
 * Adds line and fill sub-layers depending on the shape type.
 * @param {string} layerId - Unique layer identifier.
 * @param {string} mode - Initial mode: "active" or "inactive".
 * @param {Object} paintProps - Paint properties for the layer's features.
 * @param {string} shape - Shape type: "polygon", "polyline", or "rectangle".
 */
export function addLayer(layerId, mode, paintProps, shape) {
  var props = getLayerProps(layerId);
  if (props != null) {
    return;
  }
  addToLayerList(layerId, mode, paintProps, shape);

  // Create the GeoJSON source that holds inactive-mode geometry
  map.addSource(layerId, {
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': []
    }
  });
  if (shape == 'polyline' || shape == "polygon" || shape == "rectangle") {
    map.addLayer({
      'id': layerId + ".line",
      'type': 'line',
      'source': layerId,
      'layout': {},
      'paint': {
        'line-color': paintProps.polyline_line_color,
        'line-width': paintProps.polyline_line_width,
        'line-opacity': paintProps.polyline_line_opacity
      }
    });
  }
  if (shape == 'polygon' || shape == "rectangle") {
    map.addLayer({
      'id': layerId + ".fill",
      'type': 'fill',
      'source': layerId,
      'layout': {},
      'paint': {
        'fill-color': paintProps.polygon_fill_color,
        'fill-opacity': paintProps.polygon_fill_opacity
      }
    });
  }

  // Endpoint markers for polylines (start + end circles)
  if (shape == 'polyline' && hasEndpoints({paintProps: paintProps})) {
    _createEndpointLayers(layerId, paintProps);
  }
}

/**
 * Create the endpoint circle layers and legend for a polyline draw layer.
 * Deferred until map style is loaded to avoid silent failures.
 */
function _createEndpointLayers(layerId, paintProps) {
  function create() {
    // Guard against duplicate creation
    if (map.getSource(layerId + ".startpts")) return;

    map.addSource(layerId + ".startpts", {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: [] },
    });
    map.addSource(layerId + ".endpts", {
      type: 'geojson',
      data: { type: 'FeatureCollection', features: [] },
    });
    map.addLayer({
      id: layerId + ".startcircle",
      type: 'circle',
      source: layerId + ".startpts",
      layout: { visibility: 'visible' },
      paint: {
        'circle-color': paintProps.endpoint_start_color,
        'circle-radius': paintProps.endpoint_radius,
        'circle-stroke-color': '#fff',
        'circle-stroke-width': 1.5,
      },
    });
    map.addLayer({
      id: layerId + ".endcircle",
      type: 'circle',
      source: layerId + ".endpts",
      layout: { visibility: 'visible' },
      paint: {
        'circle-color': paintProps.endpoint_end_color,
        'circle-radius': paintProps.endpoint_radius,
        'circle-stroke-color': '#fff',
        'circle-stroke-width': 1.5,
      },
    });

    // Build legend
    var labels = paintProps.endpoint_labels || { start: "Start", end: "End" };
    var legendDiv = document.createElement('div');
    legendDiv.id = 'legend' + layerId;
    legendDiv.className = 'legend bottom-right-2';

    var items = [
      { color: paintProps.endpoint_start_color, text: labels.start },
      { color: paintProps.endpoint_end_color, text: labels.end },
    ];
    for (var item of items) {
      var row = document.createElement('div');
      var swatch = document.createElement('i');
      swatch.classList.add('circle');
      swatch.setAttribute('style', 'background:' + item.color);
      row.appendChild(swatch);
      var span = document.createElement('span');
      span.textContent = item.text;
      row.appendChild(span);
      legendDiv.appendChild(row);
    }
    legendDiv.style.visibility = 'hidden';
    document.body.appendChild(legendDiv);
  }

  // Try immediately; if map isn't ready yet, retry on 'idle'
  try {
    create();
  } catch (e) {
    console.log("Deferring endpoint layer creation for " + layerId);
    map.once('idle', create);
  }
}

/**
 * Push the current feature geometries to the inactive GeoJSON source.
 * @param {string} layerId - The layer whose source should be updated.
 */
function updateInactiveLayerGeometry(layerId) {
  var featureCollection = getFeatureCollectionInActiveLayer(layerId);
  map.getSource(layerId).setData(featureCollection);

  // Update endpoint markers if enabled
  var layerProps = getLayerProps(layerId);
  if (hasEndpoints(layerId)) {
    _updateEndpoints(layerId, featureCollection);
  }
}

/**
 * Remove a draw layer and all of its features from the map.
 * @param {string} layerId - The layer to delete.
 */
export function deleteLayer(layerId) {
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layerId == layerId) {
      deleteFeature(featureList[i].featureId);
    }
  }
  if (map.getLayer(layerId + ".line")) {
    map.removeLayer(layerId + ".line");
  }
  if (map.getLayer(layerId + ".fill")) {
    map.removeLayer(layerId + ".fill");
  }
  // Clean up endpoint layers
  if (map.getLayer(layerId + ".startcircle")) map.removeLayer(layerId + ".startcircle");
  if (map.getLayer(layerId + ".endcircle")) map.removeLayer(layerId + ".endcircle");
  if (map.getSource(layerId + ".startpts")) map.removeSource(layerId + ".startpts");
  if (map.getSource(layerId + ".endpts")) map.removeSource(layerId + ".endpts");
  var legend = document.getElementById('legend' + layerId);
  if (legend) legend.remove();

  map.removeSource(layerId);
  removeFromLayerList(layerId);
}

/**
 * Switch a layer between "active" (editable via MapboxDraw) and "inactive"
 * (rendered as static GeoJSON). In active mode, features are added to
 * MapboxDraw and the static layers are hidden. In inactive mode, features
 * are removed from MapboxDraw and the static layers become visible.
 * @param {string} layerId - The layer to switch.
 * @param {string} mode - "active" or "inactive".
 */
export function setLayerMode(layerId, mode) {
  var layerProps = getLayerProps(layerId);
  if (layerProps == null) {
    return;
  }
  if (mode == "active") {
    // Add features to MapboxDraw for interactive editing
    for (let i = 0; i < featureList.length; i++) {
      if (featureList[i].layerId == layerId) {
        var featureId = featureList[i].featureId;
        var geometry = featureList[i].geometry;
        var paintProps = layerProps.paintProps;
        plotFeature(featureId, geometry, paintProps);
      }
    }
  } else {
    // Remove features from MapboxDraw (they stay in the static source)
    for (let i = 0; i < featureList.length; i++) {
      if (featureList[i].layerId == layerId) {
        draw.delete(featureList[i].featureId);
      }
    }
  }
  setLayerProps(layerId, "mode", mode);

  // Toggle visibility of the static backing layers
  var showEndpoints = hasEndpoints(layerProps);
  if (mode == "inactive") {
    map.setLayoutProperty(layerId + ".line", 'visibility', 'visible');
    var fillLayer = map.getLayer(layerId + '.fill');
    if (typeof fillLayer !== 'undefined') {
      map.setLayoutProperty(layerId + ".fill", 'visibility', 'visible');
    }
    if (showEndpoints) {
      _showEndpoints(layerId);
    }
  } else if (mode == "invisible") {
    map.setLayoutProperty(layerId + ".line", 'visibility', 'none');
    var fillLayer = map.getLayer(layerId + '.fill');
    if (typeof fillLayer !== 'undefined') {
      map.setLayoutProperty(layerId + ".fill", 'visibility', 'none');
    }
    if (showEndpoints) {
      _hideEndpoints(layerId);
    }
  } else {
    // active mode — hide static layers, MapboxDraw handles rendering
    // But show endpoints (they hide only during vertex editing / drawing)
    map.setLayoutProperty(layerId + ".line", 'visibility', 'none');
    var fillLayer = map.getLayer(layerId + '.fill');
    if (typeof fillLayer !== 'undefined') {
      map.setLayoutProperty(layerId + ".fill", 'visibility', 'none');
    }
    if (showEndpoints) {
      _showEndpoints(layerId);
    }
  }
}

/**
 * Extract start and end points from polyline features and update
 * the endpoint GeoJSON sources.
 */
function _showEndpoints(layerId) {
  var fc = getFeatureCollectionInActiveLayer(layerId);
  _updateEndpoints(layerId, fc);
  if (map.getLayer(layerId + ".startcircle")) map.setLayoutProperty(layerId + ".startcircle", 'visibility', 'visible');
  if (map.getLayer(layerId + ".endcircle")) map.setLayoutProperty(layerId + ".endcircle", 'visibility', 'visible');
  var legend = document.getElementById('legend' + layerId);
  if (legend) legend.style.visibility = 'visible';
}

function _hideEndpoints(layerId) {
  if (map.getLayer(layerId + ".startcircle")) map.setLayoutProperty(layerId + ".startcircle", 'visibility', 'none');
  if (map.getLayer(layerId + ".endcircle")) map.setLayoutProperty(layerId + ".endcircle", 'visibility', 'none');
  var legend = document.getElementById('legend' + layerId);
  if (legend) legend.style.visibility = 'hidden';
}

function _updateEndpoints(layerId, featureCollection) {
  var startFeatures = [];
  var endFeatures = [];

  for (var feature of featureCollection.features) {
    if (!feature.geometry || feature.geometry.type !== 'LineString') continue;
    var coords = feature.geometry.coordinates;
    if (coords.length < 2) continue;

    startFeatures.push({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: coords[0] },
      properties: { id: feature.properties.id },
    });
    endFeatures.push({
      type: 'Feature',
      geometry: { type: 'Point', coordinates: coords[coords.length - 1] },
      properties: { id: feature.properties.id },
    });
  }

  var startSrc = map.getSource(layerId + ".startpts");
  var endSrc = map.getSource(layerId + ".endpts");
  if (startSrc) startSrc.setData({ type: 'FeatureCollection', features: startFeatures });
  if (endSrc) endSrc.setData({ type: 'FeatureCollection', features: endFeatures });
}

// ── Layer list helpers ────────────────────────────────────────────────

/** Add a layer to the internal tracking list (if not already present). */
function addToLayerList(layerId, mode, paintProps, shape) {
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index < 0) {
    layerList.push({ layerId: layerId, mode: mode, paintProps: paintProps, shape: shape });
  }
}

/** Remove a layer from the internal tracking list. */
/** Remove a layer from the internal tracking list by layer ID. */
function removeFromLayerList(layerId) {
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index >= 0) {
    layerList.splice(index, 1);
  }
}

/** Clear all entries from the layer tracking list. */
export function clearLayerList() {
  layerList = [];
}

/**
 * Retrieve a layer's properties by ID.
 * @param {string} layerId - The layer to look up.
 * @returns {Object|null} The layer entry or null.
 */
function getLayerProps(layerId) {
  var props = null;
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index >= 0) { props = layerList[index]; }
  return props;
}

/**
 * Set a single property on a layer entry.
 * @param {string} layerId - The layer to update.
 * @param {string} key - Property name.
 * @param {*} val - Property value.
 */
function setLayerProps(layerId, key, val) {
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index >= 0) { layerList[index][key] = val; }
}

// ══════════════════════════════════════════════════════════════════════
//  UTILITIES
// ══════════════════════════════════════════════════════════════════════

/**
 * Reset the draw mode to simple_select (no active drawing).
 */
export function setMouseDefault() {
  draw.changeMode('simple_select', { featureIds: [] });
}

