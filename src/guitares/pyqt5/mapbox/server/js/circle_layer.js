export function addLayer(id, data, hover_property,   min_zoom, 
  lineColor, 
  lineWidth, 
  lineOpacity, 
  fillColor, 
  fillOpacity, 
  circleRadius,
  unit) {  

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }
  
  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  // Add a symbol layer
  map.addLayer({
    'id': id,
    'type': 'circle',
    'source': id,
    'minzoom': min_zoom,
    'paint': {
      'circle-color': fillColor,
      'circle-stroke-width': lineWidth,
      'circle-stroke-color': lineColor,
      'circle-stroke-opacity': lineOpacity,
      'circle-radius': circleRadius,
      'circle-opacity': fillOpacity
    }
  });

  map.setLayoutProperty(id, 'visibility', 'visible');

  if (hover_property !== "") {

    // Create a popup, but don't add it to the map yet.
    const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
      });

    if (hover_property) {

      map.on('mouseenter', id, (e) => {

        // Change the cursor style as a UI indicator.
        map.getCanvas().style.cursor = 'pointer';
     
        // Copy coordinates array.
        const coordinates = e.features[0].geometry.coordinates.slice();
     
        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }
     
        // Display a popup 
        popup.setLngLat(e.lngLat)
          .setText(hover_property + ": " + (e.features[0].properties[hover_property])
          + " " + unit)
          .addTo(map);
      });
     
      map.on('mouseleave', id, () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
      });
    }
  };
};

export function setData(id, data) {
  var source = map.getSource(id);
  source.setData(data);
}

export function setPaintProperties(id,
  lineColor,
  lineWidth,
  lineOpacity,
  fillColor,
  fillOpacity,                         
  circleRadius) {

  if (map.getLayer(id)) {  
    map.setPaintProperty(id, 'circle-stroke-color', lineColor);
    map.setPaintProperty(id, 'circle-stroke-width', lineWidth);
    map.setPaintProperty(id, 'circle-stroke-opacity', lineOpacity);
    map.setPaintProperty(id, 'circle-color', fillColor);   
    map.setPaintProperty(id, 'circle-opacity', fillOpacity);                
    map.setPaintProperty(id, 'circle-radius', circleRadius);  
  }
}

