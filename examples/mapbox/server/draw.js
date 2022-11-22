console.log('draw.js ...');

import { draw, map, polygonDrawn, featureSelected } from './main.js';

function polygonCreated(e) {
  console.log('polygon drawn');
  var feature=e.features[0];
  console.log(feature);
  var id = feature["id"];
  console.log(id);
  const data = draw.getAll();
  console.log(data.features.length);
  console.log('mode = ' + draw.getMode());
//  draw.changeMode('direct_select',{featureId: string});
}

function ccc(e) {
  console.log('create');
  var feature=e.features[0];
  console.log(feature);
//  jsonString = 'okay!';
  polygonDrawn();
  console.log('called polygondrawn');
}

function mmm(e) {
  console.log('modechange');
//  var feature=e.features[0]
//  console.log(feature)
}

function sss(e) {
  console.log('selectionchange');
  var feature=e.features[0];
  if (feature) {
    var id = feature["id"];
    console.log(id);
    draw.changeMode('direct_select', {featureId: id});
    featureSelected(id);
  }
}

// Incoming functions
export function drawPolygon(id) {

  draw.changeMode('draw_polygon');

  map.on('draw.create', ccc);
  map.on('draw.modechange', mmm);
  map.on('draw.selectionchange', sss);

//  map.on('draw.selectionchange', polygonCreated);
}
