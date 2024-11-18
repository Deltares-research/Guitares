console.log("Adding Mapbox Compare Map ...")

//var mapboxgl = mpbox.import_mapbox_gl()

//let mapboxgl = mpbox.import_mapbox_gl()
//console.log('mapvars mapMain = ' + mapMain)
//console.log('mapvars mapA = ' + mapA)
//console.log('mapvars mapB = ' + mapB)

export let jsonString;
export let mapReady;
export let mapMoved;
export let activeSide = 'a';

mapboxgl.accessToken = mapbox_token;

mapA = new mapboxgl.Map({
  container: 'compare1',
  // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
  style: default_compare_style, // style URL
  center: default_compare_center, // starting position [lng, lat]
  zoom: default_compare_zoom, // starting zoom
  projection: default_compare_projection // display the map as a 3D globe
});
   
mapB = new mapboxgl.Map({
    container: 'compare2',
    style: default_compare_style, // style URL
    center: default_compare_center, // starting position [lng, lat]
    zoom: default_compare_zoom, // starting zoom
    projection: default_compare_projection // display the map as a 3D globe
    }
);

// A selector or reference to HTML element
const container = '#comparison-container';

var mapContainer = new mapboxgl.Compare(mapA, mapB, container, {
  //main_map.style.display = 'none';
  // Set this to enable comparing two maps by mouse movement:
  // mousemove: true
});


// var id = 'dummy_layer';
// mapA.addSource(id, {
//   'type': 'geojson'
// });
// mapA.addLayer({
//   'id': 'dummy_layer',
//   'type': 'line',
//   'source': id,
//   'layout': {},
//   'paint': {
//     'line-color': '#000',
//     'line-width': 1
//   }
// });
// mapB.addSource(id, {
//   'type': 'geojson'
// });
// mapB.addLayer({
//   'id': 'dummy_layer',
//   'type': 'line',
//   'source': id,
//   'layout': {},
//   'paint': {
//     'line-color': '#000',
//     'line-width': 1
//   }
// });

//mapA = mapA;
//mapB = mapB;

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapBoxCompare = channel.objects.MapBoxCompare;
  if (typeof MapBoxCompare != 'undefined') {
    mapReady = function() { MapBoxCompare.mapReady(jsonString)};
    mapMoved = function() { MapBoxCompare.mapMoved(jsonString)};
  }
});

//function carryOn() {



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

mapA.on('load', () => {
  console.log('Mapbox A loaded !');
    // Add dummy layer
    addDummyLayer(mapA);
    mapLoadedA();
});

mapB.on('load', () => {
  console.log('Mapbox B loaded !');
  // Add dummy layer
  addDummyLayer(mapB);
  mapLoadedB();
});

function addDummyLayer(mp) {
  // Add a dummy layer (other layer will be added BEFORE this dummy layer)
  var id = 'dummy_layer';
  mp.addSource(id, {
    'type': 'geojson'
  });
  mp.addLayer({
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

function mapLoadedA(evt) {
  // Get the map extents and tell Python Mapbox object that we're ready
  var extent = mapA.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight, "a"]);
  mapReady();
}

function mapLoadedB(evt) {
  // Get the map extents and tell Python Mapbox object that we're ready
  var extent = mapB.getBounds();
  var sw = extent.getSouthWest();
  var ne = extent.getNorthEast();
  var bottomLeft = [sw["lng"], sw["lat"]];
  var topRight   = [ne["lng"], ne["lat"]];
  jsonString = JSON.stringify([bottomLeft, topRight, "b"]);
  mapReady();
}
  
function onMoveEndA(evt) {
  // Called after moving map ended
  // Get new map extents
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

function onMoveEndB(evt) {
  // Called after moving map ended
  // Get new map extents
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

export function jumpTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	mapA.jumpTo({center: [lon, lat], zoom: zoom});
}

export function flyTo(lon, lat, zoom) {
	// Called after moving map ended
	// Get new map extents
	mapA.flyTo({center: [lon, lat], zoom: zoom});
}

export function setSlider(npix) {
	map.setSlider(npix);
}

export function removeLayer(id, side) {
  var mp = getMap(side);  
  // Remove the layer, source and legend etc.
  // Remove layer
  var mapLayer = mp.getLayer(id);
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    mp.removeLayer(id);
  }
  // Remove line layer
  var mapLayer = mp.getLayer(id + '.line');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    mp.removeLayer(id + '.line');
  }
  // Remove fill layer
  var mapLayer = mp.getLayer(id + '.fill');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    mp.removeLayer(id + '.fill');
  }
  // Remove circle layer
  var mapLayer = mp.getLayer(id + '.circle');
  if(typeof mapLayer !== 'undefined') {
    // Remove map layer
    mp.removeLayer(id + '.circle');
  }
  // Remove source
  var mapSource = mp.getSource(id);
  if(typeof mapSource !== 'undefined') {
    mp.removeSource(id);
  }
  // Remove legend
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.remove();
  }
}

