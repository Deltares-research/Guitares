/**
 * compare.js - Split-screen map comparison module.
 *
 * Sets up the QWebChannel bridge to Python, initializes two MapLibre GL maps
 * with a compare slider, and exposes exported functions for map control
 * (pan, zoom, layers, etc.) on both map panes.
 */

import { BackgroundLayerSelector, setMapStyle } from "./basemap_control.js";

// ---------------------------------------------------------------------------
// Module-level state
// ---------------------------------------------------------------------------

let mapReady;
let mapMoved;
let mouseMoved;
let getMapExtent;
let getMapCenter;
export let pong;
export let mapLibreImported;
export let jsonString;
export let pointClicked;
export let layerStyleSet;
export let marker;
export let activeSide = 'a';

let webChannelReady = false;
let firstPong = true;

// ---------------------------------------------------------------------------
// QWebChannel initialization
// ---------------------------------------------------------------------------

/**
 * Wait until the QWebChannel global is available (injected by Qt).
 * @param {number} timeout - Maximum wait time in milliseconds.
 * @returns {Promise} Resolves with QWebChannel once available.
 */
function waitForQWebChannel(timeout = 10000) {
  return new Promise((resolve, reject) => {
    const start = performance.now();
    (function check() {
      if (typeof QWebChannel !== 'undefined') {
        resolve(QWebChannel);
      } else if (performance.now() - start > timeout) {
        reject(new Error("QWebChannel not available within timeout"));
      } else {
        setTimeout(check, 100);
      }
    })();
  });
}

waitForQWebChannel()
  .then(() => {
    // Web Channel
    try {
      new QWebChannel(qt.webChannelTransport, function (channel) {
        window.MapLibreCompare = channel.objects.MapLibreCompare;
        if (typeof MapLibreCompare != 'undefined') {
          pong              = function() { MapLibreCompare.pong("pong")};
          mapReady          = function() { MapLibreCompare.mapReady(jsonString)};
          mapMoved          = function() { MapLibreCompare.mapMoved(jsonString)};
          mouseMoved        = function(coords) { MapLibreCompare.mouseMoved(JSON.stringify(coords))};
          getMapExtent      = function() { MapLibreCompare.getMapExtent(jsonString)};
          getMapCenter      = function() { MapLibreCompare.getMapCenter(jsonString)};
          featureClicked    = function(featureId, featureProps) { MapLibreCompare.featureClicked(featureId, JSON.stringify(featureProps))};
          featureDrawn      = function(featureCollection, featureId, layerId) { MapLibreCompare.featureDrawn(featureCollection, featureId, layerId)};
          featureModified   = function(featureCollection, featureId, layerId) { MapLibreCompare.featureModified(featureCollection, featureId, layerId)};
          featureSelected   = function(featureCollection, featureId, layerId) { MapLibreCompare.featureSelected(featureCollection, featureId, layerId)};
          featureAdded      = function(featureCollection, featureId, layerId) { MapLibreCompare.featureAdded(featureCollection, featureId, layerId)};
          featureDeselected = function(layerId) { MapLibreCompare.featureDeselected(layerId)};
          pointClicked      = function(coords) { MapLibreCompare.pointClicked(JSON.stringify(coords))};
          layerStyleSet     = function() { MapLibreCompare.layerStyleSet('')};
          layerAdded        = function(layerId) { MapLibreCompare.layerAdded(layerId)};
          webChannelReady   = true;
        }
      });
    } catch (error) {
      console.error('WebChannel not found:', error);
    }
  })
  .catch((err) => {
    console.error("Error loading QWebChannel:", err);
  });

// ---------------------------------------------------------------------------
// Exported functions
// ---------------------------------------------------------------------------

/**
 * Respond to a ping from Python. Sends a single pong on the first
 * successful ping after the web channel is ready.
 * @param {string} ping_string - The ping payload from Python.
 */
export function ping(ping_string) {
  if (webChannelReady && firstPong) {
    firstPong = false;
    pong();
  }
}

/**
 * Create the two MapLibre GL map instances with a compare slider,
 * add controls (navigation, scale, ruler, background-layer selector),
 * and wire up event handlers.
 */
