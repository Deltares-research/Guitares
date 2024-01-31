function getLineDashArray(lineStyle) {
  if (lineStyle === '-') {
    return [1];  // Continuous line
  } else if (lineStyle === '--') {
    return [2, 1];  // Dashed line
  } else if (lineStyle === '..') {
    return [0.5, 1];  // Dotted line
  }
}

export function addLayer(id,
                         data,
                         index,
                         lineColor,
                         lineWidth,
                         lineStyle,
                         lineOpacity,
                         lineColorSelected,
                         lineWidthSelected,
                         lineStyleSelected,
                         lineOpacitySelected,
                         hoverParam,
                         selectionOption) {

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }

  let hoveredId = null;

  var selectedFeatures = []

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  let lineDashArray = getLineDashArray(lineStyle);

  // Add a symbol layer
  map.addLayer({
    'id': id,
    'type': 'line',
    'source': id,
    'paint': {      
      'line-color': ['case',
                             ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
                             lineColorSelected,
                             lineColor],
      'line-width': ['case',
                             ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
                             lineWidthSelected,
                             lineWidth],
      'line-dasharray': lineDashArray,
    }
  });

  map.once('idle', () => {
    setSelectedIndex(id, index);
  });

  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
  });

  map.on('mouseenter', id, (e) => {

    if (map.getFeatureState({ source: id, id: e.features[0].id }).active) { 

      // Change the cursor style as a UI indicator.
      map.getCanvas().style.cursor = 'pointer';


      var description   = e.features[0].properties[hoverParam];


      if (e.features[0].properties.hasOwnProperty('hover_popup_width')) {  
	    	popup.setMaxWidth(e.features[0].properties.hover_popup_width);
      }

      // Copy coordinates array.
      const coordinates = e.lngLat;
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

  // When the user moves their mouse over a line, we'll update the
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

  // When the mouse leaves the line, update the feature state of the
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
    lineColorSelected,
    lineWidthSelected,
    lineStyleSelected,
    lineOpacitySelected) {

  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    map.setFeatureState(
      { source: id, id: i },
      { active: true }
    );
  }
  if (map.getLayer(id)) {  
    map.setPaintProperty(id, 'line-color', ['case',
      ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
      lineColorSelected,
      lineColor]);                          
  }                           
}

export function deactivate(id,
  lineColor,
  lineWidth,
  lineStyle,
  lineOpacity) {

  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    map.setFeatureState(
      { source: id, id: i },
      { active: false }
    );
  }  
  if (map.getLayer(id)) {  
    map.setPaintProperty(id, 'line-color', lineColor);                          
  }
}
