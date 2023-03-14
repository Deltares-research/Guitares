import { map, featureClicked, mapboxgl } from '/js/main.js';

export function addLayer(id, data, lineColor, lineWidth, lineStyle, lineOpacity, fillColor, fillOpacity, circleRadius) {

  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  // Add a symbol layer
  map.addLayer({
    'id': id,
    'type': 'circle',
    'source': id,
    'paint': {
      'circle-color': fillColor,
      'circle-stroke-width': lineWidth,
      'circle-stroke-color': lineColor,
      'circle-radius': circleRadius,
      'circle-opacity': 0.75
    }
  });
};

export function setData(id, data) {
  // console.log('setting data in ' + id);
  // console.log(data);
  var source = map.getSource(id);
  source.setData(data);
}

export function setPaintProperties(id,
  lineColor,
  lineWidth,
  lineStyle,
  lineOpacity,
  fillColor,
  fillOpacity,                         
  circleRadius) {

  if (map.getLayer(id)) {  
    map.setPaintProperty(id, 'circle-stroke-color', lineColor);
    map.setPaintProperty(id, 'circle-color', fillColor);                  
    map.setPaintProperty(id, 'circle-radius', circleRadius);  
  }
}
