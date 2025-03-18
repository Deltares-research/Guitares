let hover_property
let hoveredId = null
let activeLayerId = null
let selectedIndex = null // Only used for single selection
let popup
let selectedFeatures = []
let paintProperties = {}

export function addLayer(id,
  data,
  index,
  hovprop,
  paintProperties,
  selectionOption) {

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
  popup = new mapboxgl.Popup({
    offset: 10,
    closeButton: false,
    closeOnClick: false
  });
  
  // Define the layer
  layers[id] = {};
  layers[id].data = data; 
  layers[id].mode = "active"; 

  // Add source
  // The feature id is promoted to the index property
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
      'line-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], paintProperties.lineColorSelected,
//        ['boolean', ['feature-state', 'hovered'], false], paintProperties.lineColorHover,
        paintProperties.lineColor
      ], 
      'line-opacity': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], paintProperties.lineOpacitySelected,
        paintProperties.lineOpacity
      ], 
      'line-width': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], paintProperties.lineWidthSelected,
        ['boolean', ['feature-state', 'hovered'], false], paintProperties.lineWidthHover,
        paintProperties.lineWidth
      ], 
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
      'fill-color': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], paintProperties.fillColorSelected,
        ['boolean', ['feature-state', 'hovered'], false], paintProperties.fillColorHover,
        paintProperties.fillColor
      ], 
      'fill-opacity': [
        'case',
        ['boolean', ['feature-state', 'selected'], false], paintProperties.fillOpacitySelected,
        ['boolean', ['feature-state', 'hovered'], false], paintProperties.fillOpacityHover,
        paintProperties.fillOpacity
      ], 
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
  map.on('moveend', () => {moveEnd(id)} );

  // Hover pop-up
  map.on('mousemove', fillId, mouseEnter);
  map.on('mouseleave', fillId, mouseLeave);

  // Clicking
  if (selectionOption == "single") {
    map.off('click', fillId, clickSingle);
    map.on('click', fillId, clickSingle);
  } else {
    map.off('click', fillId, clickMultiple);
    map.on('click', fillId, clickMultiple);
  }  

  map.once('idle', () => {
    deselectAll(id);
    // Call layerAdded in main.js
    layerAdded(id);
  });

  // If there are any selected features, select them 
  if (index.length > 0) {
    select(id, index);
  }

};

function mouseEnter(e) {
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
        { hovered: false }
      );
    }  
    // Set hovered feature 
    map.setFeatureState(
      { source: e.features[0].source, id: e.features[0].id },
      { hovered: true }
    );
    hoveredId = e.features[0].id;
    activeLayerId = e.features[0].source;
  } 

function mouseLeave(e) {
  map.getCanvas().style.cursor = currentCursor;
  popup.remove();
  if (hoveredId !== null) {
    map.setFeatureState(
      { source: activeLayerId, id: hoveredId },
      { hovered: false }
    );
  }
  hoveredId = null;
}

function moveEnd(layerId) {
}

// for a single selection type
function clickSingle(e) {

  // Get the layer id
  var layerId = e.features[0].source;

  // First deselect previous feature
  if (selectedIndex !== null) {
    deselect(layerId, [selectedIndex]);
  }  

  // Then select the clicked feature
  selectedIndex = e.features[0].id;
  select(layerId, [selectedIndex]);

  // And call main.js
  featureClicked(e.features[0].source, e.features[0]);

}

// for a multiple selection type
function clickMultiple(e) {

  // Get the layer id and index
  var layerId = e.features[0].source;
  var index = e.features[0].id;

  // Get the feature state
  var featureState = map.getFeatureState({ source: e.features[0].source, id: e.features[0].id });

  if (featureState.selected) {
    // Was selected before, now deselect
    deselect(layerId, [index]);
  } else {
    // Was deselected, now select
    select(layerId, [index]);
  };
  // Find the selected features
  selectedFeatures = [];
  for (let i = 0; i < layers[layerId].data.features.length; i++) {
    var featureState = map.getFeatureState({ source: layerId, id: i });
    if (featureState.selected) {
      selectedFeatures.push(layers[layerId].data.features[i]);
    }
  }  
  // And call main.js
  featureClicked(layerId, selectedFeatures);
}

function select(layerId, indices) {
  // indices is an array
  for (let i = 0; i < indices.length; i++) {
    map.setFeatureState(
      { source: layerId, id: indices[i] },
      { selected: true }
    );
  }
}

function deselect(layerId, indices) {
  // indices is an array
  for (let i = 0; i < indices.length; i++) {
    map.setFeatureState(
      { source: layerId, id: indices[i] },
      { selected: false }
    );
  }
}

function deselectAll(layerId) {
  for (let i = 0; i < layers[layerId].data.features.length; i++) {
    map.setFeatureState(
      { source: layerId, id: i },
      { selected: false }
    );
  }
}

// method to select features by index (called from python layer object)
export function selectByIndex(layerId, indices) {
  // indices is an array
  select(layerId, indices);
}
