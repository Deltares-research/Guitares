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

  let fillId = id + ".fill"
  let lineId = id + ".line"

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
      // Make the layer visible by default.
      'visibility': 'visible'
      }
  });

  // Legend
  //var legend     = document.createElement("div");
  //legend.id        = "legend" + id;
  //legend.className = "choropleth_legend";
  //legend.className = legend_position;
  //var newSpan = document.createElement('span');
  //newSpan.class = 'title';
  //newSpan.innerHTML = '<b>' + legend_title + '</b>';
  //legend.appendChild(newSpan);
  //legend.appendChild(document.createElement("br"));
  //for (let i = 0; i < legendItems.length; i++) {
  //let cnt = legendItems[i]
  //    var newI = document.createElement('i');
  //    newI.setAttribute('style','background:' + cnt["style"]);
  //    legend.appendChild(newI);
  //    var newSpan = document.createElement('span');
  //   newSpan.innerHTML = cnt["label"];
  //    legend.appendChild(newSpan);
  //    legend.appendChild(document.createElement("br"));
  //}
  //document.body.appendChild(legend);

  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  function onHover(e) {
    // Change the cursor style as a UI indicator.
    map.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      if (e.features[0].properties[hover_property]) {
        // Display a popup with the name of area
        popup.setLngLat(e.lngLat)
        .setText(hover_property + ": " 
        + numberWithCommas(e.features[0].properties[hover_property]) 
        )
        .addTo(map);
      }
    }
  }

  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  map.on('mousemove', fillId, onHover);

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  map.on('mouseleave', fillId, () => {
    popup.remove();
  });  

};

function absVal(integer) {
  return integer < 0 ? -integer : integer;
}

function numberWithCommas(x) {
  if (x == 0) {
    return x.toString()
  } else {
    return x.toString().replace(/\B(?<!\.\d*)(?=(\d{3})+(?!\d))/g, ",");
  }
}
