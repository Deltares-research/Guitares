let hover_property
let hoveredId = null;
let activeLayerId = null;
let popup
let selectedFeatures = []
let paintProperties = {}

export function addLayer(id,
  data,
  index,
  hovprop,
  paintProperties,
  // lineColor,
  // lineWidth,
  // lineOpacity,
  // fillColor,
  // fillOpacity,
  selectionOption) {

  // var lineColor = paintProperties.lineColor;
  // var lineWidth = paintProperties.lineWidth;
  // var lineOpacity = paintProperties.lineOpacity;
  // var fillColor = paintProperties.fillColor;
  // var fillOpacity = paintProperties.fillOpacity;  

  hover_property = hovprop

  let hoveredId = null
  let fillId = id + ".fill"
  let lineId = id + ".line"

  // Always remove old layers first to avoid errors
  if (map.getLayer(fillId)) {
    map.removeLayer(fillId);
  }
  if (map.getLayer(lineId)) {
    map.removeLayer(lineId);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }

  // Hover popup
  popup = new maplibregl.Popup({
    offset: 10,
    closeButton: false,
    closeOnClick: false
  });
  
  // Define the layer
  layers[id] = {}
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
      'line-color': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], paintProperties.lineColorSelected, paintProperties.lineColor],
      'line-opacity': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], paintProperties.lineOpacitySelected, paintProperties.lineOpacity],
      'line-width': paintProperties.lineWidth,
    },
    'layout': {
      // Make the layer visible by default.
      'visibility': 'visible'
      }
  });

  // Add fill layer
  map.addLayer({
    'id': fillId,
    'type': 'fill',
    'source': id,
    'paint': {
      'fill-color': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], paintProperties.fillColorSelected, paintProperties.fillColor],
      'fill-opacity': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], paintProperties.fillOpacitySelected, paintProperties.fillOpacity],
      'fill-outline-color': 'transparent'
    },
    'layout': {
     // Make the layer visible by default.
    'visibility': 'visible'
    }
  });

  map.setLayoutProperty(fillId, 'visibility', 'visible');
  map.setLayoutProperty(lineId, 'visibility', 'visible');

  // Update feature state after moving
  map.on('moveend', () => { moveEnd(id); } );
  // Hover pop-up
  map.on('mousemove', fillId, mouseEnter);
  map.on('mouseleave', fillId, mouseLeave);

  // Clicking
  if (selectionOption == "single") {
    map.off('click', fillId, clickSingle);
    map.on('click', fillId, clickSingle);
    // Select and click if pre-selection is provided
    if (index) {
      selectByIndex(id, index);
      for (let i = 0; i < layers[id].data.features.length; i++) {
        if (i == index) {
          featureClicked(id, layers[id].data.features[i]) 
        }
      }
    }
  } else {
    map.off('click', fillId, clickMultiple);
    map.on('click', fillId, clickMultiple);
    // Select and click if pre-selection is provided
    if (index) {
      selectByIndex(id, index);
      featureClicked(id, selectedFeatures)
    }
  }  
  map.once('idle', () => {
    updateFeatureState(id);
    // Call layerAdded in main.js
    layerAdded(id);
  });

};

function mouseEnter(e) {
  if (map.getFeatureState({ source: e.features[0].source, id: e.features[0].id }).active) { 
    // Change the cursor style as a UI indicator.
    map.getCanvas().style.cursor = 'pointer';
    if (e.features[0].properties.hasOwnProperty('hover_popup_width')) {  
      popup.setMaxWidth(e.features[0].properties.hover_popup_width);
    }
    var text = e.features[0].properties[hover_property];
    var lngLat = e.lngLat;
    popup.setLngLat(lngLat).setText(text).addTo(map);
    // Unset old hovered feature 
    if (hoveredId !== null) {
      map.setFeatureState(
        { source: e.features[0].source, id: hoveredId },
        { hover: false }
      );
    }  
    // Set hovered feature 
    map.setFeatureState(
      { source: e.features[0].source, id: e.features[0].id },
      { hover: true }
    );
    hoveredId = e.features[0].id;
    activeLayerId = e.features[0].source;
  } 
}

function mouseLeave(e) {
  map.getCanvas().style.cursor = currentCursor;
  popup.remove();
  if (hoveredId !== null) {
    map.setFeatureState(
      { source: activeLayerId, id: hoveredId },
      { hover: false }
    );
  }
  hoveredId = null;
}

