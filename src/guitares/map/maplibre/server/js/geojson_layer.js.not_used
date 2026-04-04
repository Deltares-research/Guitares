import { map } from '/js/main.js';

export function addLayer(id, data, symbol_path) {

  let fillId = id + ".fill"
  let lineId = id + ".line"
  let circleId = id + ".circle"
  console.log(data)


  map.addSource(id, {
    type: 'geojson',
    data: data
  });

  map.addLayer({
    'id': circleId,
    'type': 'circle',
    'source': id,
    'paint': {
      'circle-radius': 3,
      'circle-stroke-width': 1.5,
      'circle-color': 'red',
      'circle-stroke-color': 'white'
    }
  });

  map.addLayer({
    'id': lineId,
    'type': 'line',
    'source': id,
    'layout': {},
    'paint': {
      'line-color': '#000',
      'line-width': 1
     }
  });

  map.addLayer({
    'id': fillId,
    'type': 'fill',
    'source': id,
    'paint': {
      'fill-color': 'transparent',
      'fill-outline-color': 'transparent'
    }
  });

};

export function setData(id, data) {
  console.log('setting data in ' + id);
  console.log(data);
  var source = map.getSource(id);
  source.setData(data);
}
