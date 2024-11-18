export function addLayer(
  id, 
  data, 
  min_zoom, 
  hover_property, // do more than one
  color_property,
  lineColor,
  lineWidth,
  lineOpacity,
  fillOpacity,
  legend_title,
  unit,
  legend_position,
  side,
  bins,
  colors,
  color_labels,
  ) {

  var mp = getMap(side);

  let fillId = id + ".fill"
  let lineId = id + ".line"

  // Always remove old layers first to avoid errors
  if (mp.getLayer(fillId)) {
    mp.removeLayer(fillId);
  }
  if (mp.getLayer(lineId)) {
    mp.removeLayer(lineId);
  }
  if (mp.getSource(id)) {
    mp.removeSource(id);
  }
  var legend = document.getElementById("legend" + id);
  if (legend) {
    legend.parentNode.removeChild(legend);
  }

  mp.addSource(id, {
    type: 'geojson',
    data: data, 
    promoteId: hover_property
  });
 
  let fillColor = ['step', ['get', color_property]];

  // Add colors and bins to fill-color array
  for (let i = 0; i < colors.length; i++) {
    fillColor.push(colors[i]);
    if (bins[i] !== undefined) {
      fillColor.push(bins[i]);
    }
  }

  // Add layer
  mp.addLayer({
    'id': fillId,
    'type': 'fill',
    'source': id,
    'minzoom': min_zoom,
    'paint': {
      'fill-color': fillColor,
      'fill-opacity': fillOpacity
    }
  });

  mp.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'minzoom': min_zoom,
    'paint': {
      'line-color': lineColor,
      'line-width': lineWidth,
      'line-opacity': lineOpacity
     },
     'layout': {
      // Make the layer visible by default.
      'visibility': 'visible'
      }
  });

  // Legend
  var legendItems = [];
  for (let i = 0; i < colors.length; i++) {
    legendItems.push({ style: colors[i], label: color_labels[i]});
  }

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

  // Create a popup, but don't add it to the map yet.
  const popup = new mapboxgl.Popup({
    closeButton: false,
    closeOnClick: false
  });

  function onHover(e) {
    // Change the cursor style as a UI indicator.
    mp.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      if (e.features[0].properties[hover_property]) {
        // Display a popup with the name of area
        popup.setLngLat(e.lngLat)
        .setText(hover_property + ": " 
        + numberWithCommas(e.features[0].properties[hover_property]) 
        + " " + unit)
        .addTo(mp);
      }
    }
  }

  // When the user moves their mouse over the fill layer, we'll update the
  // feature state for the feature under the mouse.
  mp.on('mousemove', fillId, onHover);

  // When the mouse leaves the fill layer, update the feature state of the
  // previously hovered feature.
  mp.on('mouseleave', fillId, () => {
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

function getMap(side) {
  // Return the map object for the given side
  if (side == "a") { return mapA }
  else if (side == "b") { return mapB }
  else { return map }
}


// export function activate(id,
//                          lineColor,
//                          fillColor,                   
//                          lineColorActive,
//                          fillColorActive) {

//   const features = map.querySourceFeatures(id, {sourceLayer: id});
//   for (let i = 0; i < features.length; i++) {
//     map.setFeatureState(
//       { source: id, id: features[i].id },
//       { active: true }
//     );
//   }
//   if (map.getLayer(id)) {  
//     map.setPaintProperty(id, 'circle-stroke-color', ['case',
//       ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
//       lineColorActive,
//       lineColor]);                          
//     map.setPaintProperty(id, 'circle-color', ['case',
//       ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
//       fillColorActive,
//       fillColor]);                          
//   }                           
// }

// export function deactivate(id,
//   lineColor,
//   lineWidth,
//   lineStyle,
//   lineOpacity,
//   fillColor,
//   fillOpacity,                         
//   lineColorActive,
//   fillColorActive) {

//   const features = map.querySourceFeatures(id, {sourceLayer: id});
//   for (let i = 0; i < features.length; i++) {
//     map.setFeatureState(
//       { source: id, id: i },
//       { active: false }
//     );
//   }  
//   if (map.getLayer(id)) {  
//     map.setPaintProperty(id, 'circle-stroke-color', ['case',
//       ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
//       lineColorActive,
//       lineColor]);                          
//     map.setPaintProperty(id, 'circle-color', ['case',
//       ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
//       fillColorActive,
//       fillColor]);                          
//     map.setPaintProperty(id, 'circle-radius', ['case',
//       ['any', ['boolean', ['feature-state', 'selected'], false], ['boolean', ['feature-state', 'hover'], false]],
//       circleRadiusActive,
//       circleRadius]);                          
//   }
// }
