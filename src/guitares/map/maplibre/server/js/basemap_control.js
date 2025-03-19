// Create a custom control for the background layer selector
export class BackgroundLayerSelector {
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
            // console.log(layer.id)
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

        // Add click event listener to the icon
        icon.addEventListener('click', () => {
            radioContainer.style.display = radioContainer.style.display === 'block' ? 'none' : 'block';
        });

        // // Toggle the visibility of the radio container on hover
        // icon.addEventListener('mouseenter', () => {
        //     console.log('mouseenter');
        //     radioContainer.style.display = 'block';
        // });

        // icon.addEventListener('mouseleave', () => {
        //     console.log('mouseleave');
        //     radioContainer.style.display = 'none';
        // });

        // icon.addEventListener('mouseover', () => {
        //     console.log('mouseover');
        //     radioContainer.style.display = 'block';  // Show the container on hover
        // });

        // icon.addEventListener('mouseout', () => {
        //     console.log('mouseout');
        //     radioContainer.style.display = 'none';  // Hide the container when mouse leaves
        // });

    }

    onAdd(map) {
        this._map = map;
        return this._container;
    }

    onRemove() {
        this._container.parentNode.removeChild(this._container);
        this._map = undefined;
    }
}


export function setMapStyle(styleID) {

  console.log('Setting style to: ' + styleID);

  const currentStyle = map.getStyle();
  const newStyle = Object.assign({}, mapStyles[styleID]);

  // ensure any sources from the current style are copied across to the new style
  newStyle.sources = Object.assign(
    {},
    currentStyle.sources,
    newStyle.sources
  );

  // find the index of where to insert our layers to retain in the new style
  let labelIndex = currentStyle.layers.findIndex((el) => {
    return el.id == 'dummy_layer_0';
  });

  // default to on top
  if (labelIndex === -1) {
    // This should never happen !
    labelIndex = newStyle.layers.length;
  }

  // const appLayers = currentStyle.layers.slice(labelIndex, -1);
  const appLayers = currentStyle.layers.slice(labelIndex);

  // console.log('nr appLayers: ' + appLayers.length);

  // // Loop through app layers and print id
  // for (var layer in appLayers) {
  //   console.log("app layer id: " + appLayers[layer].id);
  // }
  
  newStyle.layers = [
    ...newStyle.layers,
    ...appLayers,
  ];

  // // Print layers in new style
  // for (var layer in newStyle.layers) {
  //   console.log("new layerId: " + newStyle.layers[layer].id);
  // }

  map.setStyle(newStyle);

}
