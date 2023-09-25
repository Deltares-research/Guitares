//import { map, featureClicked, mapboxgl, layers, layerAdded } from '/js/main.js';
//import { layerAdded } from '/js/main.js';

let hover_property
let hoveredId = null;
let activeLayerId = null;

let popup = new mapboxgl.Popup({
  offset: 10,
  closeButton: false,
  closeOnClick: false
});

export function addLayer(id,
  data,
  index,
  hovprop,
  lineColor,
  lineWidth,
  lineOpacity,
  fillColor,
  fillOpacity,
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

  //  var selectedFeatures = []

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

  map.addLayer({
    'id': fillId,
    'type': 'fill',
    'source': id,
    'paint': {
      'fill-color': fillColor,
      'fill-opacity': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], fillOpacity, 0.0],
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
    map.on('click', fillId, clickSingle);
  } else {
    map.on('click', fillId, clickMultiple);
  }  
  map.once('idle', () => {
    updateFeatureState(id);
    // Call layerAdded in main.js
    layerAdded(id);
  });


  // updateFeatureState(id);

  // // Create a popup, but don't add it to the map yet.
  // const popup = new mapboxgl.Popup({
  //   closeButton: false,
  //   closeOnClick: false
  // });

  // // Update feature state after moving
  // map.on('moveend', () => {
  //   const vis = map.getLayoutProperty(lineId, 'visibility');
  //   if (vis == "visible") {
  //     updateFeatureState(id);
  //   }
  // });

  // // When the user moves their mouse over the fill layer, we'll update the
  // // feature state for the feature under the mouse.
  // map.on('mousemove', fillId, (e) => {
  //   // Change the cursor style as a UI indicator.
  //   map.getCanvas().style.cursor = 'pointer';
  //   if (e.features.length > 0) {
  //     if (hoveredId !== null) {
  //       map.setFeatureState(
  //         { source: id, id: hoveredId },
  //         { hover: false }
  //       );
  //     }
  //     hoveredId = e.features[0].id;
  //     map.setFeatureState(
  //       { source: id, id: hoveredId },
  //       { hover: true }
  //     );
  //     // Display a popup with the name of area
  //     popup.setLngLat(e.lngLat)
  //     .setText(e.features[0].properties[hover_property])
  //     .addTo(map);
  //   }
  // });

  // // When the mouse leaves the fill layer, update the feature state of the
  // // previously hovered feature.
  // map.on('mouseleave', fillId, () => {
	// map.getCanvas().style.cursor = '';
  //   if (hoveredId !== null) {
  //     map.setFeatureState(
  //       { source: id, id: hoveredId },
  //       { hover: false }
  //     );
  //   }
  //   hoveredId = null;
  //   popup.remove();
  // });

  // if (selectionOption == "single") {
  //   map.on('click', fillId, (e) => {
  //     if (e.features.length > 0) {
  //       selectByIndex(id, e.features[0].id);
  //       // And call main.js
  //       featureClicked(id, e.features[0]);
  //     };
  //   });
  // } else {
  //   map.on('click', fillId, (e) => {
  //     if (e.features.length > 0) {
  //       var featureState = map.getFeatureState({ source: id, id: e.features[0].id });
  //       if (featureState.selected) {
  //         // Was selected, now deselect
  //         deselectByIndex(id, e.features[0].id);
  //         selectedFeatures.pop(e.features[0]);
  //       } else {
  //         // Select
  //         selectByIndex(id, e.features[0].id);
  //         selectedFeatures.push(e.features[0]);
  //       };
  //       // And call main.js
  //       featureClicked(id, selectedFeatures);
  //     };
  //   });
  // }
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
  const vis = map.getLayoutProperty(layerId + '.fill', 'visibility');
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

// function moveEnd(layerId) {
//   console.log(layerId);
//   const vis = map.getLayoutProperty(layerId + '.line', 'visibility');
//   console.log(vis);
//   if (vis == "visible") {
//     updateFeatureState(layerId);
//   }
// }
