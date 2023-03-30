import { map} from '/js/main.js';

export function addLayer(id, 
  data, 
  max_zoom, 
  density_property, 
) {

  map.addSource(id, {
    type: 'geojson',
    data: data, 
  });

  map.addLayer(
    {
      id: id,
      type: 'heatmap',
      source: id,
      maxzoom: max_zoom,
      paint: {
        // increase weight as diameter breast height increases
        'heatmap-weight': {
          property: density_property,
          type: 'exponential',
          stops: [
            [0, 0],
            [2, 1]
          ]
        },
        // // increase intensity as zoom level increases
        'heatmap-intensity': {
          stops: [
            [10, 1],
            [14, 3]
          ]
        },
        // assign color values be applied to points depending on their density
        // increase radius as zoom increases
        'heatmap-radius': {
          stops: [
            [10, 2],
            [14, 10]
          ]
        },
        // decrease opacity to transition into the circle layer
        'heatmap-opacity': {
          default: 1,
          stops: [
            [10, 1],
            [max_zoom, 0.5]
          ]
        }
      }
    },
  );

};

