import { map, featureClicked, mapboxgl, layers } from '/js/main.js';

export function addLayer(id,
  data,
  index,
  hover_property,
  lineColor,
  lineWidth,
  lineOpacity,
  fillColor,
  fillOpacity,
  selectionOption) {

  let hoveredId = null
  let fillId = id + ".fill"
  let lineId = id + ".line"
  var selectedFeatures = []

  layers[id] = {}
  layers[id].data = data; 
  layers[id].mode = "active"; 

  // Select first index
  selectByIndex(id, 0);

  map.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: "id"
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

  updateFeatureState(id);

  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  // Update feature state after moving
  //map.on('moveend', moveEnd(id));
  map.on('moveend', () => {
    const vis = map.getLayoutProperty(lineId, 'visibility');
    if (vis == "visible") {
      updateFeatureState(id);
    }
  });

  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', fillId, (e) => {
    // Change the cursor style as a UI indicator.
    map.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      if (hoveredId !== null) {
        map.setFeatureState(
          { source: id, id: hoveredId },
          { hover: false }
        );
      }
      hoveredId = e.features[0].id;
      map.setFeatureState(
        { source: id, id: hoveredId },
        { hover: true }
      );
      // Display a popup with the name of area
      popup.setLngLat(e.lngLat)
      .setText(e.features[0].properties[hover_property])
      .addTo(map);
    }
  });

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  map.on('mouseleave', fillId, () => {
	map.getCanvas().style.cursor = '';
    if (hoveredId !== null) {
      map.setFeatureState(
        { source: id, id: hoveredId },
        { hover: false }
      );
    }
    hoveredId = null;
    popup.remove();
  });

  if (selectionOption == "single") {
    map.on('click', fillId, (e) => {
      if (e.features.length > 0) {
        selectByIndex(id, e.features[0].id);
        // And call main.js
        featureClicked(id, e.features[0]);
      };
    });
  } else {
    map.on('click', fillId, (e) => {
      if (e.features.length > 0) {
        var featureState = map.getFeatureState({ source: id, id: e.features[0].id });
        if (featureState.selected) {
          // Was selected, now deselect
          deselectByIndex(id, e.features[0].id);
          selectedFeatures.pop(e.features[0]);
        } else {
          // Select
          selectByIndex(id, e.features[0].id);
          selectedFeatures.push(e.features[0]);
        };
        // And call main.js
        featureClicked(id, selectedFeatures);
      };
    });
  }
};

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
    const id = features[i].id;
    if (layers[layerId].data.features[id].selected) {
      map.setFeatureState(
        { source: layerId, id: id },
        { selected: true, active: active }
      );
    } else {
      map.setFeatureState(
        { source: layerId, id: id },
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
  layers[layerId].mode = "inactive"
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

function moveEnd(layerId) {
  console.log(layerId);
  const vis = map.getLayoutProperty(layerId + '.line', 'visibility');
  console.log(vis);
  if (vis == "visible") {
    updateFeatureState(layerId);
  }
}
