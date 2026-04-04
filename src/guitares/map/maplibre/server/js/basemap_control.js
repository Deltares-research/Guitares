/**
 * basemap_control.js
 *
 * Provides a custom MapLibre GL control that lets the user switch between
 * background map styles (satellite, streets, etc.) via a radio-button
 * popup attached to a layers icon in the map controls area.
 */

/**
 * Custom MapLibre GL control for selecting the background basemap layer.
 * Renders a button with a layers icon that toggles a radio-button list.
 */
export class BackgroundLayerSelector {
  /**
   * @param {Array<{id: string, name: string}>} layers - Available basemap layers.
   * @param {string} defaultStyle - ID of the initially selected style.
   */
  constructor(layers, defaultStyle) {
    this.layers = layers;
    this._container = document.createElement('div');
    this._container.className = 'maplibregl-ctrl';

    // Create the layers icon button
    const icon = document.createElement('button');
    icon.className = 'layers-icon';

    // Create the radio buttons container (hidden initially)
    const radioContainer = document.createElement('div');
    radioContainer.className = 'radio-container';
    this.layers.forEach(layer => {
      const label = document.createElement('label');
      const input = document.createElement('input');
      input.type = 'radio';
      input.name = 'background-layer';
      input.value = layer.id;
      input.addEventListener('change', () => {
        // Close the radio container when a layer is selected
        radioContainer.style.display = 'none';
        // And change the background layer
        setMapStyle(layer.id);
      });
      label.appendChild(input);
      label.appendChild(document.createTextNode(layer.name));
      radioContainer.appendChild(label);
    });

    // Toggle radio button with default style
    const defaultInput = radioContainer.querySelector(`input[value="${defaultStyle}"]`);
    if (defaultInput) {
      defaultInput.checked = true;
    }

    // Append the icon and the radio container to the control
    this._container.appendChild(icon);
    this._container.appendChild(radioContainer);

    // Add click event listener to toggle the radio container
    icon.addEventListener('click', () => {
      radioContainer.style.display = radioContainer.style.display === 'block' ? 'none' : 'block';
    });
  }

  /**
   * Called by MapLibre when the control is added to the map.
   * @param {Object} map - The MapLibre map instance.
   * @returns {HTMLElement} The control container element.
   */
  onAdd(map) {
    this._map = map;
    return this._container;
  }

  /**
   * Called by MapLibre when the control is removed from the map.
   */
  onRemove() {
    this._container.parentNode.removeChild(this._container);
    this._map = undefined;
  }
}

/**
 * Switch the map to a different basemap style while preserving all
 * application layers that sit above the dummy_layer_0 sentinel.
 *
 * The function merges the current map sources into the new style and
 * re-appends all application layers so they are not lost during the
 * style swap.
 *
 * @param {string} styleID - Key into the global `mapStyles` dictionary.
 */
export function setMapStyle(styleID) {
  console.log('Setting style to: ' + styleID);

  const currentStyle = map.getStyle();
  const newStyle = Object.assign({}, mapStyles[styleID]);

  // Ensure any sources from the current style are copied across to the new style
  newStyle.sources = Object.assign(
    {},
    currentStyle.sources,
    newStyle.sources
  );

  // Find the index of where to insert our layers to retain in the new style
  let labelIndex = currentStyle.layers.findIndex((el) => {
    return el.id == 'dummy_layer_0';
  });

  // Default to on top
  if (labelIndex === -1) {
    labelIndex = newStyle.layers.length;
  }

  const appLayers = currentStyle.layers.slice(labelIndex);

  newStyle.layers = [
    ...newStyle.layers,
    ...appLayers,
  ];

  map.setStyle(newStyle);
}
