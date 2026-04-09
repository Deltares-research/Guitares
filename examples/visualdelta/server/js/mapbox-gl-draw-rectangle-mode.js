/**
 * mapbox-gl-draw-rectangle-mode.js
 *
 * A custom MapboxDraw mode that allows users to draw axis-aligned
 * rectangles by clicking two corners (start and end points). The
 * rectangle is built as a bounding box from those two points.
 */

"use strict";

/**
 * Helper to manage double-click zoom during drawing.
 * Disables it while drawing so double-click does not zoom in,
 * and re-enables it when drawing stops (if it was originally on).
 */
var doubleClickZoom = {
  /**
   * Re-enable double-click zoom if it was enabled in the initial config.
   * @param {Object} ctx - MapboxDraw internal context.
   */
  enable: function enable(ctx) {
    setTimeout(function () {
      if (!ctx.map || !ctx.map.doubleClickZoom || !ctx._ctx || !ctx._ctx.store || !ctx._ctx.store.getInitialConfigValue) return;
      if (!ctx._ctx.store.getInitialConfigValue("doubleClickZoom")) return;
      ctx.map.doubleClickZoom.enable();
    }, 0);
  },
  /**
   * Disable double-click zoom unconditionally.
   * @param {Object} ctx - MapboxDraw internal context.
   */
  disable: function disable(ctx) {
    setTimeout(function () {
      if (!ctx.map || !ctx.map.doubleClickZoom) return;
      ctx.map.doubleClickZoom.disable();
    }, 0);
  }
};

/**
 * MapboxDraw mode for drawing rectangles.
 * First click sets one corner; mouse movement updates the opposite
 * corner; second click finalises the rectangle.
 */
export var DrawRectangle = {
  /**
   * Initialise the drawing state: create an empty polygon feature
   * and prepare the UI for drawing.
   * @param {Object} opts - Mode options (unused).
   * @returns {Object} Initial state containing the rectangle feature.
   */
  onSetup: function onSetup(opts) {
    var rectangle = this.newFeature({
      type: "Feature",
      properties: {},
      geometry: {
        type: "Polygon",
        coordinates: [[]]
      }
    });
    this.addFeature(rectangle);
    this.clearSelectedFeatures();
    doubleClickZoom.disable(this);
    this.updateUIClasses({ mouse: "add" });
    this.setActionableState({
      trash: true
    });
    return {
      rectangle: rectangle
    };
  },

  /**
   * Support mobile taps by emulating mouse move then click.
   * @param {Object} state - Current drawing state.
   * @param {Object} e - Touch/tap event.
   */
  onTap: function onTap(state, e) {
    if (state.startPoint) this.onMouseMove(state, e);
    this.onClick(state, e);
  },

  /**
   * Handle map clicks. First click records the start corner;
   * second click (at a different position) finalises the rectangle.
   * @param {Object} state - Current drawing state.
   * @param {Object} e - Click event with lngLat.
   */
  onClick: function onClick(state, e) {
    if (state.startPoint && state.startPoint[0] !== e.lngLat.lng && state.startPoint[1] !== e.lngLat.lat) {
      this.updateUIClasses({ mouse: "pointer" });
      state.endPoint = [e.lngLat.lng, e.lngLat.lat];
      this.changeMode("simple_select", { featuresId: state.rectangle.id });
    }
    var startPoint = [e.lngLat.lng, e.lngLat.lat];
    state.startPoint = startPoint;
  },

  /**
   * Update the rectangle coordinates as the mouse moves.
   * Uses the start point and current cursor to compute a bounding box.
   * @param {Object} state - Current drawing state.
   * @param {Object} e - Mouse move event with lngLat.
   */
  onMouseMove: function onMouseMove(state, e) {
    if (state.startPoint) {
      state.rectangle.updateCoordinate("0.0", state.startPoint[0], state.startPoint[1]); // minX, minY - starting point
      state.rectangle.updateCoordinate("0.1", e.lngLat.lng, state.startPoint[1]);         // maxX, minY
      state.rectangle.updateCoordinate("0.2", e.lngLat.lng, e.lngLat.lat);                // maxX, maxY
      state.rectangle.updateCoordinate("0.3", state.startPoint[0], e.lngLat.lat);         // minX, maxY
      state.rectangle.updateCoordinate("0.4", state.startPoint[0], state.startPoint[1]); // closing vertex
    }
  },

  /**
   * Handle key presses. Escape cancels drawing and returns to simple_select.
   * @param {Object} state - Current drawing state.
   * @param {Object} e - Key event.
   */
  onKeyUp: function onKeyUp(state, e) {
    if (e.keyCode === 27) return this.changeMode("simple_select");
  },

  /**
   * Called when the mode is stopped. Validates the rectangle and either
   * fires a draw.create event or silently deletes the invalid feature.
   * @param {Object} state - Current drawing state.
   */
  onStop: function onStop(state) {
    doubleClickZoom.enable(this);
    this.updateUIClasses({ mouse: "none" });
    this.activateUIButton();

    if (this.getFeature(state.rectangle.id) === undefined) return;

    // Remove the closing coordinate before validation
    state.rectangle.removeCoordinate("0.4");
    if (state.rectangle.isValid()) {
      this.map.fire("draw.create", {
        features: [state.rectangle.toGeoJSON()]
      });
    } else {
      this.deleteFeature([state.rectangle.id], { silent: true });
      this.changeMode("simple_select", {}, { silent: true });
    }
  },

  /**
   * Render the rectangle feature during drawing.
   * Only displays the polygon once the start point has been set.
   * @param {Object} state - Current drawing state.
   * @param {Object} geojson - The GeoJSON feature to display.
   * @param {Function} display - Callback to push the feature for rendering.
   */
  toDisplayFeatures: function toDisplayFeatures(state, geojson, display) {
    var isActivePolygon = geojson.properties.id === state.rectangle.id;
    geojson.properties.active = isActivePolygon ? "true" : "false";
    if (!isActivePolygon) return display(geojson);

    if (!state.startPoint) return;
    return display(geojson);
  },

  /**
   * Handle the trash action: delete the rectangle and exit drawing mode.
   * @param {Object} state - Current drawing state.
   */
  onTrash: function onTrash(state) {
    this.deleteFeature([state.rectangle.id], { silent: true });
    this.changeMode("simple_select");
  }
};
