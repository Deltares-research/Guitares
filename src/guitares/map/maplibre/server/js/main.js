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
import { BackgroundLayerSelector, setMapStyle } from "./basemap_control.js";
let webChannelReady = false;
let firstPong = true;

console.log("Waiting for QWebChannel...");

waitForQWebChannel()

  .then(() => {
    // Now it's safe to use QWebChannel
    console.log("QWebChannel loaded successfully");
      
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
        }
      });
  
    } catch (error) {
      console.log(error)
      console.log('WebChannel not found');
    }
  
    // Set the geocoder API
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
                      feature.bbox[0] +
                  (feature.bbox[2] - feature.bbox[0]) / 2,
                      feature.bbox[1] +
                  (feature.bbox[3] - feature.bbox[1]) / 2
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
    };
  
    webChannelReady = true;

  })

.catch((err) => {
    console.error("Error loading QWebChannel:", err);
    console.error(err);
});

// Done in main.js

export function ping(ping_string) {
  //console.log("Ping from Python: " + ping_string);
  if (webChannelReady && firstPong) {
    firstPong = false;
    pong();
  }
}

export function addMap() {
    
  map = new maplibregl.Map({
    container: 'map', // container ID
    style: window.mapStyles[default_style],
    center: default_center, // starting position [lng, lat]
    zoom: default_zoom, // starting zoom
    projection: default_projection, // display the map as a 3D globe or flat
    TerrainControl: false,
  });
    
  map.scrollZoom.setWheelZoomRate(1 / 200);

  // Add controls

  // Navigation
  const nav = new maplibregl.NavigationControl({
    visualizePitch: true
  });
  map.addControl(nav, 'top-left');

  // Background layer
  var backgroundLayers = [];
  for (var key in window.mapStyles) {
    backgroundLayers.push({"id": key, "name": window.mapStyles[key].name});
  }  
  map.addControl(new BackgroundLayerSelector(backgroundLayers, default_style), 'top-left');

  // Scale
  map.addControl(new maplibregl.ScaleControl({maxWidth: 80}), 'bottom-left');

  // // Terrain (turn this off for now, need to add user-defined maptiler api key first)
  // map.addControl(
  //   new maplibregl.TerrainControl({
  //       source: 'terrain-source',
  //       exaggeration: 1.5
  //   }, 'top-left')
  // );

  // // Globe (turn off for now)
  // map.addControl(new maplibregl.GlobeControl(), 'top-left');

  // Geocoder
  if (!offline) {
    map.addControl(new MaplibreGeocoder(geocoderApi, {maplibregl}), 'top-right');
  };
    
  // Marker (why is this again?) 
  marker = new maplibregl.Marker({draggable: true});

  currentCursor = '';

  map.on('load', () => {
    // Add dummy layer
    console.log('MapLibre loaded in main.js ...');
    addDummyLayer('dummy_layer_0');
    addDummyLayer('dummy_layer_1');
    map.addControl(draw, 'top-left');
    // Load icons
    iconUrls.forEach(async (iconUrl) => {
      var image = await map.loadImage(iconUrl);
      map.addImage(iconUrl, image.data);
    });
    mapLoaded();
  });

  map.on('style.load', () => {

    // Add buildings?

    // Add globe?
  
    // // Add terrain source (by default, terrain is not shown)
    // // Turn off for now until we get a maptiler api key
    // map.addSource("terrain-source", {
    //   type: 'raster-dem',            
    //   url: "https://api.maptiler.com/tiles/terrain-rgb-v2/tiles.json?key=YdqpdVH0dDnoeOw2q3D3",
    //   tileSize: 256
    // });

  });

  map.on('moveend', () => {
    onMoveEnd();
  });

  map.on('mousemove', (e) => {
    onMouseMoved(e);
  });

}

function mapLoaded(evt) {
  // Get the map extents and tell Python MapLibre object that we're ready
  var extent = map.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight]);
  mapReady();
}

function onMoveEnd(evt) {
	// Called after moving map ended
	// Get new map extents
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

export function removeLayer(id, side) {
  // Remove the layer, source and legend etc.
  // Remove layer
  var mapLayer = map.getLayer(id);
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    map.removeLayer(id);
  }
  var mapLayer = map.getLayer(id + '.line');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    map.removeLayer(id + '.line');
  }
  var mapLayer = map.getLayer(id + '.fill');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    map.removeLayer(id + '.fill');
  }
  var mapLayer = map.getLayer(id + '.circle');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    map.removeLayer(id + '.circle');
  }
  var mapLayer = map.getLayer(id + '.a');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    map.removeLayer(id + '.a');
  }
  var mapLayer = map.getLayer(id + '.b');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    map.removeLayer(id + '.b');
  }
  // Remove source
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  var mapSource = map.getSource(id + '.a');
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id + '.a');
  }
  var mapSource = map.getSource(id + '.b');
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id + '.b');
  }
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.remove();
  }
}

