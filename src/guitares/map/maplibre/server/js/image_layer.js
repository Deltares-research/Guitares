function getMap(side) {
    // Return the map object for the given side
    if (side == "a") { return mapA }
    else if (side == "b") { return mapB }
    else { return map }
}

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
    mp.setPaintProperty(id, 'raster-opacity', 1.0); // default opacity
  }

}

function setLegend(mp, id, colorbar, legend_position) {

  // Legend
  var legend = document.getElementById("legend" + id);
  var legendImage = document.getElementById("legend_image_" + id);

//  // Clear the legend and everything in itm (it will be recreated)
//  if (legend) {
//    legend.innerHTML = '';
//  }

//  legendImage = document.getElementById("legend_image_" + id);
//  if (legendImage) {
//    legendImage.src = "";
//  }  

  // If legend does not exist, create it
  if (!legend) {
    // Legend does not exist yet, so create it
    var legend     = document.createElement("div");
    legend.id        = "legend" + id;
    legend.className = "legend_bottom_left";
    // if (typeof colorbar === 'string' || colorbar instanceof String) {
    var legendImage = document.createElement('img');
    legendImage.id = "legend_image_" + id;
    legend.appendChild(legendImage);
    // }
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
  // and just show the image. Otherwise, we want to set the src
  // of the image to ""
  if (typeof colorbar === 'string' || colorbar instanceof String) {
    // Colorbar is a URL
    // Remove all spans and i elements
    var spans = legend.getElementsByTagName('span');
    while (spans.length > 0) {
      spans[0].parentNode.removeChild(spans[0]);
    }
    var is = legend.getElementsByTagName('i');
    while (is.length > 0) {
      is[0].parentNode.removeChild(is[0]);
    }
    legend.innerHTML = '';

  } else {
    // Colorbar is an object with title and contour
    // Remove the image
    legendImage.src = "";
  }



  if (typeof colorbar === 'string' || colorbar instanceof String) {
    // Colorbar is a URL
    // Update legend image
    legendImage.src = colorbar;
    // Now check for layer visibility and update legend accordingly
    if (mp.getLayoutProperty(id, 'visibility') == 'visible') {
      legend.style.visibility = 'visible';
    } else {
      legend.style.visibility = 'hidden';
    }

  } else {

    // Colorbar is an object with title and contour

    // Clear legendImage.src
    legendImage.src = "";

    legend.innerHTML = '';
    legend.classList.add("legend"); // ensure it has base legend class

    var newSpan = document.createElement('span');
    newSpan.classList.add('title'); // correct way to set class
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

    // Now check for layer visibility and update legend accordingly
    if (mp.getLayoutProperty(id, 'visibility') == 'visible') {
      legend.style.visibility = 'visible'; 
    } else {
      legend.style.visibility = 'hidden';
    }

  }

  setLegendPosition({id: id, position: legend_position});

}

export function setLegendPosition({id = undefined, position = "bottom-left" } = {}) {
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.classList.remove("bottom-left", "bottom-right", "top-left", "top-right", "bottom", "top", "left", "right");
    legend.classList.add("legend");
    legend.classList.add(position); // position = "bottom-left", "bottom-right", etc.
  } 
}

export function setOpacity({
    id = undefined,
    opacity = 1.0,
    side = undefined
  } = {}) {
  var mp = getMap(side);
  mp.setPaintProperty(id, 'raster-opacity', opacity);
}