export function addMap() {
  mapA = new maplibregl.Map({
    container: 'compare1',
    style: window.mapStyles[default_compare_style],
    center: default_compare_center,
    zoom: default_compare_zoom,
    canvasContextAttributes: { alpha: true },
  });

  mapA.scrollZoom.setWheelZoomRate(1 / 200);

  mapA.on('error', (e) => {
    if (e.error && e.error.message && !e.error.message.includes('could not be decoded')) {
      console.log('Map A error: ' + e.error.message);
    }
  });

  mapB = new maplibregl.Map({
    container: 'compare2',
    style: window.mapStyles[default_compare_style],
    center: default_compare_center,
    zoom: default_compare_zoom,
    canvasContextAttributes: { alpha: true },
  });

  mapB.scrollZoom.setWheelZoomRate(1 / 200);

  mapB.on('error', (e) => {
    if (e.error && e.error.message && !e.error.message.includes('could not be decoded')) {
      console.log('Map B error: ' + e.error.message);
    }
  });

  // Set global 'map' alias for basemap_control.js compatibility
  window.map = mapA;

  // Navigation control on mapA
  const nav = new maplibregl.NavigationControl({
    visualizePitch: true
  });
  mapA.addControl(nav, 'top-left');

  // Background layer selector
  var backgroundLayers = [];
  for (var key in window.mapStyles) {
    backgroundLayers.push({"id": key, "name": window.mapStyles[key].name});
  }
  mapA.addControl(new BackgroundLayerSelector(backgroundLayers, default_compare_style, (styleID) => {
    setMapStyle(styleID, mapA);
    setMapStyle(styleID, mapB);
  }), 'top-left');

  // Scale
  mapA.addControl(new maplibregl.ScaleControl({maxWidth: 80}), 'bottom-left');

  // Draggable marker
  marker = new maplibregl.Marker({draggable: true});

  window.currentCursor = '';

  // Compare slider
  const container = '#comparison-container';
  var mapContainer = new maplibregl.Compare(mapA, mapB, container, {
  });

  // Track which side the user is interacting with
  mapA.on('wheel', () => {
    activeSide = 'a';
  });
  mapB.on('wheel', () => {
    activeSide = 'b';
  });
  mapA.on('dragstart', () => {
    activeSide = 'a';
  });
  mapB.on('dragstart', () => {
    activeSide = 'b';
  });

  mapA.on('moveend', () => {
    onMoveEndA();
  });
  mapB.on('moveend', () => {
    onMoveEndB();
  });

  mapA.on('mousemove', (e) => {
    onMouseMoved(e);
  });

  mapA.on('load', () => {
    addDummyLayer(mapA, 'dummy_layer_0');
    addDummyLayer(mapA, 'dummy_layer_1');
    // Load icons
    if (typeof compareIconUrls !== 'undefined') {
      compareIconUrls.forEach(async (iconUrl) => {
        try {
          const image = await mapA.loadImage(iconUrl);
          if (!mapA.hasImage(iconUrl)) {
            mapA.addImage(iconUrl, image.data);
          }
        } catch (e) {
          // Silently ignore icon loading errors (e.g. DOMException from duplicate adds)
        }
      });
    }
    mapLoadedA();
  });

  mapB.on('load', () => {
    addDummyLayer(mapB, 'dummy_layer_0');
    addDummyLayer(mapB, 'dummy_layer_1');
    // Load icons
    if (typeof compareIconUrls !== 'undefined') {
      compareIconUrls.forEach(async (iconUrl) => {
        try {
          const image = await mapB.loadImage(iconUrl);
          if (!mapB.hasImage(iconUrl)) {
            mapB.addImage(iconUrl, image.data);
          }
        } catch (e) {
          // Silently ignore icon loading errors (e.g. DOMException from duplicate adds)
        }
      });
    }
    mapLoadedB();
  });

  mapA.on('style.load', () => {
    // Reserved for future use (buildings, terrain source, etc.)
  });

  mapB.on('style.load', () => {
    // Reserved for future use (buildings, terrain source, etc.)
  });
}

/**
 * Remove a map layer and all its sub-layers (line, fill, circle, a, b),
 * associated sources, and legend elements.
 * @param {string} id   - Base layer identifier.
 * @param {string} side - Side indicator ("a" or "b").
 */
export function removeLayer(id, side) {
  var mp = getMap(side);
  var suffixes = ['', '.line', '.fill', '.circle', '.a', '.b'];
  for (var i = 0; i < suffixes.length; i++) {
    var layerId = id + suffixes[i];
    if (typeof mp.getLayer(layerId) !== 'undefined') {
      mp.removeLayer(layerId);
    }
  }
  // Remove sources
  var sourceSuffixes = ['', '.a', '.b'];
  for (var i = 0; i < sourceSuffixes.length; i++) {
    var sourceId = id + sourceSuffixes[i];
    if (typeof mp.getSource(sourceId) !== 'undefined') {
      mp.removeSource(sourceId);
    }
  }
  // Remove legend
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.remove();
  }
}

/**
 * Reset the mouse cursor to default and deactivate click/ruler listeners.
 */
