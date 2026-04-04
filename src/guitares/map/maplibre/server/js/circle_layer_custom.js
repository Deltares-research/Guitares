/**
 * Add a custom circle layer with data-driven paint properties and a legend.
 * @param {string} id - Unique layer/source identifier
 * @param {object} data - GeoJSON data for the source
 * @param {string} hover_property - Feature property name used for hover popups and promoteId
 * @param {string} unit - Unit label shown in hover popup
 * @param {number} min_zoom - Minimum zoom level for layer visibility
 * @param {object} paint_dict - MapLibre paint properties object for the circle layer
 * @param {Array} legendItems - Array of legend entries with style and label properties
 * @param {string} legend_position - CSS class name for legend positioning
 * @param {string} legend_title - Title text displayed at the top of the legend
 */
export function addLayer(
  id,
  data,
  hover_property,
  unit,
  min_zoom,
  paint_dict,
  legendItems,
  legend_position,
  legend_title,
) {

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(id)) {
    map.removeLayer(id);
  }
  if (map.getSource(id)) {
    map.removeSource(id);
  }
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.parentNode.removeChild(legend);
  }

  map.addSource(id, {
    type: 'geojson',
    data: data,
    promoteId: hover_property
  });

  map.addLayer({
    'id': id,
    'type': 'circle',
    'source': id,
    'minzoom': min_zoom,
    'paint': paint_dict
  });

  map.setLayoutProperty(id, 'visibility', 'visible');

  if (hover_property !== "") {

    // Create a popup, but don't add it to the map yet
    const popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false
    });

    if (hover_property) {

      map.on('mouseenter', id, (e) => {
        map.getCanvas().style.cursor = 'pointer';

        // Copy coordinates array
        const coordinates = e.features[0].geometry.coordinates.slice();

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

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
  }

  // Build the legend element
  var legend = document.createElement("div");
  legend.id = "legend" + id;
  legend.className = legend_position;
  var newSpan = document.createElement('span');
  newSpan.class = 'title';
  newSpan.innerHTML = '<b>' + legend_title + '</b>';
  legend.appendChild(newSpan);
  legend.appendChild(document.createElement("br"));
  for (let i = 0; i < legendItems.length; i++) {
    let cnt = legendItems[i];
    var newI = document.createElement('i');
    newI.setAttribute('style', 'background:' + cnt["style"] + '; border-radius: 50%; width: 10px; height: 10px; display: inline-block;');
    legend.appendChild(newI);
    var newSpan = document.createElement('span');
    newSpan.innerHTML = cnt["label"];
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
  }
  document.body.appendChild(legend);
}

/**
 * Update the GeoJSON data for a custom circle layer source.
 * @param {string} id - Layer/source identifier
 * @param {object} data - New GeoJSON data
 */
export function setData(id, data) {
  var source = map.getSource(id);
  source.setData(data);
}

/**
 * Update paint properties for an existing custom circle layer.
 * @param {string} id - Layer identifier
 * @param {string|Array} lineColor - Circle stroke color
 * @param {number|Array} lineWidth - Circle stroke width
 * @param {number|Array} lineOpacity - Circle stroke opacity
 * @param {string|Array} fillColor - Circle fill color
 * @param {number|Array} fillOpacity - Circle fill opacity
 * @param {number|Array} circleRadius - Circle radius in pixels
 */
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
