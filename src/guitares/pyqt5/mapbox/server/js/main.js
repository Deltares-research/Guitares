console.log('Importing MapBox ...');
//export let mapboxgl = mpbox.import_mapbox_gl()
mapboxgl = mpbox.import_mapbox_gl()

//console.log('Importing MapBox Draw ...');
import { draw, setDrawEvents } from '/js/draw_layer.js';

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

//map = new mapboxgl.Map({
//  container: 'map', // container ID
//  style: 'mapbox://styles/mapbox/streets-v11', // style URL
////  style: 'mapbox://styles/mapbox/light-v11', // style URL
//  center: [0.0, 0.0], // starting position [lng, lat]
//  zoom: 2, // starting zoom
////  projection: 'globe' // display the map as a 3D globe
//  projection: 'mercator' // display the map as a 3D globe
//});

map = new mapboxgl.Map({
  container: 'map', // container ID
  style: default_style, // style URL
  center: default_center, // starting position [lng, lat]
  zoom: default_zoom, // starting zoom
  projection: default_projection // display the map as a 3D globe
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

console.log('Adding WebChannel ...');

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapBox = channel.objects.MapBox;
  if (typeof MapBox != 'undefined') {
    mapReady          = function() { MapBox.mapReady(jsonString)};
    mapMoved          = function() { MapBox.mapMoved(jsonString)};
    getMapExtent      = function() { MapBox.getMapExtent(jsonString)};
    getMapCenter      = function() { MapBox.getMapCenter(jsonString)};
    featureClicked    = function(featureId, featureProps) { MapBox.featureClicked(featureId, JSON.stringify(featureProps))};
    featureDrawn      = function(featureCollection, featureId, layerId) { MapBox.featureDrawn(featureCollection, featureId, layerId)};
    featureModified   = function(featureCollection, featureId, layerId) { MapBox.featureModified(featureCollection, featureId, layerId)};
    featureSelected   = function(featureCollection, featureId, layerId) { MapBox.featureSelected(featureCollection, featureId, layerId)};
    featureAdded      = function(featureCollection, featureId, layerId) { MapBox.featureAdded(featureCollection, featureId, layerId)};
    featureDeselected = function(layerId) { MapBox.featureDeselected(layerId)};
    pointClicked      = function(coords) { MapBox.pointClicked(JSON.stringify(coords))};
    layerStyleSet     = function() { MapBox.layerStyleSet('')};
    layerAdded        = function(layerId) { MapBox.layerAdded(layerId)};
  }
});

layers = new Object();

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
  const labelLayer = layers.find(
    (layer) => layer.type === 'symbol' && layer.layout['text-field']
  );

  if (!labelLayer) {
    console.log('No label layer with id found with text-field property');
  } else {
    const labelLayerId = labelLayer.id;  
    // The 'building' layer in the Mapbox Streets
    // vector tileset contains building height data
    // from OpenStreetMap.
    //  console.log('Adding 3d buildings')
    map.addLayer({
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
    }, labelLayerId);
  }

  // Add additional layers
  
});

map.on('moveend', () => {
    onMoveEnd();
});

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

// styleID should be in the form "satellite-v9"
export function setLayerStyle(styleID) {
  fetch(`https://api.mapbox.com/styles/v1/mapbox/${styleID}?access_token=${mapboxgl.accessToken}`)
    .then(response => response.json())
    .then(newStyle => {
      const currentStyle = map.getStyle();
      // ensure any sources from the current style are copied across to the new style
      newStyle.sources = Object.assign(
        {},
        currentStyle.sources,
        newStyle.sources
      );

      // find the index of where to insert our layers to retain in the new style
      let labelIndex = newStyle.layers.findIndex((el) => {
        return el.id == 'waterway-label';
      });

      // default to on top
      if (labelIndex === -1) {
        labelIndex = newStyle.layers.length;
      }
      const appLayers = currentStyle.layers.filter((el) => {
        // app layers are the layers to retain, and these are any layers which have a different source set
        return (
          el.source &&
          el.source != 'mapbox://mapbox.satellite' &&
          el.source != 'mapbox' &&
          el.source != 'composite'
        );
      });
      newStyle.layers = [
        ...newStyle.layers.slice(0, labelIndex),
        ...appLayers,
        ...newStyle.layers.slice(labelIndex, -1),
      ];
      map.setStyle(newStyle);
      layerStyleSet();
    })
    .catch(error => {
      console.error(`Error fetching style: ${error.message}`);
    });
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
