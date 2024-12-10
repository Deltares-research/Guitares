let mapReady;
let mapMoved;
let getMapExtent;
let getMapCenter;
let geocoderApi;
export let pong;
export let mapLibreImported;
export let featureDrawn;
export let featureSelected;
export let featureDeselected;
export let featureModified;
export let featureAdded;
export let jsonString;
export let pointClicked;
export let layerStyleSet;
export let marker;

// Web Channel
new QWebChannel(qt.webChannelTransport, function (channel) {
  window.MapLibre = channel.objects.MapLibre;
  if (typeof MapLibre != 'undefined') {
    pong              = function() { MapLibre.pong("pong")};
    mapReady          = function() { MapLibre.mapReady(jsonString)};
    mapMoved          = function() { MapLibre.mapMoved(jsonString)};
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

if (!offline) {
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

export function ping(ping_string) {
  pong();
}

export function addMap() {
  map = new maplibregl.Map({
    container: 'map', // container ID
    style: mapStyles[default_style],
    center: default_center, // starting position [lng, lat]
    zoom: default_zoom, // starting zoom
    projection: default_projection // display the map as a 3D globe or flat
  });

  map.scrollZoom.setWheelZoomRate(1 / 200);
  const nav = new maplibregl.NavigationControl({
    visualizePitch: true
  });
  map.addControl(nav, 'top-left');
  const scale = new maplibregl.ScaleControl({
    maxWidth: 80
  });
  map.addControl(scale, 'bottom-left');

  if (!offline) {
    map.addControl(
      new MaplibreGeocoder(geocoderApi, {
        maplibregl
      })
    );
  };

  marker = new maplibregl.Marker({draggable: true});

  layers = new Object();
  currentCursor = '';

  map.on('load', async () => {
    // Add dummy layer
    console.log('MapLibre loaded in main.js ...');
    addDummyLayer();
    map.addControl(draw, 'top-left');
    // Load icons
    iconUrls.forEach(async (iconUrl) => {
      var image = await map.loadImage(iconUrl);
      map.addImage(iconUrl, image.data);
    });
    mapLoaded();
  });

  map.on('style.load', () => {

//    map.setFog({}); // Set the default atmosphere style
//    // Add terrain
//    map.addSource('mapbox-dem', {
//      'type': 'raster-dem',
//      'url': 'mapbox://mapbox.mapbox-terrain-dem-v1',
//      'tileSize': 512,
//      'maxzoom': 14
//    });

    const layers = map.getStyle().layers;
    const labelLayer = layers.find(
      (layer) => layer.type === 'symbol' && layer.layout['text-field']
    );

    if (!labelLayer) {
      console.log('No label layer with id found with text-field property');
    } else {
      const labelLayerId = labelLayer.id;  
      // The 'building' layer in the MapLibre Streets
      // vector tileset contains building height data
      // from OpenStreetMap.
      //  console.log('Adding 3d buildings')
      // map.addLayer({
      //   'id': 'add-3d-buildings',
      //   'source': 'composite',
      //   'source-layer': 'building',
      //   'filter': ['==', 'extrude', 'true'],
      //   'type': 'fill-extrusion',
      //   'minzoom': 15,
      //   'paint': {
      //     'fill-extrusion-color': '#aaa',
      //     // Use an 'interpolate' expression to
      //     // add a smooth transition effect to
      //     // the buildings as the user zooms in.
      //     'fill-extrusion-height': [
      //       'interpolate',
      //       ['linear'],
      //       ['zoom'],
      //       15,
      //       0,
      //       15.05,
      //       ['get', 'height']
      //     ],
      //     'fill-extrusion-base': [
      //       'interpolate',
      //       ['linear'],
      //       ['zoom'],
      //       15,
      //       0,
      //       15.05,
      //       ['get', 'min_height']
      //     ],
      //     'fill-extrusion-opacity': 0.6
      //   }
      // }, labelLayerId);
    }

    // Add additional layers
  
  });

  map.on('moveend', () => {
    onMoveEnd();
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
//  map.once('click', function(e) { onPointClicked(e) });
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

// styleID should be in the form "satellite-v9"
export function setLayerStyle(styleID) {
  // console.log('Setting style to: ' + styleID);

  const currentStyle = map.getStyle();

  var newStyle = mapStyles[styleID];
 
  // Loop through all keys in currentStyle.sources to see which sources need to be copied to the new style
  for (var sourceId in newStyle.sources) {
    // Check if currentStyle source has atttribute sourceId
    if (sourceId in currentStyle.sources) {
      // source already exists
    } else {
      // source does not exist, so add this source to the current style
      currentStyle.sources[sourceId] = newStyle.sources[sourceId];
    } 
  }

  // Print sources in new style
  for (var sourceId in currentStyle.sources) {
    console.log("new src: " + sourceId);
  }  

  // Do the same for the layers
  var dummyLayerFound = false; 

  // First remove all the old background layers
  for (var layer in currentStyle.layers) { 
    // console.log("layerId: " + currentStyle.layers[layer].id); 
    if (currentStyle.layers[layer].id == 'dummy_layer') {
      dummyLayerFound = true;
      break
    } else {
      const index = currentStyle.layers.indexOf(layer);
      if (index > -1) { // only splice array when item is found
        currentStyle.layers.splice(index, 1); // 2nd parameter means remove one item only
      }
    }
  }

  currentStyle.layers = [
    ...newStyle.layers,
    ...currentStyle.layers,
  ];

  // Print layers in new style
  for (var layer in currentStyle.layers) {
    console.log("new layerId: " + currentStyle.layers[layer].id);
  }

  try {
    map.setStyle(currentStyle);
    layerStyleSet();
  } catch (error) {
    console.error('Error setting map style:', error);
  }
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
    'type': 'geojson',
    'data': {
      'type': 'FeatureCollection',
      'features': []
    }
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
