console.log('Importing MapBox Simple...');
//export let mapboxgl = mpbox.import_mapbox_gl()
mapboxgl = mpbox.import_mapbox_gl()

let mapReady;
let mapMoved;
let getMapExtent;
let getMapCenter;
export let featureDrawn;
export let featureSelected;
export let featureDeselected;
export let featureModified;
export let featureAdded;
export let jsonString;
//export let featureClicked;
export let pointClicked;
export let layerStyleSet;
//export let layerAdded;
//export let layers;

mapboxgl.accessToken = mapbox_token;

//export const map = new mapboxgl.Map({
map = new mapboxgl.Map({
  container: 'map', // container ID
//  style: 'mapbox://styles/mapbox/streets-v11', // style URL
  style: 'mapbox://styles/mapbox/light-v11', // style URL
  center: [0.0, 0.0], // starting position [lng, lat]
  zoom: 2, // starting zoom
  projection: 'mercator' // display the map as a 3D globe
});

map.scrollZoom.setWheelZoomRate(1 / 200);
//const nav = new mapboxgl.NavigationControl({
//  visualizePitch: true
//});
//map.addControl(nav, 'top-left');
//const scale = new mapboxgl.ScaleControl({
//  maxWidth: 80
//});
//map.addControl(scale, 'bottom-left');

//export const marker = new mapboxgl.Marker({draggable: true});

console.log('Adding WebChannel ...');

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapBoxSimple = channel.objects.MapBoxSimple;
  if (typeof MapBoxSimple != 'undefined') {
    mapReady          = function() { MapBoxSimple.mapReady(jsonString)};
//    mapMoved          = function() { MapBoxSimple.mapMoved(jsonString)};
//    getMapExtent      = function() { MapBoxSimple.getMapExtent(jsonString)};
//    getMapCenter      = function() { MapBoxSimple.getMapCenter(jsonString)};
//    featureClicked    = function(featureId, featureProps) { MapBox.featureClicked(featureId, JSON.stringify(featureProps))};
//    pointClicked      = function(coords) { MapBox.pointClicked(JSON.stringify(coords))};
  }
});

//layers = new Object();

map.on('load', () => {
  console.log('Mapbox loaded !');
  // Add dummy layer
  addDummyLayer();
  mapLoaded();
});

//map.on('moveend', () => {
//    onMoveEnd();
//});

//};

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
  // Remove source
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.remove();
  }

//  // What is this doing here?
//  map.off('moveend', () => {
//    const vis = map.getLayoutProperty(lineId, 'visibility');
//    if (vis == "visible") {
//      updateFeatureState(id);
//    }
//  });

}

export function setMouseDefault() {
  map.getCanvas().style.cursor = '';
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
  map.getCanvas().style.cursor = 'crosshair'
//  map.once('click', function(e) { onPointClicked(e) });
  map.once('click', onPointClicked);
  map.once('contextmenu', onPointRightClicked);
}

function onPointClicked(e) {
  map.getCanvas().style.cursor = '';
  pointClicked(e.lngLat);
}

function onPointRightClicked(e) {
  map.getCanvas().style.cursor = '';
  console.log("point right clicked");
  map.off('click', onPointClicked);
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
  var legends = document.getElementsByClassName("overlay_legend")
  if (legends) {
    for (const legend of legends) {
      legend.remove();
    }
  }
  var legends = document.getElementsByClassName("choropleth_legend")
  if (legends) {
    for (const legend of legends) {
      legend.remove();
    }
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
