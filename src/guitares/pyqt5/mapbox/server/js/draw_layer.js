let MapboxDraw = mpbox.import_mapbox_draw()

//import { map, featureDrawn, featureSelected, featureModified, featureAdded, featureDeselected } from '/js/main.js';
import { featureDrawn, featureSelected, featureModified, featureAdded, featureDeselected } from '/js/main.js';
import { DrawRectangle } from '/js/mapbox-gl-draw-rectangle-mode.js';
import { drawStyles } from '/js/draw_styles.js'
import { SRMode, SRCenter } from '/js/mapbox_gl_draw_scale_rotate_mode.js'

let createListener = dummyFunction
var featureList = []
var layerList = []
let activeLayerId
let modes
let selectedFeatureId

// Add extra modes
modes = MapboxDraw.modes;
modes.draw_rectangle = DrawRectangle;
modes.scale_rotate_mode = SRMode

export const draw = new MapboxDraw({displayControlsDefault: false,
                                    userProperties: true,
                                    styles: drawStyles,
                                    modes: modes,
                                   });

export function setDrawEvents() {
  map.on('draw.create', createListener);
  map.on('draw.modechange', modeChanged);
  map.on('draw.selectionchange', selectionChanged);
  map.on('draw.update', featureUpdated);
  // Set mode to simple_select when right-clicking
  map.on("mousedown", (e) => {
    if (e.originalEvent.button === 2) {
      draw.changeMode('simple_select', { featureIds: [] })
    }
  });
}

function dummyFunction(e) {
}

function modeChanged(e) {
  draw.changeMode('simple_select', {featureIds: []});
}

function selectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    var featureId = feature["id"];
    selectedFeatureId = featureId;
    var featureProps = getFeatureProps(featureId)
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

function featureUpdated(e) {
  var feature=e.features[0];
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

function activateScaleRotateMode(featureId) {
  draw.changeMode('scale_rotate_mode', {
    featureId: featureId,
//    canScale: false,
//    canRotate: false, // only rotation enabled
    canScale: true,
    canRotate: getLayerProps(activeLayerId).paintProps.rotate, // only rotation enabled
    canTrash: false, // disable feature delete
    rotatePivot: SRCenter.Center, // rotate around center
    scaleCenter: SRCenter.Opposite, // scale around opposite vertex
    singleRotationPoint: true, // only one rotation point
    rotationPointRadius: 1.2, // offset rotation point
    canSelectFeatures: true,
  });
}

function activateDirectSelectMode(featureId) {
  draw.changeMode('direct_select', {featureId: featureId});
}

/// POLYGON \\\

export function drawPolygon(layerId) {
  setDrawEvents();
  activeLayerId = layerId;
  setLayerMode(layerId, 'active');
  draw.changeMode('draw_polygon');
  map.off('draw.create', createListener);
  createListener = polygonCreated;
  map.on('draw.create', createListener);
  map.getCanvas().style.cursor = 'pointer';

}

function polygonCreated(e) {
  var feature = e.features[0];
  var featureId = feature["id"];
  var layerProps = getLayerProps(activeLayerId);
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(featureId, key, value);
  }
  addToFeatureList(featureId, activeLayerId, "polygon", feature.geometry);
  updateInactiveLayerGeometry(activeLayerId);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  featureDrawn(JSON.stringify(featureCollection), featureId, activeLayerId);
}

function polygonUpdated(e) {
  var feature=e.features[0];
  var featureId = feature["id"];
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  setGeometryInFeatureList(featureId, feature.geometry); 
  updateInactiveLayerGeometry(activeLayerId);
  featureModified(JSON.stringify(featureCollection), featureId, activeLayerId);
}

function polygonSelectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    var featureId = feature["id"];
    activateDirectSelectMode(featureId);
    activeLayerId        = getFeatureProps(featureId).layerId;
    var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
    featureSelected(JSON.stringify(featureCollection), featureId, activeLayerId);
  }
}

/// POLYLINE \\\

export function drawPolyline(id) {
  setDrawEvents();
  activeLayerId         = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_line_string');
  map.off('draw.create', createListener);
  createListener = polylineCreated
  map.on('draw.create', createListener);
}

function polylineCreated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var layerProps = getLayerProps(activeLayerId)
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(id, activeLayerId, 'polyline', feature.geometry);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  featureDrawn(JSON.stringify(featureCollection), id, activeLayerId);
}

function polylineUpdated(e) {
  var feature=e.features[0];
  var featureId = feature["id"];
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  setGeometryInFeatureList(featureId, feature.geometry); 
  updateInactiveLayerGeometry(activeLayerId);
  featureModified(JSON.stringify(featureCollection), featureId, activeLayerId);
}

function polylineSelectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    var id = feature["id"];
    activateDirectSelectMode(id);
    activeLayerId        = getFeatureProps(id).layerId;
    var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
    featureSelected(JSON.stringify(featureCollection), id, activeLayerId);
  }
}

/// RECTANGLE \\\

export function drawRectangle(id) {
  setDrawEvents();
  activeLayerId = id;
  setLayerMode(id, 'active');
  draw.changeMode('draw_rectangle');
  map.off('draw.create', createListener);
  createListener = rectangleCreated;
  map.on('draw.create', createListener);
}

function rectangleCreated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var layerProps = getLayerProps(activeLayerId);
  for (const [key, value] of Object.entries(layerProps.paintProps)) {
    draw.setFeatureProperty(id, key, value);
  }
  addToFeatureList(id, activeLayerId, 'rectangle', feature.geometry);
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  featureDrawn(JSON.stringify(featureCollection), id, activeLayerId);
}

function rectangleUpdated(e) {
  var feature=e.features[0];
  var featureId = feature["id"];
  var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
  setGeometryInFeatureList(featureId, feature.geometry); 
  updateInactiveLayerGeometry(activeLayerId);
  featureModified(JSON.stringify(featureCollection), featureId, activeLayerId);
}

function rectangleSelectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    var id = feature["id"];
    activateScaleRotateMode(id);
    activeLayerId        = getFeatureProps(id).layerId;
    var featureCollection = getFeatureCollectionInActiveLayer(activeLayerId);
    featureSelected(JSON.stringify(featureCollection), id, activeLayerId);
  }
}

/// FEATURES \\\

export function addFeature(featureCollection, layerId) {
  setDrawEvents();
  activeLayerId = layerId;
  // Geometry comes in as a feature collection
  var geometry = featureCollection.features[0].geometry;
  var layerProps = getLayerProps(layerId);
  if (layerProps == null) {
    console.log("No draw layer found with ID " + layerId)
    return
  }
  // Make random featureId 
  var featureId = makeid(15);
  // Plot feature and add to feature list
  plotFeature(featureId, geometry, layerProps.paintProps);
  addToFeatureList(featureId, layerId, layerProps.shape, geometry);
  // Update geometry of inactive layer 
  updateInactiveLayerGeometry(layerId);
  // Set the layer mode
  setLayerMode(layerId, layerProps.mode);
  if (layerProps.mode == "active") {
    var featureCollection = getFeatureCollectionInActiveLayer(layerId);
  } else {
    var featureCollection = getFeatureCollectionInInactiveLayer(layerId);
  }
  featureAdded(JSON.stringify(featureCollection), featureId, layerId);
}

function plotFeature(featureId, geometry, paintProps) {
  var feature = {
    id: featureId,
    type: 'Feature',
    properties: {},
    geometry: geometry
  };
  draw.add(feature);
  // Loop through paint props
  for (const [key, value] of Object.entries(paintProps)) {
    draw.setFeatureProperty(featureId, key, value);
  }
}

export function deleteFeature(featureId) {
  var layerId = getFeatureProps(featureId).layerId;
  draw.delete(featureId);
  removeFromFeatureList(featureId);
  updateInactiveLayerGeometry(layerId);
}

export function activateFeature(featureId) {
  // Called from other script
  draw.changeMode('simple_select', { featureIds: [featureId] })
  selectedFeatureId = featureId;
  activeLayerId = getFeatureProps(featureId).layerId;
  var featureProps = getFeatureProps(featureId)
  if (featureProps.shape == "polygon" || featureProps.shape == "polyline") {
    activateDirectSelectMode(featureId);
  }
  if (featureProps.shape == "rectangle") {
    activateScaleRotateMode(featureId);
  }
}

function addToFeatureList(featureId, layerId, shape, geometry) {
  featureList.push({
    featureId: featureId,
    shape: shape,
    layerId: layerId,
    geometry: geometry
  });
}

function setGeometryInFeatureList(featureId, geometry) {
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].featureId == featureId) {
      featureList[i].geometry = geometry;
    }
  }
}

export function setFeatureGeometry(layerId, featureId, featureCollection) {
  // Update geometry of feature
  var geometry = featureCollection.features[0].geometry;
  var layerProps = getLayerProps(layerId);
  setGeometryInFeatureList(featureId, geometry);
  updateInactiveLayerGeometry(layerId);
}

function removeFromFeatureList(featureId) {
  featureList.splice(featureList.findIndex(v => v.featureId === featureId), 1);
}

function getFeatureProps(featureId) {
  var props = null
  var index = featureList.findIndex(v => v.featureId === featureId);
  if (index>=0) {props = featureList[index]};
  return props
}

