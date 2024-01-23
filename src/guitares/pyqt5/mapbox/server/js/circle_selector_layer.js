let hover_property
let hoveredId = null;
let activeLayerId = null;
let popup

export function addLayer(id,
                         data,
                         index,
                         hovprop,
                         lineColor,
                         lineWidth,
                         lineStyle,
                         lineOpacity,
                         fillColor,
                         fillOpacity,                         
                         circleRadius,
                         lineColorActive,
                         fillColorActive,
                         circleRadiusActive,

                         selectionOption) {

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }

  popup = new mapboxgl.Popup({
    offset: 10,
    closeButton: false,
    closeOnClick: false
  });
  
  hover_property = hovprop

  var selectedFeatures = []

  layers[id] = {}
  layers[id].data = data; 
  layers[id].mode = "active"; 

  // Select first index
  selectByIndex(id, index);

  map.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: "index"
  });

  // Add layer
  map.addLayer({
    'id': id,
    'type': 'circle',
    'source': id,
    'paint': {      
      'circle-stroke-color': ['case',
                               ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
                               lineColorActive,
                               lineColor],
      'circle-color': ['case',
                        ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
                        fillColorActive,
                        fillColor],
      'circle-stroke-width': lineWidth,
      'circle-radius': ['case',
                         ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
                         circleRadiusActive,
                         circleRadius],
      'circle-opacity': fillOpacity
    }
  });

  map.setLayoutProperty(id, 'visibility', 'visible');
  // Update feature state after moving
  map.on('moveend', () => { moveEnd(id); } );
  // Hover pop-up
  map.on('mouseenter', id, mouseEnter);
  map.on('mouseleave', id, mouseLeave);
  // Clicking
  if (selectionOption == "single") {
    map.on('click', id, clickSingle);
  } else {
    map.on('click', id, clickMultiple);
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
    // Copy coordinates array.
    const coordinates = e.features[0].geometry.coordinates.slice();
    // Ensure that if the map is zoomed out such that multiple
    // copies of the feature are visible, the popup appears
    // over the copy being pointed to.
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }
    // Populate the popup and set its coordinates
    // based on the feature found.
    var text = e.features[0].properties[hover_property];
    var lngLat = e.features[0].geometry.coordinates;
    popup.setLngLat(lngLat).setText(text).addTo(map);
    // Unset old hovered feature 
    if (hoveredId !== null) {
      map.setFeatureState(
        { source: e.features[0].source, id: e.features[0].id },
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
  map.getCanvas().style.cursor = "grab";
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
  const vis = map.getLayoutProperty(layerId, 'visibility');
  if (vis == "visible") {
    updateFeatureState(layerId);
  }
}

function clickSingle(e) {
  if (e.features.length > 0) {
    selectByIndex(e.features[0].source, e.features[0].id);
    // And call main.js
    featureClicked(e.features[0].source, e.features[0]);
  };
}

function clickMultiple(e) {
  if (e.features.length > 0) {
    var featureState = map.getFeatureState({ source: e.features[0].source, id: e.features[0].id });
    if (featureState.selected) {
      // Was selected, now deselect
      map.setFeatureState(
        { source: e.features[0].source, id: e.features[0].id },
        { selected: false }
      );
      selectedFeatures.pop(e.features[0]);
    } else {
      // Select
      map.setFeatureState(
        { source: e.features[0].source, id: e.features[0].id },
        { selected: true }
      );
      selectedFeatures.push(e.features[0]);
    };
    featureClicked(e.features[0].source, selectedFeatures);
  };
}

export function selectByIndex(layerId, index) {
  for (let i = 0; i < layers[layerId].data.features.length; i++) {
    if (i == index) {
      layers[layerId].data.features[i].selected = true
    } else {
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
  const features = map.querySourceFeatures(layerId, {sourceLayer: layerId});
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
  lineWidth,
  lineStyle,
  lineOpacity,
  fillColor,
  fillOpacity,
  circleRadius,
  lineColorSelected,
  fillColorSelected,
  circleRadiusSelected) {  

  layers[id].mode = "active"

  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      lineColorSelected,
      lineColor]);
    map.setPaintProperty(id, 'circle-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      fillColorSelected,
      fillColor]);
    map.setPaintProperty(id, 'circle-radius', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      circleRadiusSelected,
      circleRadius]);
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
  circleRadius,
  lineColorSelected,
  fillColorSelected,
  circleRadiusSelected) {  
  layers[id].mode = "inactive"
  if (map.getLayer(id)) {
    map.setPaintProperty(id, 'circle-stroke-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      lineColorSelected,
      lineColor]);
    map.setPaintProperty(id, 'circle-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      fillColorSelected,
      fillColor]);
    map.setPaintProperty(id, 'circle-radius', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      circleRadiusSelected,
      circleRadius]);
  }
  updateFeatureState(id);
}

export function remove(id) {
  // Remove layer
  var mapLayer = map.getLayer(id);
  if(typeof mapLayer !== 'undefined') {
    map.removeLayer(id);
  }
  // Remove source
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  map.off('moveend', moveEnd);
  map.off('mouseenter', id, mouseEnter);
  map.off('mouseleave', id, mouseLeave);
  // Clicking
  if (selectionOption == "single") {
    map.off('click', id, clickSingle);
  } else {
    map.off('click', id, clickMultiple);
  }  
}
