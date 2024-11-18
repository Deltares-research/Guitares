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
          .setText(hover_property + ": " + (e.features[0].properties[hover_property])
          + " " + unit)
          .addTo(map);
      });

      map.on('mouseleave', id, () => {
        map.getCanvas().style.cursor = '';
        popup.remove();
      });
    }
  };

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
      newI.setAttribute('style','background:' + cnt["style"] + '; border-radius: 50%; width: 10px; height: 10px; display: inline-block;');
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