function getFeatureCollectionInActiveLayer(layerId) {
  // Feature collection with all features (of every layer)
  var featureCollection = draw.getAll();
  // Make list with features in active layer
  var featureIdsInLayer = [];
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layerId == layerId) {
      featureIdsInLayer.push(featureList[i].featureId);
    }
  }
  var nfeat = featureCollection.features.length;
  for (let i = 0; i < nfeat; i++) {
    if (featureIdsInLayer.includes(featureCollection.features[nfeat - i - 1].id) == false) {
      featureCollection.features.splice(nfeat - i - 1, 1);
    }
  }
  return featureCollection
}

function getFeatureCollectionInInactiveLayer(layerId) {
  // Feature collection with all features
  var featureCollection = {}
  featureCollection.type = "FeatureCollection"
  featureCollection.features = []
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layerId == layerId) {
      var feature = {}
      feature.type = "Feature"
      feature.properties = {}
      feature.properties["id"] = featureList[i].featureId;
      feature.id = featureList[i].featureId;
      feature.geometry = featureList[i].geometry;
      featureCollection.features.push(feature);
    }
  }
  return featureCollection
}


/// LAYERS \\\

export function addLayer(layerId, mode, paintProps, shape) {

  // Check if this layer already exists
  var props = getLayerProps(layerId);
  if (props != null) {
    return
  }
  addToLayerList(layerId, mode, paintProps, shape);

  // Add inactive layer 
  map.addSource(layerId, {
    'type': 'geojson'
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
}

function updateInactiveLayerGeometry(layerId) {
  var featureCollection = getFeatureCollectionInActiveLayer(layerId);
  map.getSource(layerId).setData(featureCollection);
}

export function deleteLayer(layerId) {
  // Loop through features in layer
  for (let i = 0; i < featureList.length; i++) {
    if (featureList[i].layerId == layerId) {
      deleteFeature(featureList[i].featureId);
    }
  }
  // Delete inactive layer
  if (map.getLayer(layerId + ".line")) {
    map.removeLayer(layerId + ".line");
  }
  if (map.getLayer(layerId + ".fill")) {
    map.removeLayer(layerId + ".fill");
  }  
//  map.removeLayer(layerId + ".line");
//  map.removeLayer(layerId + ".fill");
  map.removeSource(layerId);
  removeFromLayerList(layerId);
}

export function setLayerMode(layerId, mode) {
  var layerProps   = getLayerProps(layerId);
  if (layerProps == null) {
    return
  }
  if (mode == "active") {
    // Plot features
    // Loop through features in layer
    for (let i = 0; i < featureList.length; i++) {
      if (featureList[i].layerId == layerId) {
        // This feature is part of this layer
        var featureId = featureList[i].featureId;
        var geometry = featureList[i].geometry;
        var paintProps = layerProps.paintProps;
        plotFeature(featureId, geometry, paintProps);
      }
    }
  }
  else {
    // Delete features
    for (let i = 0; i < featureList.length; i++) {
      if (featureList[i].layerId == layerId) {
        draw.delete(featureList[i].featureId);
      }
    }  
  }
  setLayerProps(layerId, "mode", mode);
  // Set visibility for inactive layer 
  if (mode == "inactive") {
    map.setLayoutProperty(layerId + ".line", 'visibility', 'visible');
    var fillLayer = map.getLayer(layerId + '.fill');
    if(typeof fillLayer !== 'undefined') {  
      map.setLayoutProperty(layerId + ".fill", 'visibility', 'visible');
    }  
  } else {
    map.setLayoutProperty(layerId + ".line", 'visibility', 'none');
    var fillLayer = map.getLayer(layerId + '.fill');
    if(typeof fillLayer !== 'undefined') {  
      map.setLayoutProperty(layerId + ".fill", 'visibility', 'none');
    }  
  }
}

function addToLayerList(layerId, mode, paintProps, shape) {
  // Check if layer already exists
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index < 0) {
    layerList.push({layerId: layerId, mode: mode, paintProps: paintProps, shape: shape})
  }
}

function removeFromLayerList(featureId) {
  layerList.splice(layerList.findIndex(v => v.featureId === featureId), 1);
}

export function clearLayerList() {
  layerList = [];
}

function getLayerProps(layerId) {
  var props = null
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index>=0) {props = layerList[index]};
  return props
}

function setLayerProps(layerId, key, val) {
  var index = layerList.findIndex(v => v.layerId === layerId);
  if (index>=0) {layerList[index][key] = val};
}


/// OTHER \\\

export function setMouseDefault() {
  draw.changeMode('simple_select', { featureIds: [] })
}

function makeid(length) {
  let result = '';
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const charactersLength = characters.length;
  let counter = 0;
  while (counter < length) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
    counter += 1;
  }
  return result;
}
