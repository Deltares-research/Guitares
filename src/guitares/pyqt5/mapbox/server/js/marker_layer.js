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

  var prop0 = map.getSource(id)._data.features[0].properties;
  // Check if icon_size is defined.
  var iconSize = prop0.icon_size;
  if (!iconSize) {iconSize = 1.0;}
  // Check if icon_color is defined.
  var iconColor = prop0.icon_color;
  if (!iconColor) {iconColor = 'red';}
  // Check if icon_url is a property of the GeoJSON data.
  var iconUrl = prop0.icon_url;

  // Add a layer for the points with icons based on icon URL property
  map.addLayer({
    id: id,
    type: 'symbol',
    source: id,
    layout: {
      'icon-image': ['get', 'icon_url'],
      'icon-size': iconSize, // Adjust the icon size as needed
      'icon-allow-overlap': true
    }
  });

  // Initialize a popup
  var hoverPopup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false,
    offset: [0, -12]
  });

  // Initialize a popup
  var clickPopup = new mapboxgl.Popup({
    closeButton: true,
    closeOnClick: true,
    offset: [0, -12]
  });

  // Add an event listener for mouseenter on the points
  map.on('mouseenter', id, function (e) {
    // Change the cursor style as a UI indicator.
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
  });

  // Remove the popup when the mouse leaves the points
  map.on('mouseleave', id, function () {
    map.getCanvas().style.cursor = '';
    hoverPopup.remove();
  });

  // Open popup on click. Should only work if click_html is defined.
  map.on('click', id, function (e) {
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
  });
}
