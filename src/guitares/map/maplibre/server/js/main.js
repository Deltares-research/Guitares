/**
 * main.js - Core map initialization and interaction module.
 *
 * Sets up the QWebChannel bridge to Python, initializes the MapLibre GL map,
 * and exposes exported functions for map control (pan, zoom, layers, etc.).
 */

import { BackgroundLayerSelector, setMapStyle } from "./basemap_control.js";
import { RulerControl, deactivateRuler } from "./ruler_control.js";
import { TerrainControl } from "./terrain_control.js";

// ---------------------------------------------------------------------------
// Module-level state
// ---------------------------------------------------------------------------

let mapReady;
let mapMoved;
let mouseMoved;
let getMapExtent;
let getMapCenter;
let geocoderApi;
export let pong;
export let mapLibreImported;
export let jsonString;
export let pointClicked;
export let layerStyleSet;
export let marker;

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
        window.MapLibre = channel.objects.MapLibre;
        if (typeof MapLibre != 'undefined') {
          pong              = function() { MapLibre.pong("pong")};
          mapReady          = function() { MapLibre.mapReady(jsonString)};
          mapMoved          = function() { MapLibre.mapMoved(jsonString)};
          mouseMoved        = function(coords) { MapLibre.mouseMoved(JSON.stringify(coords))};
          getMapExtent      = function() { MapLibre.getMapExtent(jsonString)};
          getMapCenter      = function() { MapLibre.getMapCenter(jsonString)};
          featureClicked    = function(featureId, featureProps) { MapLibre.featureClicked(featureId, JSON.stringify(featureProps))};
          featureDrawn      = function(featureCollection, featureId, layerId) { MapLibre.featureDrawn(featureCollection, featureId, layerId)};
          featureModified   = function(featureCollection, featureId, layerId) { MapLibre.featureModified(featureCollection, featureId, layerId)};
          featureSelected   = function(featureCollection, featureId, layerId) { MapLibre.featureSelected(featureCollection, featureId, layerId)};
          featureAdded      = function(featureCollection, featureId, layerId) { MapLibre.featureAdded(featureCollection, featureId, layerId)};
          featureDeselected = function(layerId) { MapLibre.featureDeselected(layerId)};
          pointClicked      = function(coords) { MapLibre.pointClicked(JSON.stringify(coords))};
          layerStyleSet     = function() { MapLibre.layerStyleSet('')};
          layerAdded        = function(layerId) { MapLibre.layerAdded(layerId)};
          webChannelReady   = true;
        }
      });
    } catch (error) {
      console.error('WebChannel not found:', error);
    }

    // Set the geocoder API (Nominatim)
    if (!window.offline) {
      geocoderApi = {
        forwardGeocode: async (config) => {
          const features = [];
          try {
            const request =
              `https://nominatim.openstreetmap.org/search?q=${
                config.query
              }&format=geojson&polygon_geojson=1&addressdetails=1`;
            const response = await fetch(request);
            const geojson = await response.json();
            for (const feature of geojson.features) {
              const center = [
                feature.bbox[0] + (feature.bbox[2] - feature.bbox[0]) / 2,
                feature.bbox[1] + (feature.bbox[3] - feature.bbox[1]) / 2
              ];
              const point = {
                type: 'Feature',
                geometry: {
                  type: 'Point',
                  coordinates: center
                },
                place_name: feature.properties.display_name,
                properties: feature.properties,
                text: feature.properties.display_name,
                place_type: ['place'],
                center
              };
              features.push(point);
            }
          } catch (e) {
            console.error(`Failed to forwardGeocode with error: ${e}`);
          }
          return {
            features
          };
        }
      };
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
 * Create the MapLibre GL map instance, add controls (navigation, geocoder,
 * scale, ruler, background-layer selector), and wire up event handlers.
 */
export function addMap() {
  map = new maplibregl.Map({
    container: 'map',
    style: window.mapStyles[default_style],
    center: default_center,
    zoom: default_zoom,
    TerrainControl: false,
    canvasContextAttributes: { alpha: true },
    // We add a compact AttributionControl ourselves at 'bottom-left' below
    // (next to the scale bar), so disable the default bottom-right one.
    attributionControl: false,
  });

  map.scrollZoom.setWheelZoomRate(1 / 200);

  // Navigation (zoom/pitch controls)
  if (window.showZoomControl !== false) {
    const nav = new maplibregl.NavigationControl({
      visualizePitch: true
    });
    map.addControl(nav, 'top-left');
  }

  // Ruler (distance measurement)
  if (window.showRuler !== false) {
    window.rulerControl = new RulerControl();
    map.addControl(window.rulerControl, 'top-left');
  }

  // 3D Terrain toggle
  if (window.showTerrain3d !== false) {
    window.terrainControl = new TerrainControl();
    map.addControl(window.terrainControl, 'top-left');
  }

  // Globe
  if (window.showGlobe !== false) {
    var globeControl = new maplibregl.GlobeControl();
    map.addControl(globeControl, 'top-left');
    setTimeout(() => {
      var globeBtns = map.getContainer().querySelectorAll('.maplibregl-ctrl-globe');
      if (globeBtns.length > 0) {
        globeBtns[0].addEventListener('click', () => {
          setTimeout(() => {
            var proj = map.getProjection();
            var projType = (typeof proj === 'object') ? proj.type : proj;
            setProjection(projType);
          }, 100);
        });
      }
    }, 500);
  }

  // Background layer selector
  if (window.showStyleSelector !== false) {
    var backgroundLayers = [];
    for (var key in window.mapStyles) {
      backgroundLayers.push({"id": key, "name": window.mapStyles[key].name});
    }
    map.addControl(new BackgroundLayerSelector(backgroundLayers, default_style), 'top-left');
  }

  // Scale
  map.addControl(new maplibregl.ScaleControl({maxWidth: 80}), 'bottom-left');

  // Attribution — placed in the same lower-left corner as the scale bar
  // (compact so it doesn't push the legends up). MapLibre keeps the
  // compact control expanded on wide maps; force it closed on startup so
  // it shows just the (i) icon until the user clicks it.
  const attribCtl = new maplibregl.AttributionControl({compact: true});
  map.addControl(attribCtl, 'bottom-left');
  map.once('load', () => {
    const el = map.getContainer().querySelector('.maplibregl-ctrl-attrib');
    if (el) el.classList.remove('maplibregl-compact-show');
  });

  // Geocoder
  if (!offline && window.showGeocoder !== false) {
    map.addControl(new MaplibreGeocoder(geocoderApi, {maplibregl}), 'top-right');
  }

  // Draggable marker
  marker = new maplibregl.Marker({draggable: true});

  window.currentCursor = '';

  map.on('load', () => {
    addDummyLayer('dummy_layer_0');
    addDummyLayer('dummy_layer_1');
    map.addControl(draw, 'top-left');
    // Load icons
    iconUrls.forEach(async (iconUrl) => {
      try {
        const image = await map.loadImage(iconUrl);
        if (!map.hasImage(iconUrl)) {
          map.addImage(iconUrl, image.data);
        }
      } catch (e) {
        // Silently ignore icon loading errors (e.g. DOMException from duplicate adds)
      }
    });
    mapLoaded();
  });

  map.on('style.load', () => {
    // Reserved for future use (buildings, terrain source, etc.)
  });

  map.on('moveend', () => {
    onMoveEnd();
  });

  map.on('mousemove', (e) => {
    onMouseMoved(e);
  });
}

/**
 * Remove a map layer and all its sub-layers (line, fill, circle, a, b),
 * associated sources, and legend elements.
 * @param {string} id   - Base layer identifier.
 * @param {string} side - Side indicator (unused, kept for API compat).
 */
export function removeLayer(id, side) {
  var suffixes = ['', '.line', '.fill', '.circle', '.a', '.b'];
  for (var i = 0; i < suffixes.length; i++) {
    var layerId = id + suffixes[i];
    if (typeof map.getLayer(layerId) !== 'undefined') {
      map.removeLayer(layerId);
    }
  }
  // Remove sources
  var sourceSuffixes = ['', '.a', '.b'];
  for (var i = 0; i < sourceSuffixes.length; i++) {
    var sourceId = id + sourceSuffixes[i];
    if (typeof map.getSource(sourceId) !== 'undefined') {
      map.removeSource(sourceId);
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
  map.getCanvas().style.cursor = '';
  window.currentCursor = '';
  map.off('click', onPointClicked);
  deactivateRuler();
}

/**
 * Show a layer and all its sub-layers on the map, including its legend.
 * @param {string} id   - Base layer identifier.
 * @param {string} side - Side indicator (unused, kept for API compat).
 */
export function showLayer(id, side) {
  var suffixes = ['', '.line', '.fill', '.circle', '.a', '.b'];
  for (var i = 0; i < suffixes.length; i++) {
    var map_id = id + suffixes[i];
    if (map.getLayer(map_id)) {
      map.setLayoutProperty(map_id, 'visibility', 'visible');
    }
  }
  showLegend(id);
  showLegend(id + '.a');
}

/**
 * Hide a layer and all its sub-layers on the map, including its legend.
 * @param {string} id   - Base layer identifier.
 * @param {string} side - Side indicator (unused, kept for API compat).
 */
export function hideLayer(id, side) {
  var suffixes = ['', '.line', '.fill', '.circle', '.a', '.b'];
  for (var i = 0; i < suffixes.length; i++) {
    var map_id = id + suffixes[i];
    if (map.getLayer(map_id)) {
      map.setLayoutProperty(map_id, 'visibility', 'none');
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
  var extent = map.getBounds();
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
  var center = map.getCenter();
  var zoom = map.getZoom();
  jsonString = JSON.stringify([center["lng"], center["lat"], zoom]);
  getMapCenter();
}

/**
 * Enter "click point" mode: change the cursor to a crosshair and wait
 * for a single left-click (or right-click to cancel).
 */
export function clickPoint() {
  map.getCanvas().style.cursor = 'crosshair';
  window.currentCursor = 'crosshair';
  map.once('click', onPointClicked);
  map.once('contextmenu', onPointRightClicked);
}

/**
 * Set the map center to the given coordinates.
 * @param {number} lon - Longitude.
 * @param {number} lat - Latitude.
 */
export function setCenter(lon, lat) {
  map.setCenter([lon, lat]);
}

/**
 * Set the map zoom level.
 * @param {number} zoom - Zoom level.
 */
export function setZoom(zoom) {
  map.setZoom(zoom);
}

/**
 * Fit the map view to the bounding box defined by two corner coordinates.
 * @param {number} lon1 - Southwest longitude.
 * @param {number} lat1 - Southwest latitude.
 * @param {number} lon2 - Northeast longitude.
 * @param {number} lat2 - Northeast latitude.
 */
export function fitBounds(lon1, lat1, lon2, lat2) {
  map.fitBounds([[lon1, lat1], [lon2, lat2]]);
}

/**
 * Instantly move the map to a given position and zoom (no animation).
 * @param {number} lon  - Longitude.
 * @param {number} lat  - Latitude.
 * @param {number} zoom - Zoom level.
 */
export function jumpTo(lon, lat, zoom) {
  map.jumpTo({center: [lon, lat], zoom: zoom});
}

/**
 * Animate the map to a given position and zoom.
 * @param {number} lon  - Longitude.
 * @param {number} lat  - Latitude.
 * @param {number} zoom - Zoom level.
 */
export function flyTo(lon, lat, zoom) {
  map.flyTo({center: [lon, lat], zoom: zoom});
}

/**
 * Set the map projection (e.g. 'mercator' or 'globe'). When set to
 * 'globe', atmospheric fog and stars are enabled.
 * @param {string} projection - Projection name.
 */
export function setProjection(projection) {
  var mapDiv = document.getElementById('map');
  if (projection == 'globe') {
    mapDiv.style.background = '#000';
    // Must set projection + sky in the style for atmosphere to work
    var style = map.getStyle();
    style.projection = { type: 'globe' };
    style.sky = {
      'atmosphere-blend': ['interpolate', ['linear'], ['zoom'], 0, 1, 5, 1, 7, 0],
    };
    map.setStyle(style);
  } else {
    mapDiv.style.background = '';
    var style = map.getStyle();
    delete style.projection;
    delete style.sky;
    map.setStyle(style);
  }
}

/**
 * Switch the base map style. Called from Python.
 * @param {string} styleID - Identifier of the target style.
 */
export function setLayerStyle(styleID) {
  setMapStyle(styleID);
  layerStyleSet();
}

/**
 * Enable or disable 3-D terrain rendering.
 * @param {boolean} trueOrFalse  - Whether to enable terrain.
 * @param {number}  exaggeration - Vertical exaggeration factor.
 */
export function setTerrain(trueOrFalse, exaggeration) {
  if (trueOrFalse) {
    map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': exaggeration });
  } else {
    map.setTerrain();
  }
}

// ---------------------------------------------------------------------------
// Internal helpers
// ---------------------------------------------------------------------------

/**
 * Called once the map has finished loading. Sends the initial map extent
 * back to Python via the mapReady bridge callback.
 */
function mapLoaded(evt) {
  var extent = map.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight]);
  mapReady();
}

/**
 * Called when map movement ends. Sends the new extent, center and zoom
 * back to Python via the mapMoved bridge callback.
 */
function onMoveEnd(evt) {
  var extent = map.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  var center = map.getCenter();
  var zoom = map.getZoom();
  jsonString = JSON.stringify([bottomLeft, topRight, center["lng"], center["lat"], zoom]);
  mapMoved();
}

function onPointClicked(e) {
  map.getCanvas().style.cursor = '';
  window.currentCursor = '';
  pointClicked(e.lngLat);
}

function onPointRightClicked(e) {
  map.getCanvas().style.cursor = '';
  window.currentCursor = '';
  map.off('click', onPointClicked);
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
    .addTo(map);
}

function onMouseMoved(e) {
  mouseMoved(e.lngLat);
}

/**
 * Add an invisible placeholder layer used for z-ordering.
 * Background layers go before dummy_layer_0, data layers between
 * dummy_layer_0 and dummy_layer_1, draw layers after dummy_layer_1.
 * @param {string} id - Dummy layer identifier.
 */
function addDummyLayer(id) {
  map.addSource(id, {
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': []
    }
  });
  map.addLayer({
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