export function setMouseDefault() {
  mapA.getCanvas().style.cursor = '';
  window.currentCursor = '';
  mapA.off('click', onPointClicked);
  deactivateRuler();
}

/**
 * Show a layer and all its sub-layers on the map, including its legend.
 * @param {string} id   - Base layer identifier.
 * @param {string} side - Side indicator ("a" or "b").
 */
export function showLayer(id, side) {
  var mp = getMap(side);
  var suffixes = ['', '.line', '.fill', '.circle', '.a', '.b'];
  for (var i = 0; i < suffixes.length; i++) {
    var map_id = id + suffixes[i];
    if (mp.getLayer(map_id)) {
      mp.setLayoutProperty(map_id, 'visibility', 'visible');
    }
  }
  showLegend(id);
  showLegend(id + '.a');
}

/**
 * Hide a layer and all its sub-layers on the map, including its legend.
 * @param {string} id   - Base layer identifier.
 * @param {string} side - Side indicator ("a" or "b").
 */
export function hideLayer(id, side) {
  var mp = getMap(side);
  var suffixes = ['', '.line', '.fill', '.circle', '.a', '.b'];
  for (var i = 0; i < suffixes.length; i++) {
    var map_id = id + suffixes[i];
    if (mp.getLayer(map_id)) {
      mp.setLayoutProperty(map_id, 'visibility', 'none');
    }
  }
  hideLegend(id);
  hideLegend(id + '.a');
}

/**
 * Show the legend element associated with a layer.
 * @param {string} id - Layer identifier.
 */
export function showLegend(id) {
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.style.visibility = 'visible';
  }
}

/**
 * Hide the legend element associated with a layer.
 * @param {string} id - Layer identifier.
 */
export function hideLegend(id) {
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.style.visibility = 'hidden';
  }
}

/**
 * Close any open MapLibre popup on the map.
 */
export function closePopup() {
  var popup = document.getElementsByClassName('maplibre-popup');
  if (popup[0]) {
    popup[0].remove();
  }
}

/**
 * Retrieve the current map extent (bounding box) and send it to Python
 * via the getMapExtent bridge callback.
 */
export function getExtent() {
  var extent = mapA.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight]);
  getMapExtent();
}

/**
 * Retrieve the current map center and zoom level and send it to Python
 * via the getMapCenter bridge callback.
 */
export function getCenter() {
  var center = mapA.getCenter();
  var zoom = mapA.getZoom();
  jsonString = JSON.stringify([center["lng"], center["lat"], zoom]);
  getMapCenter();
}

/**
 * Enter "click point" mode: change the cursor to a crosshair and wait
 * for a single left-click (or right-click to cancel).
 */
export function clickPoint() {
  mapA.getCanvas().style.cursor = 'crosshair';
  window.currentCursor = 'crosshair';
  mapA.once('click', onPointClicked);
  mapA.once('contextmenu', onPointRightClicked);
}

/**
 * Set the map center to the given coordinates.
 * @param {number} lon - Longitude.
 * @param {number} lat - Latitude.
 */
export function setCenter(lon, lat) {
  mapA.setCenter([lon, lat]);
}

/**
 * Set the map zoom level.
 * @param {number} zoom - Zoom level.
 */
export function setZoom(zoom) {
  mapA.setZoom(zoom);
}

/**
 * Fit the map view to the bounding box defined by two corner coordinates.
 * @param {number} lon1 - Southwest longitude.
 * @param {number} lat1 - Southwest latitude.
 * @param {number} lon2 - Northeast longitude.
 * @param {number} lat2 - Northeast latitude.
 */
export function fitBounds(lon1, lat1, lon2, lat2) {
  mapA.fitBounds([[lon1, lat1], [lon2, lat2]]);
}

/**
 * Instantly move the map to a given position and zoom (no animation).
 * @param {number} lon  - Longitude.
 * @param {number} lat  - Latitude.
 * @param {number} zoom - Zoom level.
 */
export function jumpTo(lon, lat, zoom) {
  mapA.jumpTo({center: [lon, lat], zoom: zoom});
}

/**
 * Animate the map to a given position and zoom.
 * @param {number} lon  - Longitude.
 * @param {number} lat  - Latitude.
 * @param {number} zoom - Zoom level.
 */
export function flyTo(lon, lat, zoom) {
  mapA.flyTo({center: [lon, lat], zoom: zoom});
}

/**
 * Set the map projection (e.g. 'mercator' or 'globe'). When set to
 * 'globe', atmospheric fog and stars are enabled.
 * @param {string} projection - Projection name.
 */
