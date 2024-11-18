function getMap(side) {
    // Return the map object for the given side
    if (side == "a") { return mapA }
    else if (side == "b") { return mapB }
    else { return map }
}

export function addLayer(fileName, id, bounds, colorbar, side) {
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
    'url': fileName,
    'coordinates': [
      [bounds[0][0], bounds[1][1]],
      [bounds[0][1], bounds[1][1]],
      [bounds[0][1], bounds[1][0]],
      [bounds[0][0], bounds[1][0]]
    ]
  });
  mp.addLayer({
    'id': id,
    'source': id,
    'type': 'raster',
    'paint': {
      'raster-resampling': 'nearest'
    }
  }, 'dummy_layer');
  mp.setLayoutProperty(id, 'visibility', 'visible');    
  mp.setPaintProperty(id, 'raster-opacity',0.5);
  if (colorbar) {
    // If colorbar is a string, then it is a URL and we add it as an image
    setLegend(mp, id, colorbar);
  }
}

export function updateLayer(fileName, id, bounds, colorbar, side) {
  var mp = getMap(side);
  
  // If the layer does not exist, add it
  if (!mp.getLayer(id)) {
    // console.log("Layer " + id + " does not exist, adding it instead of updating it");
    mp.addLayer(fileName, id, bounds, colorbar, side);
    return;
  }

  // If the layer is not visible, do not update it
  if (mp.getLayoutProperty(id, 'visibility') !== 'visible') {
    // console.log("Layer " + id + " is not visible, so it won't be updated");
    return;
  }
  
  // If the source does not exist, add it
  if (!mp.getSource(id)) {
    mp.addSource(id, {
      'type': 'image',
      'url': fileName,
      'coordinates': [
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][1]],
        [bounds[0][1], bounds[1][0]],
        [bounds[0][0], bounds[1][0]]
      ]
    });
  }

  var source = mp.getSource(id);
  // If the source does not have updateImage method, do not update it
  if (typeof source.updateImage !== 'function') {
    // console.log("Source does not have updateImage method");
    return;
  }

  // Update the image
  source.updateImage({
    'url': fileName,
    'coordinates': [
      [bounds[0][0], bounds[1][1]],
      [bounds[0][1], bounds[1][1]],
      [bounds[0][1], bounds[1][0]],
      [bounds[0][0], bounds[1][0]]
    ]
  });

  if (colorbar) {
    setLegend(mp, id, colorbar);
  }
}

function setLegend(mp, id, colorbar) {

  // Legend

  var legend = document.getElementById("legend" + id);
  var legendImage = document.getElementById("legend_image_" + id);

  // If legend does not exist, create it
  if (!legend) {
    // Legend does not exist yet, so create it
    var legend     = document.createElement("div");
    legend.id        = "legend" + id;
    legend.className = "legend_bottom_left";  
//    legend.className = "overlay_legend";  
    if (typeof colorbar === 'string' || colorbar instanceof String) {
      var legendImage = document.createElement('img');
      legendImage.id = "legend_image_" + id;
      legend.appendChild(legendImage);
    }  
    document.body.appendChild(legend);
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

    // Clear legend
    legend.innerHTML = '';

    var newSpan = document.createElement('span');
    newSpan.class = 'title';
    newSpan.innerHTML = '<b>' + colorbar["title"] + '</b>';
    legend.appendChild(newSpan);
    legend.appendChild(document.createElement("br"));
    for (let i = 0; i < colorbar["contour"].length; i++) {
      let cnt = colorbar["contour"][i]
      var newI = document.createElement('i');
      newI.setAttribute('style','background:' + cnt["color"]);
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
}

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

export function setOpacity(id, opacity, side) {
  var mp = getMap(side);
  mp.setPaintProperty(id, 'raster-opacity', opacity);
}
