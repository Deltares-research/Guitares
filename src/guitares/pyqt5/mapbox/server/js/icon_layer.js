export function addLayer(id, data) {

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  
  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  // Iterate through your GeoJSON data to extract unique icon URLs and add them as images
  var uniqueIconUrls = {};
  map.getSource(id)._data.features.forEach(function (feature) {
    var iconUrl = feature.properties.icon_url; // Replace 'iconUrl' with the property in your GeoJSON that specifies the icon URL
    // Check if this icon is already loaded
    if (!map.hasImage(iconUrl)) {
      if (iconUrl && !uniqueIconUrls[iconUrl]) {
        map.loadImage(iconUrl, function (error, image) {
          if (error) throw error;
          map.addImage(iconUrl, image);
        });
        uniqueIconUrls[iconUrl] = true;
      }
    }
  });

  // Add a layer for the points with custom icons based on icon URL property
  map.addLayer({
    id: id,
    type: 'symbol',
    source: id,
    layout: {
      'icon-image': ['get', 'icon_url'],
      'icon-size': 1.0, // Adjust the icon size as needed
      'icon-allow-overlap': true,
    }
  });

  // Initialize a popup
  var popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  // Add an event listener for mouseenter on the points
  map.on('mouseenter', id, function (e) {
    var coordinates = e.features[0].geometry.coordinates.slice();
    var description = e.features[0].properties.hover_html;
    // Ensure that if the map is zoomed out, the popup does not appear beyond the visible bounds
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }
    // Set the popup content and coordinates
    popup.setLngLat(coordinates).setHTML(description).addTo(map);
  });

  // Remove the popup when the mouse leaves the points
  map.on('mouseleave', id, function () {
    popup.remove();
  });

  // Open popup on click. Should only work if click_html is defined.
  map.on('click', id, function (e) {
    var coordinates = e.features[0].geometry.coordinates.slice();
    var description = e.features[0].properties.click_html;
    if (description) {
      popup.setLngLat(coordinates).setHTML(description).addTo(map);
    }
  });

}

//   map.addLayer({
//     'id': lineId,
//     'type': 'line',
//     'source': id,
//     'layout': {},
//     'paint': {
//       'line-color': lineColor,
//       'line-width': lineWidth,
//       'line-opacity': lineOpacity,
//      }
//   });
  
//   if (circleRadius>0) {
//     map.addLayer({
//       'id': circleId,
//       'type': 'circle',
//       'source': id,
//       'paint': {
//         'circle-color': fillColor,
//         'circle-stroke-width': lineWidth,
//         'circle-stroke-color': lineColor,
//         'circle-stroke-opacity': lineOpacity,
//         'circle-radius': circleRadius,
//         'circle-opacity': fillOpacity
//       }
//     });
//   }
// };

// export function setData(id, data) {
//   var source = map.getSource(id);
//   source.setData(data);
// }

// export function setPaintProperties(id,
//   lineColor,
//   lineWidth,
//   lineOpacity,
//   fillColor,
//   fillOpacity,                         
//   circleRadius) {

//   if (map.getLayer(id)) {  
//     map.setPaintProperty(id + ".circle", 'circle-stroke-color', lineColor);
//     map.setPaintProperty(id + ".circle", 'circle-stroke-width', lineWidth);
//     map.setPaintProperty(id + ".circle", 'circle-stroke-opacity', lineOpacity);
//     map.setPaintProperty(id + ".circle", 'circle-color', fillColor);   
//     map.setPaintProperty(id + ".circle", 'circle-opacity', fillOpacity);                
//     map.setPaintProperty(id + ".circle", 'circle-radius', circleRadius);  

//     map.setPaintProperty(id + ".line", 'line-color', lineColor);
//     map.setPaintProperty(id + ".line", 'line-width', lineWidth);               
 
//   }
// }