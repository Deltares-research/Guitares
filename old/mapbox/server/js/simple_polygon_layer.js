let activeLayerId = null

export function addLayer(id,
  data,
  lineColor,
  lineWidth,
  lineOpacity,) {

  let lineId = id + ".line";

  // Always remove old layers first to avoid errors
  if (map.getLayer(lineId)) {
    map.removeLayer(lineId);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }

  // Define the layer
  layers[id] = {};
  layers[id].data = data;
  layers[id].mode = "active";

  // Add source
  map.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: "index"
  });

  // Add line layer
  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': lineColor,
      'line-width': lineWidth,
      'line-opacity': lineOpacity
    },
    'layout': {
      // Make the layer visible by default.
      'visibility': 'visible'
    }
  });


  map.setLayoutProperty(lineId, 'visibility', 'visible');

  map.once('idle', () => {
    updateFeatureState(id);
    // Call layerAdded in main.js
    layerAdded(id);
  });
}

function updateFeatureState(layerId) {
  if (layers[layerId].mode == "active") {
    var active = true;
  } else {
    var active = false;
  }
  const features = map.querySourceFeatures(layerId, { sourceLayer: layerId + ".fill" });
  for (let i = 0; i < features.length; i++) {
    const index = features[i].id;
    map.setFeatureState(
      { source: layerId, id: index },
      { active: active }
    );
  }
}

export function activate(id,
  lineColor) {
  layers[layerId].mode = "active"
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', lineColor);
  }
  updateFeatureState(id);
}

export function deactivate(id,
  lineColor) {
  layers[id].mode = "inactive"
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', lineColor);
  }
  updateFeatureState(id);
}

export function remove(id) {
  // Remove line layer
  var mapLayer = map.getLayer(id + '.line');
  if (typeof mapLayer !== 'undefined') {
    map.removeLayer(id + '.line');
  }
  // Remove fill layer
  var mapLayer = map.getLayer(id + '.fill');
  if (typeof mapLayer !== 'undefined') {
    map.removeLayer(id + '.line');
  }
  // Remove source
  var mapSource = map.getSource(id);
  if (typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
}