export function setMouseDefault() {
  map.getCanvas().style.cursor = '';
  currentCursor = '';
  map.off('click', onPointClicked);
}

export function showLayer(id, side) {
	// Show layer
	if (map.getLayer(id)) {
    map.setLayoutProperty(id, 'visibility', 'visible');
  }
  var map_id = id + '.line'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'visible');
  }
  var map_id = id + '.fill'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'visible');
  }
  var map_id = id + '.circle'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'visible');
  }
  var map_id = id + '.a'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'visible');
  }
  var map_id = id + '.b'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'visible');
  }
  showLegend(id);
}

export function hideLayer(id, side) {
	// Hide layer
	if (map.getLayer(id)) {
  	map.setLayoutProperty(id, 'visibility', 'none');
  }
  var map_id = id + '.line'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'none');
  }
  var map_id = id + '.fill'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'none');
  }
  var map_id = id + '.circle'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'none');
  }
  var map_id = id + '.a'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'none');
  }
  var map_id = id + '.b'
	if (map.getLayer(map_id)) {
  	map.setLayoutProperty(map_id, 'visibility', 'none');
  }
  hideLegend(id);
}

export function showLegend(id) {
	// Show legend
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.style.visibility = 'visible';
  }
}

export function hideLegend(id) {
	// Hide layer
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.style.visibility = 'hidden';
  }
}

export function closePopup() {
  var popup = document.getElementsByClassName('maplibre-popup');
  // if popup is defined, remove it
  if (popup[0]) {
    popup[0].remove();
  }
}

export function getExtent() {
	// Called after moving map ended
	// Get new map extents
    var extent = map.getBounds();
    var sw = extent.getSouthWest();
    var ne = extent.getNorthEast();
    var bottomLeft = [sw["lng"], sw["lat"]];
    var topRight   = [ne["lng"], ne["lat"]];
    jsonString = JSON.stringify([bottomLeft, topRight]);
    getMapExtent();
}

export function getCenter() {
  var center = map.getCenter();
  var zoom = map.getZoom();
  jsonString = JSON.stringify([center["lng"], center["lat"], zoom]);
  getMapCenter();
}

export function clickPoint() {
  map.getCanvas().style.cursor = 'crosshair';
  currentCursor = 'crosshair';
  map.once('click', onPointClicked);
  map.once('contextmenu', onPointRightClicked);
}

function onPointClicked(e) {
  map.getCanvas().style.cursor = '';
  currentCursor = '';
  pointClicked(e.lngLat);
}

function onPointRightClicked(e) {
  map.getCanvas().style.cursor = '';
  currentCursor = '';
  map.off('click', onPointClicked);
}

function onMouseMoved(e) {
  mouseMoved(e.lngLat);
}

export function setCenter(lon, lat) {
	// Called after moving map ended
	// Get new map extents
	map.setCenter([lon, lat]);
}

export function setZoom(zoom) {
	// Called after moving map ended
	// Get new map extents
	map.setZoom(zoom);
}

export function fitBounds(lon1, lat1, lon2, lat2) {
  // Fit bounds of map using southwest and northeast corner coordinates
	map.fitBounds([[lon1, lat1], [lon2, lat2]])
}

export function jumpTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	map.jumpTo({center: [lon, lat], zoom: zoom});
}

export function flyTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	map.flyTo({center: [lon, lat], zoom: zoom});
}

export function setProjection(projection) {
	map.setProjection(projection);
  if (projection == 'globe') {
    map.setFog({
      color: 'rgb(186, 210, 235)', // Lower atmosphere
      'high-color': 'rgb(36, 92, 223)', // Upper atmosphere
      'horizon-blend': 0.02, // Atmosphere thickness (default 0.2 at low zooms)
      'space-color': 'rgb(11, 11, 25)', // Background color
      'star-intensity': 0.6 // Background star brightness (default 0.35 at low zoooms )
    });
  }
}

export function setLayerStyle(styleID) {
  // function called by python
  setMapStyle(styleID);
  layerStyleSet();
}

export function setTerrain(trueOrFalse, exaggeration) {
  if (trueOrFalse) {
    map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': exaggeration });
  } else {
    map.setTerrain();
  }
}

function addDummyLayer(id) {
  // Add dummy layer
  // Background layers will be added before dummy_layer_0
  // Data layers will be added between dummy_layer_0 and dummy_layer_1
  // Draw layers will be added after dummy_layer_1
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
