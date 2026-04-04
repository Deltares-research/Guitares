/**
 * Return the map object for the given side panel.
 * @param {string} side - Panel identifier ("a", "b", or undefined for default)
 * @returns {object} The corresponding map instance
 */
function getMap(side) {
  if (side == "a") { return mapA; }
  else if (side == "b") { return mapB; }
  else { return map; }
}

/**
 * Add a raster tile layer from a tile URL template.
 * @param {string} id - Unique layer/source identifier
 * @param {string} url - Tile URL template (e.g. "https://example.com/{z}/{x}/{y}.png")
 * @param {string} side - Panel identifier ("a", "b", or undefined)
 */
export function addLayer(id, url, side) {
  var mp = getMap(side);
  mp.addSource(id, {
    'type': 'raster',
    'tiles': [url],
    'tileSize': 256
  });
  mp.addLayer({
    'id': id,
    'source': id,
    'type': 'raster'
  }, 'dummy_layer');
  mp.setLayoutProperty(id, 'visibility', 'visible');
  mp.setPaintProperty(id, 'raster-opacity', 0.5);
}

/**
 * Update a raster tile layer (currently a no-op placeholder).
 * @param {string} fileName - Image file name (unused)
 * @param {string} id - Layer identifier (unused)
 * @param {Array} bounds - Bounding box (unused)
 * @param {string|object} colorbar - Colorbar config (unused)
 * @param {string} side - Panel identifier (unused)
 */
export function updateLayer(fileName, id, bounds, colorbar, side) {
}

/**
 * Create or update the legend element for a raster tile layer.
 * @param {object} mp - Map instance
 * @param {string} id - Layer identifier used to build legend element ID
 * @param {string|object} colorbar - Legend URL string or object with title and contour array
 */
function setLegend(mp, id, colorbar) {

  var legend = document.getElementById("legend" + id);
  var legendImage = document.getElementById("legend_image_" + id);

  // If legend does not exist, create it
  if (!legend) {
    var legend = document.createElement("div");
    legend.id = "legend" + id;
    legend.className = "legend_bottom_left";
    if (typeof colorbar === 'string' || colorbar instanceof String) {
      var legendImage = document.createElement('img');
      legendImage.id = "legend_image_" + id;
      legend.appendChild(legendImage);
    }
    document.body.appendChild(legend);
  }

  if (typeof colorbar === 'string' || colorbar instanceof String) {
    // Colorbar is a URL -- update legend image
    legendImage.src = colorbar;
    if (mp.getLayoutProperty(id, 'visibility') == 'visible') {
      legend.style.visibility = 'visible';
    } else {
      legend.style.visibility = 'hidden';
    }

  } else {
    // Colorbar is an object with title and contour

    // Clear legend
    legend.innerHTML = '';

    var newSpan = document.createElement('span');
    newSpan.class = 'title';
    newSpan.innerHTML = '<b>' + colorbar["title"] + '</b>';
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
    for (let i = 0; i < colorbar["contour"].length; i++) {
      let cnt = colorbar["contour"][i];
      var newI = document.createElement('i');
      newI.setAttribute('style', 'background:' + cnt["color"]);
      legend.appendChild(newI);
      var newSpan = document.createElement('span');
      newSpan.innerHTML = cnt["text"];
      legend.appendChild(newSpan);
      legend.appendChild(document.createElement("br"));
    }
    document.body.appendChild(legend);

    if (mp.getLayoutProperty(id, 'visibility') == 'visible') {
      legend.style.visibility = 'visible';
    } else {
      legend.style.visibility = 'hidden';
    }
  }
}

/**
 * Update the CSS position class of a layer's legend element.
 * @param {string} id - Layer identifier
 * @param {string} position - Position string ("bottom-left", "bottom-right", "top-left", "top-right")
 * @param {string} side - Panel identifier (unused, kept for API consistency)
 */
export function setLegendPosition(id, position, side) {
  var mp = getMap(side);
  var legend = document.getElementById("legend" + id);
  if (legend) {
    if (position == "bottom-left") {
      legend.className = "legend_bottom_left";
    } else if (position == "bottom-right") {
      legend.className = "overlay_legend";
    } else if (position == "top-left") {
      legend.className = "legend_top_left";
    } else if (position == "top-right") {
      legend.className = "legend_top_right";
    }
  }
}

/**
 * Set the raster opacity for a tile layer.
 * @param {string} id - Layer identifier
 * @param {number} opacity - Opacity value between 0 and 1
 * @param {string} side - Panel identifier ("a", "b", or undefined)
 */
export function setOpacity(id, opacity, side) {
  var mp = getMap(side);
  mp.setPaintProperty(id, 'raster-opacity', opacity);
}
