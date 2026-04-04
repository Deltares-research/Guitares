/**
 * Add a custom polygon layer with fill styling, a legend, and hover popups.
 * @param {string} id - Layer identifier
 * @param {Object} data - GeoJSON data
 * @param {string} hover_property - Feature property used for hover display
 * @param {number} min_zoom - Minimum zoom level for the layer
 * @param {Object} paint_dict - MapLibre paint properties for the fill layer
 * @param {Array} legendItems - Array of {style, label} objects for the legend
 * @param {string} legend_position - CSS class for legend positioning
 * @param {string} legend_title - Title displayed above the legend
 */
export function addLayer(
  id,
  data,
  hover_property,
  min_zoom,
  paint_dict,
  legendItems,
  legend_position,
  legend_title,
) {

  let fillId = id + ".fill";
  let lineId = id + ".line";

  // Always remove old layers first to avoid errors
  if (map.getLayer(fillId)) {
    map.removeLayer(fillId);
  }
  if (map.getLayer(lineId)) {
    map.removeLayer(lineId);
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
    'id': fillId,
    'type': 'fill',
    'source': id,
    'minzoom': min_zoom,
    'paint': paint_dict,
    'layout': {
      'visibility': 'visible'
    }
  });

  // Build legend element
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
    newI.setAttribute('style', 'background:' + cnt["style"]);
    legend.appendChild(newI);
    var newSpan = document.createElement('span');
    newSpan.innerHTML = cnt["label"];
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
  }
  document.body.appendChild(legend);

  // Create a popup, but don't add it to the map yet.
  const popup = new maplibregl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  function onHover(e) {
    map.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      if (e.features[0].properties[hover_property]) {
        popup.setLngLat(e.lngLat)
          .setText(hover_property + ": "
            + numberWithCommas(e.features[0].properties[hover_property]))
          .addTo(map);
      }
    }
  }

  // Update feature state on hover
  map.on('mousemove', fillId, onHover);

  // Clear popup when mouse leaves
  map.on('mouseleave', fillId, () => {
    popup.remove();
  });
}

/**
 * Return the absolute value of an integer.
 * @param {number} integer
 * @returns {number}
 */
function absVal(integer) {
  return integer < 0 ? -integer : integer;
}

/**
 * Format a number with comma-separated thousands.
 * @param {number} x
 * @returns {string}
 */
function numberWithCommas(x) {
  if (x == 0) {
    return x.toString();
  } else {
    return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
  }
}
