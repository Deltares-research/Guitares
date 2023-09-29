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
  scaler,
  legend_title,
  unit,
  legend_position,
  side
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
      '#EEF5E8',
      0.000001*scaler,
      '#FEE3C4',
      0.02*scaler,
      '#FED7AB',
      0.05*scaler,
      '#FCCC96',
      0.1*scaler,
      '#F8AB54',
      0.2*scaler,
      '#FB9420',
      0.4*scaler,
      '#FB2807',
      1*scaler,
      '#B8220A',
    ],
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
  var legendItems = [
    { style: '#EEF5E8', label: '0 ' + unit},
    { style: '#FEE3C4', label: '0 - ' + numberWithCommas(0.02*scaler) + ' ' + unit},
    { style: '#FED7AB', label: numberWithCommas(0.02*scaler) + ' - ' + numberWithCommas(0.05*scaler) + ' ' + unit},
    { style: '#FCCC96', label: numberWithCommas(0.05*scaler) + ' - ' + numberWithCommas(0.1*scaler) + ' ' + unit},
    { style: '#F8AB54', label: numberWithCommas(0.1*scaler) + ' - ' + numberWithCommas(0.2*scaler) + ' ' + unit},
    { style: '#FB9420', label: numberWithCommas(0.2*scaler) + ' - ' + numberWithCommas(0.4*scaler) + ' ' + unit},
    { style: '#FB2807', label: numberWithCommas(0.4*scaler) + ' - ' + numberWithCommas(1*scaler) + ' ' + unit},
    { style: '#B8220A', label: '> ' + numberWithCommas(1*scaler) + ' ' + unit},
  ];
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
