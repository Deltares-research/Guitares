import { map, featureClicked } from '/js/main.js';

export function addLayer(id, data, index,
  lineColor,
  lineWidth,
  lineStyle,
  lineOpacity,
  fillColor,
  fillOpacity,                         
  lineColorActive,
  fillColorActive,
  selectionOption) {

  let hoveredId = null;
  let selectedId = null
  let fillId = id + ".fill"
  let lineId = id + ".line"
  var selectedFeatures = []

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': '#000',
      'line-width': 0.5
     }
  });

  map.addLayer({
    id: fillId,
    type: 'fill',
    source: id,
    'paint': {
      'fill-color': fillColor,
      'fill-opacity': ['case', ['any', ['boolean', ['feature-state', 'hover'], false], ['boolean', ['feature-state', 'selected'], false]], fillOpacity, 0.0],
      'fill-outline-color': 'transparent'
    }
  });

//  map.addLayer({
//    'id': 'points',
//    'type': 'symbol',
//    'source': id,
//    'layout': {
//      // get the title name from the source's "title" property
//      'text-field': ['get', 'utm_number'],
//      'text-font': [
//        'Open Sans Semibold',
//        'Arial Unicode MS Bold'
//      ],
//      'text-offset': [0, 0],
//      'text-anchor': 'top',
//      'text-size': 12
//    }
//  });

  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', fillId, (e) => {
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
    }
  });

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  map.on('mouseleave', fillId, () => {
    if (hoveredId !== null) {
      map.setFeatureState(
        { source: id, id: hoveredId },
        { hover: false }
      );
    }
    hoveredId = null;
  });

  if (selectionOption == "single") {
    map.on('click', fillId, (e) => {
      if (e.features.length > 0) {
        // Set previous selected to False
        map.setFeatureState(
          { source: id, id: selectedId },
          { selected: false }
        );
        selectedId = e.features[0].id
        map.setFeatureState(
          { source: id, id: e.features[0].id },
          { selected: true }
        );
        featureClicked(id, e.features[0]);
      };
    });
  } else {
    map.on('click', fillId, (e) => {
      if (e.features.length > 0) {
        var featureState = map.getFeatureState({ source: id, id: e.features[0].id });
        if (featureState.selected) {
          // Was selected, now deselect
          map.setFeatureState(
            { source: id, id: e.features[0].id },
            { selected: false }
          );
          selectedFeatures.pop(e.features[0]);
        } else {
          // Select
          map.setFeatureState(
            { source: id, id: e.features[0].id },
            { selected: true }
          );
          selectedFeatures.push(e.features[0]);
        };
        // Now make a list of all selected features
//        var selectedFeatureProperties = []
//        selectedFeatures.forEach((feature) => {
//          var featureState = map.getFeatureState({ source: id, id: feature.id });
//          if (featureState.selected) {
//            selectedFeatureProperties.push(feature);
//          }
//        });
        featureClicked(id, selectedFeatures);
      };
    });


  }
};

// export function setData(id, data) {
//   console.log('setting data in ' + id);
//   console.log(data);
//   var source = map.getSource(id);
//   source.setData(data);
// }

export function setSelectedIndex(id, index) {
  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    if (features[i].id == index) {
      map.setFeatureState(
        { source: id, id: i },
        { selected: true, active: true }
      );
    } else {
      map.setFeatureState(
        { source: id, id: i },
        { selected: false, active: true }
      );
    }
  }
}

export function activate(id,
                         lineColor,
                         lineWidth,
                         lineStyle,
                         lineOpacity,
                         fillColor,
                         fillOpacity,                         
                         lineColorActive,
                         fillColorActive) {

  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    map.setFeatureState(
      { source: id, id: i },
      { active: true }
    );
  }
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
}

export function deactivate(id,
  lineColor,
  lineWidth,
  lineStyle,
  lineOpacity,
  fillColor,
  fillOpacity,                         
  lineColorActive,
  fillColorActive) {

  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    map.setFeatureState(
      { source: id, id: i },
      { active: false }
    );
  }  
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
}
