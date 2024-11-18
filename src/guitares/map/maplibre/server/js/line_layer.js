export function addLayer(id, data,   
  lineColor, 
  lineWidth, 
  lineOpacity, 
  fillColor, 
  fillOpacity, 
  circleRadius){

  let lineId = id + ".line"
  let circleId = id + ".circle"

  // Always remove old layer and source first to avoid errors
  if (map.getLayer(lineId)) {
    map.removeLayer(lineId);
  }
  if (map.getLayer(circleId)) {
    map.removeLayer(circleId);
  }
  var mapSource = map.getSource(id);
  if(typeof mapSource !== 'undefined') {
    map.removeSource(id);
  }
  
  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': lineColor,
      'line-width': lineWidth,
      'line-opacity': lineOpacity,
     }
  });
  
  if (circleRadius>0) {
    map.addLayer({
      'id': circleId,
      'type': 'circle',
      'source': id,
      'paint': {
        'circle-color': fillColor,
        'circle-stroke-width': lineWidth,
        'circle-stroke-color': lineColor,
        'circle-stroke-opacity': lineOpacity,
        'circle-radius': circleRadius,
        'circle-opacity': fillOpacity
      }
    });
  }
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
    map.setPaintProperty(id + ".circle", 'circle-stroke-color', lineColor);
    map.setPaintProperty(id + ".circle", 'circle-stroke-width', lineWidth);
    map.setPaintProperty(id + ".circle", 'circle-stroke-opacity', lineOpacity);
    map.setPaintProperty(id + ".circle", 'circle-color', fillColor);   
    map.setPaintProperty(id + ".circle", 'circle-opacity', fillOpacity);                
    map.setPaintProperty(id + ".circle", 'circle-radius', circleRadius);  

    map.setPaintProperty(id + ".line", 'line-color', lineColor);
    map.setPaintProperty(id + ".line", 'line-width', lineWidth);               
 
  }
}