var clickPopup = new maplibregl.Popup({
  className: 'maplibre-popup',
  closeButton: true,
  closeOnClick: true,
  offset: [0, -12]
});

var hoverPopup = new maplibregl.Popup({
  closeButton: false,
  closeOnClick: false,
  offset: [0, -12]
});

export function addLayer(id, data) {

  map.off('click', id, onClick);
  map.off('mouseenter', id, mouseEnter);
  map.off('mouseleave', id, mouseLeave);

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

  var prop0 = map.getSource(id)._data.features[0].properties;
  // Check if icon_size is defined.
  var iconSize = prop0.icon_size;
  if (!iconSize) {iconSize = 1.0;}
  // Check if icon_color is defined.
  var iconColor = prop0.icon_color;
  if (!iconColor) {iconColor = 'red';}

  // Add a layer for the points with icons based on icon URL property
  // console.log('Adding layer with id: ' + id);
  map.addLayer({
    id: id,
    type: 'symbol',
    source: id,
    layout: { 
      'icon-image': ['get', 'icon_url'],
      'icon-size': iconSize, // Adjust the icon size as needed
      'icon-allow-overlap': true
    }
  }, 'dummy_layer_1');

  // Add an event listener for mouseenter on the points
  map.on('mouseenter', id, mouseEnter);

  // Remove the popup when the mouse leaves the points
  map.on('mouseleave', id, mouseLeave)

  // Open popup on click. Should only work if click_html is defined.
  map.on('click', id, onClick);

}

function mouseEnter(e) {
  map.getCanvas().style.cursor = 'pointer';
  var coordinates = e.features[0].geometry.coordinates.slice();
  // If hover_property is defined, 
  if (e.features[0].properties.hasOwnProperty('hover_html')) {
      var html = e.features[0].properties.hover_html;
  } else {var html = null;}    
  // Ensure that if the map is zoomed out, the popup does not appear beyond the visible bounds
  while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
  }
  // Set the popup content and coordinates
  if (html) {
    hoverPopup.setLngLat(coordinates).setHTML(html).addTo(map);
  }  
}  

function mouseLeave(e) {
  map.getCanvas().style.cursor = currentCursor;
  hoverPopup.remove();
}

function onClick(e) {
    if (e.features[0].properties.hasOwnProperty('click_html')) {
      var coordinates = e.features[0].geometry.coordinates.slice();
      // Let the popup be slightly offset from the point, depending on the zoom level
      var offset = 0.0005 * Math.pow(2, 14 - map.getZoom());
      var html = e.features[0].properties.click_html;
//      if (e.features[0].properties.hasOwnProperty('click_popup_width')) {
//        var maxWidth = e.features[0].properties.click_popup_width.toString() + 'px';
//      } else {
//        var maxWidth = "none";
//      }
      var maxWidth = "none";
      // Ensure that if the map is zoomed out, the popup does not appear beyond the visible bounds
      while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
        coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
      }
      if (html) {
        clickPopup.setLngLat(coordinates).setHTML(html).setMaxWidth(maxWidth).addTo(map);
      }
    }  
}