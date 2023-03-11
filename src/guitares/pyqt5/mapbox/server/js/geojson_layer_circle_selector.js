import { map, featureClicked, mapboxgl } from '/js/main.js';

export function addLayer(id,
                         data,
                         index,
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

  let hoveredId = null;
//  let selectedId = null;

  var selectedFeatures = []
  // map.loadImage('./js/img/cross-marker-48-green.png',
  //   (error, image) => {
  //      if (error) throw error;
  //        map.addImage('custom-marker', image);
  //   }
  // );

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

//const marker = new map.Marker({draggable: true});

//  map.addLayer({
//    'id': 'points',
//    'type': 'symbol',
//    'source': id
//  });

  // Add a symbol layer
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

  map.once('idle', () => {
    setSelectedIndex(id, index);
  });

//  // Add a symbol layer
//  map.addLayer({
//    'id': 'points',
//    'type': 'symbol',
//    'source': id,
//    'layout': {
//      'icon-image': 'custom-marker',
//      'icon-size': 0.25,
//      // get name from the source's "name" property
//      'text-field': ['get', 'name'],
//      'text-font': [
//        'Open Sans Semibold',
//        'Arial Unicode MS Bold'
//      ],
//      'text-offset': [0, 0.5],
//      'text-anchor': 'top'
//    }
//  });

  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
  });

  map.on('mouseenter', id, (e) => {

//    const feature_state = map.getFeatureState({ source: id, sourceLayer: id, id: e.features[0].id })
//    const feature_state = map.getFeatureState({ source: id, id: e.features[0].id })
//    console.log(feature_state.active)
    if (map.getFeatureState({ source: id, id: e.features[0].id }).active) { 

      // Change the cursor style as a UI indicator.
      map.getCanvas().style.cursor = 'pointer';

      // Copy coordinates array.
      const coordinates = e.features[0].geometry.coordinates.slice();
      var description   = e.features[0].properties.name;

      if (e.features[0].properties.hasOwnProperty('hover_popup_width')) {  
	    	popup.setMaxWidth(e.features[0].properties.hover_popup_width);
      }

      // Ensure that if the map is zoomed out such that multiple
      // copies of the feature are visible, the popup appears
      // over the copy being pointed to.
      while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
      }

      // Populate the popup and set its coordinates
      // based on the feature found.
      popup.setLngLat(coordinates).setHTML(description).addTo(map);

    } 
  });

  map.on('mouseleave', id, () => {
      map.getCanvas().style.cursor = '';
      popup.remove();
  });

  // When the user moves their mouse over a circle marker, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', id, (e) => {
    if (e.features.length > 0) {
      if (map.getFeatureState({ source: id, id: e.features[0].id }).active) { 
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
    }
  });

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  map.on('mouseleave', id, () => {
    if (hoveredId !== null) {
      map.setFeatureState(
        { source: id, id: hoveredId },
        { hover: false }
      );
    }
    hoveredId = null;
  });

  if (selectionOption == "single") {
    map.on('click', id, (e) => {     
      if (map.getFeatureState({ source: id, id: e.features[0].id }).active) { 
        setSelectedIndex(id, e.features[0].id);
        featureClicked(id, e.features[0]);
      }
    });
  } else {
    map.on('click', id, (e) => {
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
        featureClicked(id, selectedFeatures);
      };
    });
  }
};

export function setSelectedIndex(id, index) {
  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    if (features[i].properties.index == index) {
      map.setFeatureState(
        { source: id, id: features[i].id },
        { selected: true, active: true }
      );
    } else {
      map.setFeatureState(
        { source: id, id: features[i].id  },
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
                         circleRadius,
                         lineColorActive,
                         fillColorActive,
                         circleRadiusActive) {

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
  circleRadius,
  lineColorActive,
  fillColorActive,
  circleRadiusActive) {

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
