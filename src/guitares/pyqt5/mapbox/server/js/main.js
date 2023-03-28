export let mapboxgl = mpbox.import_mapbox_gl()

import { draw, setDrawEvents } from '/js/draw.js';

let mapReady;
let mapMoved;
let getMapExtent;
export let featureDrawn;
export let featureSelected;
export let featureModified;
export let jsonString;
export let featureClicked;
export let pointClicked;
export let layerStyleSet;

console.log('Adding MapBox map ...')

mapboxgl.accessToken = mapbox_token;

export const map = new mapboxgl.Map({
  container: 'map', // container ID
  style: 'mapbox://styles/mapbox/streets-v11', // style URL
//  style: 'mapbox://styles/mapbox/light-v11', // style URL
  center: [0.0, 0.0], // starting position [lng, lat]
  zoom: 2, // starting zoom
//  projection: 'globe' // display the map as a 3D globe
  projection: 'mercator' // display the map as a 3D globe
});

map.scrollZoom.setWheelZoomRate(1 / 200);

const nav = new mapboxgl.NavigationControl({
  visualizePitch: true
});
map.addControl(nav, 'top-left');

const scale = new mapboxgl.ScaleControl({
  maxWidth: 80
});
map.addControl(scale, 'bottom-left');

export const marker = new mapboxgl.Marker({draggable: true});

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapBox = channel.objects.MapBox;
  if (typeof MapBox != 'undefined') {
    mapReady          = function() { MapBox.mapReady(jsonString)};
    mapMoved          = function() { MapBox.mapMoved(jsonString)};
    getMapExtent      = function() { MapBox.getMapExtent(jsonString)};
    featureClicked    = function(featureId, featureProps) { MapBox.featureClicked(featureId, JSON.stringify(featureProps))};
    featureDrawn      = function(featureCollection, featureId) { MapBox.featureDrawn(featureCollection, featureId)};
    featureModified   = function(featureCollection, featureId) { MapBox.featureModified(featureCollection, featureId)};
    featureSelected   = function(featureCollection, featureId) { MapBox.featureSelected(featureCollection, featureId)};
    pointClicked      = function(coords) { MapBox.pointClicked(JSON.stringify(coords))};
    layerStyleSet     = function() { MapBox.layerStyleSet('')};
  }
});


map.on('load', () => {
  console.log('Mapbox loaded !');
  // Add dummy layer
  addDummyLayer();
  map.addControl(draw, 'top-left');
  mapLoaded();
});

map.on('style.load', () => {
  map.setFog({}); // Set the default atmosphere style
  // Add terrain
  map.addSource('mapbox-dem', {
    'type': 'raster-dem',
    'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
    'tileSize': 512,
    'maxzoom': 14
  });

  const layers = map.getStyle().layers;
  const labelLayerId = layers.find(
      (layer) => layer.type === 'symbol' && layer.layout['text-field']
  ).id;

  // The 'building' layer in the Mapbox Streets
  // vector tileset contains building height data
  // from OpenStreetMap.
  console.log('Adding 3d buildings')
  map.addLayer(
      {
          'id': 'add-3d-buildings',
          'source': 'composite',
          'source-layer': 'building',
          'filter': ['==', 'extrude', 'true'],
          'type': 'fill-extrusion',
          'minzoom': 15,
          'paint': {
              'fill-extrusion-color': '#aaa',

              // Use an 'interpolate' expression to
              // add a smooth transition effect to
              // the buildings as the user zooms in.
              'fill-extrusion-height': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  15,
                  0,
                  15.05,
                  ['get', 'height']
              ],
              'fill-extrusion-base': [
                  'interpolate',
                  ['linear'],
                  ['zoom'],
                  15,
                  0,
                  15.05,
                  ['get', 'min_height']
              ],
              'fill-extrusion-opacity': 0.6
          }
      },
      labelLayerId
  );

});

map.on('moveend', () => {
    onMoveEnd();
});


function mapLoaded(evt) {
  // Get the map extents and tell Python Mapbox object that we're ready
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
    jsonString = JSON.stringify([bottomLeft, topRight]);
    mapMoved();
}



export function removeLayer(id) {
  // Remove layer
  var mapLayer = map.getLayer(id);
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer & source.
    map.removeLayer(id);
  }
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.remove();
  }
}

export function showLayer(id) {
	// Show layer
	if (map.getLayer(id)) {
    map.setLayoutProperty(id, 'visibility', 'visible');
  }
}

export function hideLayer(id) {
	// Show layer
	if (map.getLayer(id)) {
  	map.setLayoutProperty(id, 'visibility', 'none');
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

export function clickPoint() {
  map.getCanvas().style.cursor = 'crosshair'
  map.once('click', function(e) {
    var coordinates = e.lngLat;
    onPointClicked(coordinates);
  });
}

function onPointClicked(coordinates) {
  map.getCanvas().style.cursor = '';
  pointClicked(coordinates);
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
	// Called after moving map ended
	// Get new map extents
	map.setProjection(projection);
}

export function setLayerStyle(style) {
  map.setStyle('mapbox://styles/mapbox/' + style);
  map.once('idle', () => { addDummyLayer(); layerStyleSet(); });
}

export function setTerrain(trueOrFalse, exaggeration) {
  if (trueOrFalse) {
    map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': exaggeration });
  } else {
    map.setTerrain();
  }
}

function addDummyLayer() {
  // Add a dummy layer (other layer will be added BEFORE this dummy layer)
  var id = 'dummy_layer';
  map.addSource(id, {
    'type': 'geojson'
  });
  map.addLayer({
    'id': 'dummy_layer',
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': '#000',
      'line-width': 1
    }
  });
}