function moveEnd(layerId) {
  const vis = map.getLayoutProperty(layerId + '.fill', 'visibility');
  if (vis == "visible") {
    updateFeatureState(layerId);
  }
}

// for a single selection type
function clickSingle(e) {
  if (e.features.length > 0) {
    selectByIndex(e.features[0].source, e.features[0].id);
    // And call main.js
    featureClicked(e.features[0].source, e.features[0]);
  };
}

// for a multiple selection type
function clickMultiple(e) {
  if (e.features.length > 0) {
    var featureState = map.getFeatureState({ source: e.features[0].source, id: e.features[0].id });
    // Get the layer id
    const layerId = e.features[0].source;
    if (featureState.selected) {
      // Was selected before, now deselect
      map.setFeatureState(
        { source: e.features[0].source, id: e.features[0].id },
        { selected: false }
      );
      layers[layerId].data.features[e.features[0].id].selected = false;
    } else {
      // Was deselected, now select
      map.setFeatureState(
        { source: e.features[0].source, id: e.features[0].id },
        { selected: true }
      );
      layers[layerId].data.features[e.features[0].id].selected = true;
    };
    // And call main.js
    // Find the selected features
    // Loop through all features in the source e.features[0].source
    var nfeat = layers[layerId].data.features.length
    selectedFeatures = [];
    for (let i = 0; i < nfeat; i++) {
      var featureState = map.getFeatureState({ source: e.features[0].source, id: i });
      if (featureState.selected) {
        selectedFeatures.push(layers[layerId].data.features[i]);
      }
    }
    featureClicked(e.features[0].source, selectedFeatures);
  };
}

// method to select features by index (called from python layer object)
export function selectByIndex(layerId, index) {
  if (index.length > 0) {
    for (let k = 0; k < index.length; k++) {
      for (let i = 0; i < layers[layerId].data.features.length; i++) {
        if (i == index[k]) {
          layers[layerId].data.features[i].selected = true
          selectedFeatures.push(layers[layerId].data.features[i]);
        }
      }
    }
  } else {
    for (let i = 0; i < layers[layerId].data.features.length; i++) {
      layers[layerId].data.features[i].selected = false
    }
  }
  // And update the feature state
  updateFeatureState(layerId);
}

// Set active and selected feature states
function updateFeatureState(layerId) {
  if (layers[layerId].mode == "active") {
    var active = true;
  } else {
    var active = false;
  }
  const features = map.querySourceFeatures(layerId, {sourceLayer: layerId + ".fill"});
  for (let i = 0; i < features.length; i++) {
    const index = features[i].id;
    if (layers[layerId].data.features[index].selected) {
      map.setFeatureState(
        { source: layerId, id: index },
        { selected: true, active: active }
      );
    } else {
      map.setFeatureState(
        { source: layerId, id: index },
        { selected: false, active: active }
      );
    }
  }  

}

// Set colors to active and update feature state
export function activate(id,
                         lineColor,
                         fillColor,
                         lineColorActive,
                         fillColorActive) {
  layers[layerId].mode = "active"
  if (map.getLayer(id)) {
    console.log('WTF?')
    map.setPaintProperty(id, 'circle-stroke-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      lineColorActive,
      lineColor]);
    map.setPaintProperty(id, 'circle-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      fillColorActive,
      fillColor]);
  }
  updateFeatureState(id);
}

// Set colors to inactive and update feature state
export function deactivate(id,
  lineColor,
  lineWidth,
  lineStyle,
  lineOpacity,
  fillColor,
  fillOpacity,
  lineColorActive,
  fillColorActive) {  
  layers[id].mode = "inactive"
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      lineColorActive,
      lineColor]);
    map.setPaintProperty(id, 'circle-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      fillColorActive,
      fillColor]);
    map.setPaintProperty(id, 'circle-radius', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      circleRadiusActive,
      circleRadius]);
  }
  updateFeatureState(id);
}

export function remove(id) {
  // Remove line layer
  var mapLayer = map.getLayer(id + '.line');
  if(typeof mapLayer !== 'undefined') {
    map.removeLayer(id + '.line');
  }
  // Remove fill layer
  var mapLayer = map.getLayer(id + '.fill');
  if(typeof mapLayer !== 'undefined') {
    map.removeLayer(id + '.line');
  }
  // Remove source
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  map.off('moveend', moveEnd(layerId));
}
