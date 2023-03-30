import { map, featureClicked, mapboxgl} from '/js/main.js';

export function addLayer(id, 
  data, 
  min_zoom, 
  hover_property, // do more than one
  color_property,
  lineColor,
  lineWidth,
  lineOpacity,
  fillOpacity) {

  let fillId = id + ".fill"
  let lineId = id + ".line"

  map.addSource(id, {
    type: 'geojson',
    data: data, 
    promoteId: hover_property
  });

  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'minzoom': min_zoom,
    'paint': {
      'line-color': lineColor,
      'line-width': lineWidth,
      'line-opacity': lineOpacity
     }
  });


  map.addLayer({
    'id': fillId,
    'type': 'fill',
    'source': id,
    'minzoom': min_zoom,
    'paint': {
      'fill-color': [
      'interpolate',
      ['linear'],
      ['get', color_property],
      // This should all not be hard0-coded and provided with input
      0,
      '#22f702',
      1,
      '#fffc51',
      3,
      '#fed976',
      6,
      '#ff2b20',
    ],
    'fill-opacity': fillOpacity
    }
  });

  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', fillId, (e) => {
    // Change the cursor style as a UI indicator.
    map.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      // Display a popup with the name of area
      popup.setLngLat(e.lngLat)
      .setText(hover_property + ": " + e.features[0].properties[hover_property])
      .addTo(map);
    }
  });

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  map.on('mouseleave', fillId, () => {
    popup.remove();
  });

};


export function activate(id,
                         lineColor,
                         fillColor,                   
                         lineColorActive,
                         fillColorActive) {

  const features = map.querySourceFeatures(id, {sourceLayer: id});
  for (let i = 0; i < features.length; i++) {
    map.setFeatureState(
      { source: id, id: features[i].id },
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
