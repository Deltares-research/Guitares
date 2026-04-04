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

/**
 * Add a marker/symbol layer with hover and click popup support.
 * @param {string} id - Unique layer/source identifier
 * @param {object} data - GeoJSON data with icon_url, hover_html, and click_html feature properties
 */
export function addLayer(id, data) {

  map.off('click', id, onClick);
  map.off('mouseenter', id, mouseEnter);
  map.off('mouseleave', id, mouseLeave);

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

  var prop0 = map.getSource(id)._data.features[0].properties;
  var iconSize = prop0.icon_size;
  if (!iconSize) { iconSize = 1.0; }
  var iconColor = prop0.icon_color;
  if (!iconColor) { iconColor = 'red'; }

  map.addLayer({
    id: id,
    type: 'symbol',
    source: id,
    layout: {
      'icon-image': ['get', 'icon_url'],
      'icon-size': iconSize,
      'icon-allow-overlap': true
    }
  }, 'dummy_layer_1');

  map.on('mouseenter', id, mouseEnter);
  map.on('mouseleave', id, mouseLeave);
  map.on('click', id, onClick);
}

/**
 * Handle mouseenter events to show hover popup and change cursor.
 * @param {object} e - MapLibre mouse event
 */
function mouseEnter(e) {
  map.getCanvas().style.cursor = 'pointer';
  var coordinates = e.features[0].geometry.coordinates.slice();
  var html = null;
  if (e.features[0].properties.hasOwnProperty('hover_html')) {
    html = e.features[0].properties.hover_html;
  }
  while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
    coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
  }
  if (html) {
    hoverPopup.setLngLat(coordinates).setHTML(html).addTo(map);
  }
}

/**
 * Handle mouseleave events to restore cursor and remove hover popup.
 * @param {object} e - MapLibre mouse event
 */
function mouseLeave(e) {
  map.getCanvas().style.cursor = window.currentCursor;
  hoverPopup.remove();
}

/**
 * Handle click events to show a click popup if click_html is defined.
 * @param {object} e - MapLibre mouse event
 */
function onClick(e) {
  if (e.features[0].properties.hasOwnProperty('click_html')) {
    var coordinates = e.features[0].geometry.coordinates.slice();
    var offset = 0.0005 * Math.pow(2, 14 - map.getZoom());
    var html = e.features[0].properties.click_html;
    var maxWidth = "none";
    while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
      coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
    }
    if (html) {
      clickPopup.setLngLat(coordinates).setHTML(html).setMaxWidth(maxWidth).addTo(map);
    }
  }
}
