/**
 * basemap_control.js
 *
 * Provides a custom MapLibre GL control that lets the user switch between
 * background map styles via a thumbnail grid popup.
 */

/**
 * Custom MapLibre GL control for selecting the background basemap layer.
 * Renders a button with a layers icon that toggles a scrollable grid
 * of style thumbnails.
 */
export class BackgroundLayerSelector {
  /**
   * @param {Array<{id: string, name: string}>} layers - Available basemap layers.
   * @param {string} defaultStyle - ID of the initially selected style.
   */
  constructor(layers, defaultStyle) {
    this.layers = layers;
    this._selectedId = defaultStyle;
    this._container = document.createElement("div");
    this._container.className = "maplibregl-ctrl";

    // Layers icon button
    const icon = document.createElement("button");
    icon.className = "layers-icon";
    icon.title = "Select map style";

    // Thumbnail grid container (hidden initially)
    const panel = document.createElement("div");
    panel.className = "basemap-panel";

    this.layers.forEach((layer) => {
      const card = document.createElement("div");
      card.className = "basemap-card";
      if (layer.id === defaultStyle) card.classList.add("selected");

      // Thumbnail image
      const thumb = document.createElement("div");
      thumb.className = "basemap-thumb";
      // Try to load a thumbnail; fall back to a colored placeholder
      const img = document.createElement("img");
      img.src = "/icons/basemaps/" + layer.id + ".png";
      img.alt = layer.name;
      img.draggable = false;
      img.onerror = function () {
        // No thumbnail available — show a placeholder with initials
        this.style.display = "none";
        var placeholder = document.createElement("div");
        placeholder.className = "basemap-thumb-placeholder";
        placeholder.textContent = layer.name
          .split(" ")
          .map((w) => w[0])
          .join("")
          .substring(0, 3);
        thumb.appendChild(placeholder);
      };
      thumb.appendChild(img);

      // Label
      const label = document.createElement("div");
      label.className = "basemap-label";
      label.textContent = layer.name;

      card.appendChild(thumb);
      card.appendChild(label);

      card.addEventListener("click", () => {
        // Deselect all
        panel
          .querySelectorAll(".basemap-card")
          .forEach((c) => c.classList.remove("selected"));
        card.classList.add("selected");
        this._selectedId = layer.id;
        panel.style.display = "none";
        setMapStyle(layer.id);
      });

      panel.appendChild(card);
    });

    this._container.appendChild(icon);
    this._container.appendChild(panel);

    // Toggle panel on icon click
    icon.addEventListener("click", () => {
      panel.style.display =
        panel.style.display === "grid" ? "none" : "grid";
    });

    // Close panel when clicking outside
    document.addEventListener("click", (e) => {
      if (!this._container.contains(e.target)) {
        panel.style.display = "none";
      }
    });
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

/**
 * Switch the map to a different basemap style while preserving all
 * application layers that sit above the dummy_layer_0 sentinel.
 *
 * @param {string} styleID - Key into the global `mapStyles` dictionary.
 */
export function setMapStyle(styleID) {
  console.log("Setting style to: " + styleID);

  const currentStyle = map.getStyle();
  const newStyle = Object.assign({}, mapStyles[styleID]);

  // Ensure any sources from the current style are copied across
  newStyle.sources = Object.assign({}, currentStyle.sources, newStyle.sources);

  // Find the index of where to insert our layers
  let labelIndex = currentStyle.layers.findIndex((el) => {
    return el.id == "dummy_layer_0";
  });

  if (labelIndex === -1) {
    labelIndex = newStyle.layers.length;
  }

  const appLayers = currentStyle.layers.slice(labelIndex);

  newStyle.layers = [...newStyle.layers, ...appLayers];

  map.setStyle(newStyle);
}
