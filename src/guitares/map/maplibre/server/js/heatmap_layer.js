import { getMap } from './utils.js';

/**
 * Add a heatmap layer driven by a density property.
 * @param {string} id - Unique layer/source identifier
 * @param {object} data - GeoJSON data for the source
 * @param {number} max_zoom - Maximum zoom level for the heatmap layer
 * @param {string} density_property - Feature property name used for heatmap weight
 * @param {string} side - Panel identifier ("a", "b", or undefined)
 */
export function addLayer(id, data, max_zoom, density_property, side) {

  var mp = getMap(side);

  // Always remove old layers first to avoid errors
  if (mp.getLayer(id)) {
    mp.removeLayer(id);
  }
  if (mp.getSource(id)) {
    mp.removeSource(id);
  }

  mp.addSource(id, {
    type: 'geojson',
    data: data,
  });

  mp.addLayer({
    id: id,
    type: 'heatmap',
    source: id,
    maxzoom: max_zoom,
    paint: {
      // Increase weight as the density property increases
      'heatmap-weight': {
        property: density_property,
        type: 'exponential',
        stops: [
          [0, 0],
          [2, 1]
        ]
      },
      // Increase intensity as zoom level increases
      'heatmap-intensity': {
        stops: [
          [10, 1],
          [14, 3]
        ]
      },
      // Increase radius as zoom increases
      'heatmap-radius': {
        stops: [
          [10, 2],
          [14, 10]
        ]
      },
      // Decrease opacity to transition into the circle layer
      'heatmap-opacity': {
        default: 1,
        stops: [
          [10, 1],
          [max_zoom, 0.5]
        ]
      }
    }
  });
}
