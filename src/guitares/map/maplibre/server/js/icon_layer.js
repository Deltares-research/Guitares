/**
 * Add an icon/symbol layer with hover and click popups.
 * @param {string} id - Unique layer/source identifier
 * @param {object} data - GeoJSON data with icon_url, hover_html, and click_html feature properties
 */
export function addLayer(id, data) {

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  var mapSource = map.getSource(id);
  if (typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  // Load unique icon images from feature properties
  var uniqueIconUrls = {};
  map.getSource(id)._data.features.forEach(function (feature) {
    var iconUrl = feature.properties.icon_url;
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

  // Add a symbol layer with icons driven by the icon_url property
  map.addLayer({
    id: id,
    type: 'symbol',
    source: id,
    layout: {
      'icon-image': ['get', 'icon_url'],
      'icon-size': 1.0,
      'icon-allow-overlap': true,
    }
  });

  // Initialize a popup for hover/click
  var popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  map.on('mouseenter', id, function (e) {
    var coordinates = e.features[0].geometry.coordinates.slice();
    var description = e.features[0].properties.hover_html;
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }
    popup.setLngLat(coordinates).setHTML(description).addTo(map);
  });

  map.on('mouseleave', id, function () {
    popup.remove();
  });

  // Open popup on click if click_html property is defined
  map.on('click', id, function (e) {
    var coordinates = e.features[0].geometry.coordinates.slice();
    var description = e.features[0].properties.click_html;
    if (description) {
      popup.setLngLat(coordinates).setHTML(description).addTo(map);
    }
  });
}
