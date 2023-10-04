import {make_html_table} from '/js/main.js';

export function addLayer(
  id, 
  data, 
  min_zoom, 
  hover_properties, // do more than one
  color_property,
  lineColor,
  lineWidth,
  lineOpacity,
  fillOpacity,
  scaler,
  legend_title,
  unit,
  legend_position,
  side,
  color_type,
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
    // promoteId: hover_property
  });
 
  if (color_type == 'damage') {
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
        '#FFFFFF',
        0.000001*scaler,
        '#FEE9CE',
        0.06*scaler,
        '#FDBB84',
        0.2*scaler,
        '#FC844E',
        0.4*scaler,
        '#E03720',
        1*scaler,
        '#860000',
      ],
      'fill-opacity': fillOpacity
      }
    });
  } else if (color_type == 'flooding') {
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
        '#BED2FF',
        1 * scaler,
        '#B4D79E',
        3 * scaler,
        '#1F80B8',
        5 * scaler,
        '#081D58',
      ],
      'fill-opacity': fillOpacity
      }
    });
  }


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
  if (color_type == 'damage') {
    var legendItems = [
      { style: '#FFFFFF', label: '0 '},
      { style: '#FEE9CE', label: unit + '0 - ' + unit + numberWithCommas(0.06*scaler)},
      { style: '#FDBB84', label: unit + numberWithCommas(0.06*scaler) + ' - ' + unit + numberWithCommas(0.2*scaler)},
      { style: '#FC844E', label: unit + numberWithCommas(0.2*scaler) + ' - ' + unit + numberWithCommas(0.4*scaler)},
      { style: '#E03720', label: unit + numberWithCommas(0.4*scaler) + ' - ' + unit + numberWithCommas(1*scaler)},
      { style: '#860000', label: '> ' + unit + numberWithCommas(1*scaler)},
    ];
  } else if (color_type == 'flooding') {
    var legendItems = [
      { style: '#081D58', label: '> ' + numberWithCommas(5*scaler)},
      { style: '#1F80B8', label: numberWithCommas(3*scaler) + ' - ' + numberWithCommas(5*scaler)},
      { style: '#B4D79E', label: numberWithCommas(1*scaler) + ' - ' + numberWithCommas(3*scaler)},
      { style: '#BED2FF', label: '< ' + numberWithCommas(1*scaler)},
    ];
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
    closeOnClick: false,
    maxWidth: 'none'
  });

  function onHover(e) {
    // Change the cursor style as a UI indicator.
    mp.getCanvas().style.cursor = 'pointer';
    if (e.features.length > 0) {
      // Display a popup with the name of area
      popup.setLngLat(e.lngLat)
      .setHTML(make_html_table(hover_properties, e, true))
      .addTo(mp);
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
