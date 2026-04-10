/**
 * Add a deck.gl TileLayer that renders topo-bathymetry PNG tiles.
 * Shallow areas (depth > 0 and zb > -2) are colored blue; all other
 * pixels are made transparent.
 * @param {string} id - Layer identifier
 * @param {Object} data - Unused (tile URL is hardcoded)
 */
export function addLayer(id, data) {

  var tileSize = 256;

  var tileLayer = new deck.MapboxLayer({
    type: deck.TileLayer,
    id: id,
    minZoom: 0,
    maxZoom: 13,
    tileSize: 256,
    data: 'topobathy/{z}/{x}/{y}.png',
    getTileData: async function (tile) {
      const rgb = await getPromise(tile.url);
      const arrLength = 256 * 256 * 4;
      for (let i = 0; i < arrLength / 4; i++) {
        const zb = -20000.0 + (rgb.data[i * 4] * 65536 + rgb.data[(i * 4) + 1] * 256 + rgb.data[(i * 4) + 2]) * 0.01;
        const depth = 10.0 - zb;
        if (depth > 0.0 && zb > -2.0) {
          rgb.data[i * 4] = 0;
          rgb.data[(i * 4) + 1] = 0;
          rgb.data[(i * 4) + 2] = 255;
        } else {
          rgb.data[(i * 4) + 3] = 0;
        }
      }
      return createImageBitmap(rgb);
    },

    renderSubLayers: props => {
      const {
        data,
        bbox: {west, south, east, north}
      } = props.tile;
      return new deck.BitmapLayer(props, {
        data: null,
        image: props.tile.data,
        bounds: [west, south, east, north]
      });
    }
  });

  console.log("Adding tiles ...");
  map.addLayer(tileLayer);
  map.getLayer(id)._deck_layer = tileLayer;
}

/**
 * Load an image from a URL and return its pixel data as an ImageData object.
 * @param {string} url - Image URL to fetch
 * @returns {Promise<ImageData>} Resolved with the pixel data
 */
function getPromise(url) {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = function () {
      var canvas = document.createElement('canvas');
      canvas.width = img.width;
      canvas.height = img.height;
      var context = canvas.getContext('2d');
      context.drawImage(img, 0, 0);
      var pixels = context.getImageData(0, 0, img.width, img.height);
      resolve(pixels);
    };
    img.onerror = function () {
      reject(null);
    };
    img.src = url;
  });
}

/**
 * Update the tile data URL for an existing deck.gl tile layer.
 * @param {string} id - Layer identifier
 * @param {string} data - New tile URL template
 */
export function setData(id, data) {
  var deck_layer = map.getLayer(id)._deck_layer;
  deck_layer.setProps({data: data});
}
