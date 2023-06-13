import {compareMap1} from './compare.js';
import {compareMap2} from './compare.js';

export function addLayer(fileName, id, bounds, colorbar, side) {

  console.log("Making side " + side + " id:" + id + " filename=" + fileName);
  console.log(bounds);

  if (side == "a") { var map = compareMap1 }
  if (side == "b") { var map = compareMap2 }

  map.addSource(id, {
    'type': 'image',
    'url': fileName,
    'coordinates': [
      [bounds[0][0], bounds[1][1]],
      [bounds[0][1], bounds[1][1]],
      [bounds[0][1], bounds[1][0]],
      [bounds[0][0], bounds[1][0]]
    ]
  });

  map.addLayer({
    'id': id,
    'source': id,
    'type': 'raster',
    'paint': {
      'raster-resampling': 'nearest'
    }
  });

  map.setPaintProperty(id,
    'raster-opacity',0.5
  );

  if (colorbar) {
    // Legend
    const legend     = document.createElement("div");
    legend.id        = "legend" + id;
    legend.className = "overlay_legend";
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
  }
}

export function updateLayer(fileName, id, bounds, colorbar, side) {

    console.log("Updating side " + side + " id:" + id + " filename=" + fileName);

    if (side == "a") { var map = compareMap1 }
    if (side == "b") { var map = compareMap2 }

    map.getSource(id).updateImage({
        'url': fileName,
        'coordinates': [
        [bounds[0][0], bounds[1][1]],
        [bounds[0][1], bounds[1][1]],
        [bounds[0][1], bounds[1][0]],
        [bounds[0][0], bounds[1][0]]
        ]
    });

    if (colorbar) {
        // Legend
        var legend = document.getElementById("legend" + id);
        if (legend) {
            legend.remove();
        }
        var legend     = document.createElement("div");
        legend.id        = "legend" + id;
        legend.className = "overlay_legend";
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
    }
}

export function setOpacity(id, opacity, side) {

    if (side == "a") { var map = compareMap1 }
    if (side == "b") { var map = compareMap2 }

    map.setPaintProperty(id,
      'raster-opacity', opacity
    );
}