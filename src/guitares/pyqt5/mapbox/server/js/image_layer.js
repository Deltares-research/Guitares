function getMap(side) {
    // Return the map object for the given side
    if (side == "a") { return mapA }
    else if (side == "b") { return mapB }
    else { return map }
}

export function addLayer(fileName, id, bounds, colorbar, side) {
  var mp = getMap(side);
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
      setLegend(mp, id, colorbar);
  }    
}

export function updateLayer(fileName, id, bounds, colorbar, side) {
  var mp = getMap(side);
  mp.getSource(id).updateImage({
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
  if (legend) {
    legend.remove();
  }
  var legend     = document.createElement("div");
  legend.id        = "legend" + id;
  legend.className = "overlay_legend";
//        legend.className = legend_position;
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

export function setOpacity(id, opacity, side) {
  var mp = getMap(side);
  mp.setPaintProperty(id, 'raster-opacity', opacity);
}
