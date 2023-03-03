import { map, featureClicked, mapboxgl } from '/js/main.js';

export function addLayer(id, data, fillColor, fillOpacity, lineColor, lineWidth, circleRadius, selectionOption) {

  let hoveredId = null;
  let selectedId = null
  let fillId = id + ".fill"
  let lineId = id + ".line"
  var selectedFeatures = []

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
  console.log('setting data in ' + id);
  console.log(data);
  var source = map.getSource(id);
  source.setData(data);
}