export function showLayer(id, side) {
	// Show layer
  var mp = getMap(side);  
	if (mp.getLayer(id)) {
    mp.setLayoutProperty(id, 'visibility', 'visible');
  }
	if (mp.getLayer(id + '.line')) {
    mp.setLayoutProperty(id + '.line', 'visibility', 'visible');
  }
	if (mp.getLayer(id + '.fill')) {
    mp.setLayoutProperty(id + '.fill', 'visibility', 'visible');
  }
	if (mp.getLayer(id + '.circle')) {
    mp.setLayoutProperty(id + '.circle', 'visibility', 'visible');
  }
  showLegend(id);
}

export function hideLayer(id, side) {
	// Hide layer
  var mp = getMap(side);  
	if (mp.getLayer(id)) {
  	mp.setLayoutProperty(id, 'visibility', 'none');
  }
	if (mp.getLayer(id + '.line')) {
    mp.setLayoutProperty(id + '.line', 'visibility', 'none');
  }
	if (mp.getLayer(id + '.fill')) {
    mp.setLayoutProperty(id + '.fill', 'visibility', 'none');
  }
	if (mp.getLayer(id + '.circle')) {
    mp.setLayoutProperty(id + '.circle', 'visibility', 'none');
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


function getMap(side) {
  if (side == "a") { return mapA }
  else { return mapB }
}

// export let mapboxgl = mpbox.import_mapbox_gl()

// import { draw, setDrawEvents } from '/js/draw.js';

// let mapReady;
// let mapMoved;
// let getMapExtent;
// export let featureDrawn;
// export let featureSelected;
// export let featureDeselected;
// export let featureModified;
// export let featureAdded;
// export let jsonString;
// export let featureClicked;
// export let pointClicked;
// export let layerStyleSet;
// export let layers;



// console.log('Adding MapBox map ...')

// mapboxgl.accessToken = mapbox_token;

// export const map = new mapboxgl.Map({
//   container: 'map', // container ID
//   style: 'mapbox://styles/mapbox/streets-v11', // style URL
// //  style: 'mapbox://styles/mapbox/light-v11', // style URL
//   center: [0.0, 0.0], // starting position [lng, lat]
//   zoom: 2, // starting zoom
// //  projection: 'globe' // display the map as a 3D globe
//   projection: 'mercator' // display the map as a 3D globe
// });

// map.scrollZoom.setWheelZoomRate(1 / 200);

// const nav = new mapboxgl.NavigationControl({
//   visualizePitch: true
// });
// map.addControl(nav, 'top-left');

// const scale = new mapboxgl.ScaleControl({
//   maxWidth: 80
// });
// map.addControl(scale, 'bottom-left');

// export const marker = new mapboxgl.Marker({draggable: true});

// // Web Channel
// new QWebChannel(qt.webChannelTransport, function (channel) {
//   window.MapBox = channel.objects.MapBox;
//   if (typeof MapBox != 'undefined') {
//     mapReady          = function() { MapBox.mapReady(jsonString)};
//     mapMoved          = function() { MapBox.mapMoved(jsonString)};
//     getMapExtent      = function() { MapBox.getMapExtent(jsonString)};
//     featureClicked    = function(featureId, featureProps) { MapBox.featureClicked(featureId, JSON.stringify(featureProps))};
//     featureDrawn      = function(featureCollection, featureId, layerId) { MapBox.featureDrawn(featureCollection, featureId, layerId)};
//     featureModified   = function(featureCollection, featureId, layerId) { MapBox.featureModified(featureCollection, featureId, layerId)};
//     featureSelected   = function(featureCollection, featureId, layerId) { MapBox.featureSelected(featureCollection, featureId, layerId)};
//     featureAdded      = function(featureCollection, featureId, layerId) { MapBox.featureAdded(featureCollection, featureId, layerId)};
//     featureDeselected = function(layerId) { MapBox.featureDeselected(layerId)};
//     pointClicked      = function(coords) { MapBox.pointClicked(JSON.stringify(coords))};
//     layerStyleSet     = function() { MapBox.layerStyleSet('')};
//   }
// });

// layers = new Object();

// map.on('load', () => {
//   console.log('Mapbox loaded !');
//   // Add dummy layer
//   addDummyLayer();
//   map.addControl(draw, 'top-left');
//   mapLoaded();
// });

// map.on('style.load', () => {
//   map.setFog({}); // Set the default atmosphere style
//   // Add terrain
//   map.addSource('mapbox-dem', {
//     'type': 'raster-dem',
//     'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
//     'tileSize': 512,
//     'maxzoom': 14
//   });

//   const layers = map.getStyle().layers;
//   const labelLayerId = layers.find(
//       (layer) => layer.type === 'symbol' && layer.layout['text-field']
//   ).id;

//   // The 'building' layer in the Mapbox Streets
//   // vector tileset contains building height data
//   // from OpenStreetMap.
//   console.log('Adding 3d buildings')
//   map.addLayer(
//       {
//           'id': 'add-3d-buildings',
//           'source': 'composite',
//           'source-layer': 'building',
//           'filter': ['==', 'extrude', 'true'],
//           'type': 'fill-extrusion',
//           'minzoom': 15,
//           'paint': {
//               'fill-extrusion-color': '#aaa',

//               // Use an 'interpolate' expression to
//               // add a smooth transition effect to
//               // the buildings as the user zooms in.
//               'fill-extrusion-height': [
//                   'interpolate',
//                   ['linear'],
//                   ['zoom'],
//                   15,
//                   0,
//                   15.05,
//                   ['get', 'height']
//               ],
//               'fill-extrusion-base': [
//                   'interpolate',
//                   ['linear'],
//                   ['zoom'],
//                   15,
//                   0,
//                   15.05,
//                   ['get', 'min_height']
//               ],
//               'fill-extrusion-opacity': 0.6
//           }
//       },
//       labelLayerId
//   );

// });

// map.on('moveend', () => {
//     onMoveEnd();
// });


// function mapLoaded(evt) {
//   // Get the map extents and tell Python Mapbox object that we're ready
//   var extent = map.getBounds();
//   var sw = extent.getSouthWest();
//   var ne = extent.getNorthEast();
//   var bottomLeft = [sw["lng"], sw["lat"]];
//   var topRight   = [ne["lng"], ne["lat"]];
//   jsonString = JSON.stringify([bottomLeft, topRight]);
//   mapReady();
// }


// function onMoveEnd(evt) {
// 	// Called after moving map ended
// 	// Get new map extents
//     var extent = map.getBounds();
//     var sw = extent.getSouthWest();
//     var ne = extent.getNorthEast();
//     var bottomLeft = [sw["lng"], sw["lat"]];
//     var topRight   = [ne["lng"], ne["lat"]];
//     jsonString = JSON.stringify([bottomLeft, topRight]);
//     mapMoved();
// }



// export function removeLayer(id) {

//   // Remove layer
//   var mapLayer = map.getLayer(id);
//   if(typeof mapLayer !== 'undefined') {
//     // Remove map layer
//     console.log('removing ' + id)
//     map.removeLayer(id);
//   }

//   var mapLayer = map.getLayer(id + '.line');
//   if(typeof mapLayer !== 'undefined') {
//     // Remove map layer
//     console.log('removing ' + id + '.line')
//     map.removeLayer(id + '.line');
//     console.log('done removing ' + id + '.line')
//   }

//   var mapLayer = map.getLayer(id + '.fill');
//   if(typeof mapLayer !== 'undefined') {
//     // Remove map layer
//     console.log('removing ' + id + '.fill')
//     map.removeLayer(id + '.line');
//     console.log('done removing ' + id + '.fill')
//   }

//   var mapLayer = map.getLayer(id + '.circle');
//   if(typeof mapLayer !== 'undefined') {
//     // Remove map layer
//     console.log('removing ' + id + '.circle')
//     map.removeLayer(id + '.circle');
//   }

//   // Remove source
//   var mapSource = map.getSource(id);
//   if(typeof mapSource !== 'undefined') {
//     console.log('removing source ' + id)
//     map.removeSource(id);
//   }

//   var legend = document.getElementById("legend" + id);
//   if (legend) {
//     legend.remove();
//   }

//   map.off('moveend', () => {
//     const vis = map.getLayoutProperty(lineId, 'visibility');
//     if (vis == "visible") {
//       updateFeatureState(id);
//     }
//   });

// }

// export function showLayer(id) {
// 	// Show layer
// 	if (map.getLayer(id)) {
//     map.setLayoutProperty(id, 'visibility', 'visible');
//     var legend = document.getElementById("legend" + id);
//     if (legend) {
//       legend.style.visibility = 'visible';
//     }  
//   }
// }

// export function hideLayer(id) {
// 	// Hide layer
// 	if (map.getLayer(id)) {
//   	map.setLayoutProperty(id, 'visibility', 'none');
//     var legend = document.getElementById("legend" + id);
//     if (legend) {
//       legend.style.visibility = 'hidden';
//     }  
//   }
// }

// export function getExtent() {
// 	// Called after moving map ended
// 	// Get new map extents
//     var extent = map.getBounds();
//     var sw = extent.getSouthWest();
//     var ne = extent.getNorthEast();
//     var bottomLeft = [sw["lng"], sw["lat"]];
//     var topRight   = [ne["lng"], ne["lat"]];
//     jsonString = JSON.stringify([bottomLeft, topRight]);
//     getMapExtent();
// }

// export function clickPoint() {
//   map.getCanvas().style.cursor = 'crosshair'
//   map.once('click', function(e) {
//     var coordinates = e.lngLat;
//     onPointClicked(coordinates);
//   });
// }

// function onPointClicked(coordinates) {
//   map.getCanvas().style.cursor = '';
//   pointClicked(coordinates);
// }

// export function setCenter(lon, lat) {
// 	// Called after moving map ended
// 	// Get new map extents
// 	map.setCenter([lon, lat]);
// }

// export function setZoom(zoom) {
// 	// Called after moving map ended
// 	// Get new map extents
// 	map.setZoom(zoom);
// }

// export function fitBounds(lon1, lat1, lon2, lat2) {
//   // Fit bounds of map using southwest and northeast corner coordinates
// 	map.fitBounds([[lon1, lat1], [lon2, lat2]])
// }

// export function jumpTo(lon, lat, zoom) {
// 	// Called after moving map ended
// 	// Get new map extents
// 	map.jumpTo({center: [lon, lat], zoom: zoom});
// }

// export function flyTo(lon, lat, zoom) {
// 	// Called after moving map ended
// 	// Get new map extents
// 	map.flyTo({center: [lon, lat], zoom: zoom});
// }

// export function setProjection(projection) {
// 	// Called after moving map ended
// 	// Get new map extents
// 	map.setProjection(projection);
// }

// export function setLayerStyle(style) {
//   map.setStyle('mapbox://styles/mapbox/' + style);
//   map.once('idle', () => { addDummyLayer(); layerStyleSet(); });
//   var legends = document.getElementsByClassName("overlay_legend")
//   if (legends) {
//     for (const legend of legends) {
//       legend.remove();
//     }
//   }
// }

// export function setTerrain(trueOrFalse, exaggeration) {
//   if (trueOrFalse) {
//     map.setTerrain({ 'source': 'mapbox-dem', 'exaggeration': exaggeration });
//   } else {
//     map.setTerrain();
//   }
// }

// function addDummyLayer() {
//   // Add a dummy layer (other layer will be added BEFORE this dummy layer)
//   var id = 'dummy_layer';
//   map.addSource(id, {
//     'type': 'geojson'
//   });
//   map.addLayer({
//     'id': 'dummy_layer',
//     'type': 'line',
//     'source': id,
//     'layout': {},
//     'paint': {
//       'line-color': '#000',
//       'line-width': 1
//     }
//   });
// }

// export function compare() {

//   console.log("Comparing ...")

//   var main_map = document.getElementById("map");
//   main_map.style.display = 'none';

//   const mapA = new mapboxgl.Map({
//     container: 'compare1',
//     // Choose from Mapbox's core styles, or make your own style with Mapbox Studio
//     style: 'mapbox://styles/mapbox/light-v11',
//     center: [0, 0],
//     zoom: 0
//   });
     
//   const mapB = new mapboxgl.Map({
//     container: 'compare2',
//     style: 'mapbox://styles/mapbox/dark-v11',
//     center: [0, 0],
//     zoom: 0
//   });
     
//   // A selector or reference to HTML element
//   const container = '#comparison-container';
     
//   const map = new mapboxgl.Compare(mapA, mapB, container, {
//   // Set this to enable comparing two maps by mouse movement:
//   // mousemove: true
//   });


// }
