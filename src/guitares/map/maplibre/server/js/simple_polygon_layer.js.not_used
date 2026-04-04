let activeLayerId = null;

/**
 * Add a simple polygon layer with a styled line outline.
 * @param {string} id - Layer identifier
 * @param {Object} data - GeoJSON data
 * @param {string} lineColor - CSS color for the line
 * @param {number} lineWidth - Line width in pixels
 * @param {number} lineOpacity - Line opacity (0-1)
 * @param {string} lineStyle - Line style ("--" for dashed)
 */
export function addLayer(id,
  data,
  lineColor,
  lineWidth,
  lineOpacity,
  lineStyle) {

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
    promoteId: "index",
    'generateId': true
  });

  var lineDasharray = [1];
  if (lineStyle == "--") {
    lineDasharray = [2, 2];
  }

  // Add line layer
  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {
      'visibility': 'visible'
    },
    'paint': {
      'line-color': lineColor,
      'line-width': lineWidth,
      'line-opacity': lineOpacity,
      'line-dasharray': lineDasharray
    }
  });

  map.setLayoutProperty(lineId, 'visibility', 'visible');

  map.once('idle', () => {
    updateFeatureState(id);
    // Call layerAdded in main.js
    layerAdded(id);
  });
}

/**
 * Update the active/inactive feature state for all features in a layer.
 * @param {string} layerId - Layer identifier
 */
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

/**
 * Mark a layer as active and update its line color.
 * @param {string} id - Layer identifier
 * @param {string} lineColor - CSS color for the active state
 */
export function activate(id,
  lineColor) {
  layers[layerId].mode = "active";
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', lineColor);
  }
  updateFeatureState(id);
}

/**
 * Mark a layer as inactive and update its line color.
 * @param {string} id - Layer identifier
 * @param {string} lineColor - CSS color for the inactive state
 */
export function deactivate(id,
  lineColor) {
  layers[id].mode = "inactive";
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', lineColor);
  }
  updateFeatureState(id);
}

/**
 * Remove a polygon layer (line, fill, and source) from the map.
 * @param {string} id - Layer identifier
 */
export function remove(id) {
  // Remove line layer
  var mapLayer = map.getLayer(id + '.line');
  if (typeof mapLayer !== 'undefined') {
    map.removeLayer(id + '.line');
  }
  // Remove fill layer
  var mapLayer = map.getLayer(id + '.fill');
  if (typeof mapLayer !== 'undefined') {
    map.removeLayer(id + '.fill');
  }
  // Remove source
  var mapSource = map.getSource(id);
  if (typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
}
