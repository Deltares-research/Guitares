console.log('draw.js ...');

import { draw, map, polygonDrawn, featureSelected, featureModified } from './main.js';

function polygonCreated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  polygonDrawn(coordString, id);
}

function polygonUpdated(e) {
  var feature=e.features[0];
  var id = feature["id"];
  var coordString = JSON.stringify(feature.geometry.coordinates);
  featureModified(coordString, id);
}

function modeChanged(e) {
}

function selectionChanged(e) {
  var feature=e.features[0];
  if (feature) {
    var id = feature["id"];
    draw.changeMode('direct_select', {featureId: id});
    featureSelected(id);
  }
}

// Incoming functions
export function drawPolygon(id) {
  draw.changeMode('draw_polygon');
  map.on('draw.create', polygonCreated);
  map.on('draw.modechange', modeChanged);
  map.on('draw.selectionchange', selectionChanged);
  map.on('draw.update', polygonUpdated);
}

export function deleteActiveFeature(id) {
  draw.delete(id);
}

export function deleteInactiveFeature(id) {
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }
}

export function addActiveFeature(id, geometry) {

  var feature = {
    id: id,
    type: 'Feature',
    properties: {},
    geometry: geometry
  };

  draw.add(feature);

}

export function addInactiveFeature(id, geometry) {

  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }

  map.addSource(id, {
    'type': 'geojson',
    'data': {'type': 'Feature', 'geometry': geometry}
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
