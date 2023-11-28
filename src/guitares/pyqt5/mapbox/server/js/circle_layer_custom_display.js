export function addLayer(
  id,
  data,
  hover_property,
  min_zoom,
  paint_dict,
  legendItems,
  legend_position,
  legend_title,
  color_no,
  bins,
  colors,
  color_labels,
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
  // add color bins
  if (color_no == 6) {
    mp.addLayer({
      'id': fillId,
      'type': 'fill',
      'source': id,
      'minzoom': min_zoom,
      'paint': {
        'fill-color': [
        'step',
        ['get', color_property],
        // This should all not be hard0-coded and provided with input
        colors[0],
        bins[0],
        colors[1],
        bins[1],
        colors[2],
        bins[2],
        colors[3],
        bins[3],
        colors[4],
        bins[4],
        colors[5],
      ],
      'fill-opacity': fillOpacity
      }
    });
  } else if (color_no == 4) {
    mp.addLayer({
      'id': fillId,
      'type': 'fill',
      'source': id,
      'minzoom': min_zoom,
      'paint': {
        'fill-color': [
        'step',
        ['get', color_property],
        // This should all not be hard0-coded and provided with input
        colors[0],
        bins[0],
        colors[1],
        bins[1],
        colors[2],
        bins[2],
        colors[3],
      ],
      'fill-opacity': fillOpacity
      }
    });
  }

  // Add a symbol layer
  map.addLayer({
    'id': id,
    'type': 'circle',
    'source': id,
    'minzoom': min_zoom,
    'paint': paint_dict
  });

  map.setLayoutProperty(id, 'visibility', 'visible');

  if (hover_property !== "") {

    // Create a popup, but don't add it to the map yet.
    const popup = new mapboxgl.Popup({
      closeButton: false,
      closeOnClick: false
    });

    if (hover_property) {

      map.on('mouseenter', id, (e) => {

        // Change the cursor style as a UI indicator.
        map.getCanvas().style.cursor = 'pointer';

        // Copy coordinates array.
        const coordinates = e.features[0].geometry.coordinates.slice();

        // Ensure that if the map is zoomed out such that multiple
        // copies of the feature are visible, the popup appears
        // over the copy being pointed to.
        while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
          coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360;
        }

        // Display a popup 
        popup.setLngLat(e.lngLat)
          .setText(hover_property + ": " + e.features[0].properties[hover_property])
          .addTo(map);
      });

      map.on('mouseleave', id, () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
      });
    }
  };

  // Legend
  if (color_no == 6) {
    var legendItems = [
      { style: colors[0], label: color_labels[0]},
      { style: colors[1], label: color_labels[1]},
      { style: colors[2], label: color_labels[2]},
      { style: colors[3], label: color_labels[3]},
      { style: colors[4], label: color_labels[4]},
      { style: colors[5], label: color_labels[5]},
    ];
  } else if (color_no == 4) {
    var legendItems = [
      { style: colors[0], label: color_labels[0]},
      { style: colors[1], label: color_labels[1]},
      { style: colors[2], label: color_labels[2]},
      { style: colors[3], label: color_labels[3]},
    ];
  }

  // Legend
  var legend     = document.createElement("div");
  legend.id        = "legend" + id;
  //legend.className = "choropleth_legend";
  legend.className = legend_position;
  var newSpan = document.createElement('span');
  newSpan.class = 'title';
  newSpan.innerHTML = '<b>' + legend_title + '</b>';
  legend.appendChild(newSpan);
  legend.appendChild(document.createElement("br"));
  for (let i = 0; i < legendItems.length; i++) {
  let cnt = legendItems[i]
      var newI = document.createElement('i');
      newI.setAttribute('style','background:' + cnt["style"]);
      legend.appendChild(newI);
      var newSpan = document.createElement('span');
      newSpan.innerHTML = cnt["label"];
      legend.appendChild(newSpan);
      legend.appendChild(document.createElement("br"));
  }
  document.body.appendChild(legend);

};

export function setData(id, data) {
  var source = map.getSource(id);
  source.setData(data);
}

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
