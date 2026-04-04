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
 * Add a raster image layer initialized with a blank pixel.
 * @param {object} options - Named parameters
 * @param {string} options.id - Unique layer/source identifier
 * @param {string} options.side - Panel identifier ("a", "b", or undefined)
 */
export function addLayer({id = undefined, side = undefined} = {}) {

  const blankPixel =
    "data:image/png;base64," +
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR4nGNgYAAAAAMAASsJTYQAAAAASUVORK5CYII=";

  var mp = getMap(side);

  // Always remove the layer first to avoid an error
  if (mp.getLayer(id)) {
    mp.removeLayer(id);
  }

  if (mp.getSource(id)) {
    mp.removeSource(id);
  }

  mp.addSource(id, {
    'type': 'image',
    'url': blankPixel,
    'coordinates': [
      [-1.0, 1.0],
      [-1.0, -1.0],
      [1.0, -1.0],
      [1.0, 1.0]
    ]
  });

  mp.addLayer({
    'id': id,
    'source': id,
    'type': 'raster',
    'paint': {
      'raster-resampling': 'nearest'
    }
  }, 'dummy_layer_1');
  mp.setLayoutProperty(id, 'visibility', 'visible');
  mp.setPaintProperty(id, 'raster-opacity', 0.5);
}

/**
 * Update an existing raster image layer with new image data, legend, and opacity.
 * @param {object} options - Named parameters
 * @param {string} options.filename - URL of the new image
 * @param {string} options.id - Layer/source identifier
 * @param {Array} options.bounds - Bounding box as [[west, east], [south, north]]
 * @param {string|object} options.colorbar - Legend URL string or contour config object
 * @param {string} options.legend_position - Legend position (e.g. "bottom-left")
 * @param {number} options.opacity - Raster opacity between 0 and 1
 * @param {string} options.side - Panel identifier ("a", "b", or undefined)
 */
export function updateLayer({filename = undefined,
                             id = undefined,
                             bounds = undefined,
                             colorbar = undefined,
                             legend_position = "bottom-left",
                             opacity = 1.0,
                             side = undefined} = {}) {

  var mp = getMap(side);

  // If the layer does not exist, add it (this should never happen)
  if (!mp.getLayer(id)) {
    addLayer({id: id, side: side});
  }

  var source = mp.getSource(id);

  // Update the image
  source.updateImage({
    'url': filename,
    'coordinates': [
      [bounds[0][0], bounds[1][1]],
      [bounds[0][1], bounds[1][1]],
      [bounds[0][1], bounds[1][0]],
      [bounds[0][0], bounds[1][0]]
    ]
  });

  if (colorbar) {
    setLegend(mp, id, colorbar, legend_position);
  }

  // Set the opacity of the layer
  if (opacity !== undefined) {
    mp.setPaintProperty(id, 'raster-opacity', opacity);
  } else {
    mp.setPaintProperty(id, 'raster-opacity', 1.0);
  }
}

/**
 * Create or update the legend element for a raster image layer.
 * @param {object} mp - Map instance
 * @param {string} id - Layer identifier used to build legend element ID
 * @param {string|object} colorbar - Legend URL string or object with title and contour array
 * @param {string} legend_position - CSS position class for the legend
 */
function setLegend(mp, id, colorbar, legend_position) {

  var legend = document.getElementById("legend" + id);
  var legendImage = document.getElementById("legend_image_" + id);

  // If legend does not exist, create it
  if (!legend) {
    var legend = document.createElement("div");
    legend.id = "legend" + id;
    legend.className = "legend_bottom_left";
    var legendImage = document.createElement('img');
    legendImage.id = "legend_image_" + id;
    legend.appendChild(legendImage);
    document.body.appendChild(legend);
  }

  if (!legendImage) {
    // Legend image does not exist yet, so create it
    var legendImage = document.createElement('img');
    legendImage.id = "legend_image_" + id;
    legend.appendChild(legendImage);
  }

  // If colorbar is a string, it is a URL to an image
  // so we want to remove all the spans and i elements
  // and just show the image. Otherwise, clear the image src.
  if (typeof colorbar === 'string' || colorbar instanceof String) {
    // Remove all spans and i elements
    var spans = legend.getElementsByTagName('span');
    while (spans.length > 0) {
      spans[0].parentNode.removeChild(spans[0]);
    }
    var is = legend.getElementsByTagName('i');
    while (is.length > 0) {
      is[0].parentNode.removeChild(is[0]);
    }
    var brs = legend.getElementsByTagName('br');
    while (brs.length > 0) {
      brs[0].parentNode.removeChild(brs[0]);
    }

  } else {
    // Colorbar is an object with title and contour -- remove the image
    legendImage.src = "";
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

    legendImage.src = "";

    legend.innerHTML = '';
    legend.classList.add("legend");

    var newSpan = document.createElement('span');
    newSpan.classList.add('title');
    newSpan.innerHTML = '<b>' + colorbar["title"] + '</b>';
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));

    for (let i = 0; i < colorbar["contour"].length; i++) {
      let cnt = colorbar["contour"][i];
      var newI = document.createElement('i');
      newI.setAttribute(
        'style',
        'background:' + cnt["color"]
      );
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

  setLegendPosition({id: id, position: legend_position});
}

/**
 * Update the CSS position classes of a layer's legend element.
 * @param {object} options - Named parameters
 * @param {string} options.id - Layer identifier
 * @param {string} options.position - Position string (e.g. "bottom-left", "top-right")
 */
export function setLegendPosition({id = undefined, position = "bottom-left"} = {}) {
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.classList.remove("bottom-left", "bottom-right", "top-left", "top-right", "bottom", "top", "left", "right");
    legend.classList.add("legend");
    legend.classList.add(position);
  }
}

/**
 * Set the raster opacity for a raster image layer.
 * @param {object} options - Named parameters
 * @param {string} options.id - Layer identifier
 * @param {number} options.opacity - Opacity value between 0 and 1
 * @param {string} options.side - Panel identifier ("a", "b", or undefined)
 */
export function setOpacity({
    id = undefined,
    opacity = 1.0,
    side = undefined
  } = {}) {
  var mp = getMap(side);
  mp.setPaintProperty(id, 'raster-opacity', opacity);
}