export function setProjection(projection) {
  var mapDiv = document.getElementById('compare1');
  if (projection == 'globe') {
    mapDiv.style.background = '#000';
    var style = mapA.getStyle();
    style.projection = { type: 'globe' };
    style.sky = {
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 5, 1, 7, 0],
    };
    mapA.setStyle(style);
  } else {
    mapDiv.style.background = '';
    var style = mapA.getStyle();
    delete style.projection;
    delete style.sky;
    mapA.setStyle(style);
  }
}

/**
 * Switch the base map style. Called from Python.
 * @param {string} styleID - Identifier of the target style.
 */
export function setLayerStyle(styleID) {
  setMapStyle(styleID, mapA);
  setMapStyle(styleID, mapB);
  layerStyleSet();
}

/**
 * Enable or disable 3-D terrain rendering.
 * @param {boolean} trueOrFalse  - Whether to enable terrain.
 * @param {number}  exaggeration - Vertical exaggeration factor.
 */
export function setTerrain(trueOrFalse, exaggeration) {
  if (trueOrFalse) {
    mapA.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': exaggeration });
  } else {
    mapA.setTerrain();
  }
}

/**
 * Set the compare slider position.
 * @param {number} npix - Position in pixels.
 */
export function setSlider(npix) {
  map.setSlider(npix);
}

/**
 * Show a popup with an iframe at the given coordinates.
 * @param {object} options
 * @param {number} options.lon - Longitude.
 * @param {number} options.lat - Latitude.
 * @param {string} options.url - URL to load in the iframe.
 * @param {number} [options.width=520] - Popup width in pixels.
 * @param {number} [options.height=320] - Popup height in pixels.
 */
export function showPopup({lon, lat, url, width = 520, height = 320} = {}) {
  // Remove existing popup if any
  if (window._iframePopup) {
    window._iframePopup.remove();
  }
  const html = `<iframe src="${url}" style="width:${width}px;height:${height}px;border:none;"></iframe>`;
  window._iframePopup = new maplibregl.Popup({
    closeOnClick: true,
    closeButton: true,
    maxWidth: `${width + 40}px`,
  })
    .setLngLat([lon, lat])
    .setHTML(html)
    .addTo(mapA);
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Return the map object for the given side.
 * @param {string} side - "a" or "b".
 * @returns {object} The corresponding map instance.
 */
function getMap(side) {
  if (side == "a") { return mapA }
  else { return mapB }
}

/**
 * Called once mapA has finished loading. Sends the initial map extent
 * back to Python via the mapReady bridge callback.
 */
function mapLoadedA(evt) {
  var extent = mapA.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight, "a"]);
  mapReady();
}

/**
 * Called once mapB has finished loading. Sends the initial map extent
 * back to Python via the mapReady bridge callback.
 */
function mapLoadedB(evt) {
  var extent = mapB.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight, "b"]);
  mapReady();
}

/**
 * Called when mapA movement ends. Sends the new extent, center and zoom
 * back to Python via the mapMoved bridge callback.
 */
function onMoveEndA(evt) {
  if (activeSide == 'b') {return;}
  var extent = mapA.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  var center = mapA.getCenter();
  var zoom = mapA.getZoom();
  jsonString = JSON.stringify([bottomLeft, topRight, center["lng"], center["lat"], zoom]);
  mapMoved();
}

/**
 * Called when mapB movement ends. Sends the new extent, center and zoom
 * back to Python via the mapMoved bridge callback.
 */
function onMoveEndB(evt) {
  if (activeSide == 'a') {return;}
  var extent = mapB.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  var center = mapB.getCenter();
  var zoom = mapB.getZoom();
  jsonString = JSON.stringify([bottomLeft, topRight, center["lng"], center["lat"], zoom]);
  mapMoved();
}

function onPointClicked(e) {
  mapA.getCanvas().style.cursor = '';
  window.currentCursor = '';
  pointClicked(e.lngLat);
}

function onPointRightClicked(e) {
  mapA.getCanvas().style.cursor = '';
  window.currentCursor = '';
  mapA.off('click', onPointClicked);
}

function onMouseMoved(e) {
  mouseMoved(e.lngLat);
}

/**
 * Add an invisible placeholder layer used for z-ordering.
 * Background layers go before dummy_layer_0, data layers between
 * dummy_layer_0 and dummy_layer_1, draw layers after dummy_layer_1.
 * @param {object} mp - Map instance.
 * @param {string} id - Dummy layer identifier.
 */
function addDummyLayer(mp, id) {
  mp.addSource(id, {
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': []
    }
  });
  mp.addLayer({
    'id': id,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': '#000',
      'line-width': 1
    }
  });
}
