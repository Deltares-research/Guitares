/**
 * mapbox_gl_draw_scale_rotate_mode.js
 *
 * A custom MapboxDraw mode that allows scaling and rotating polygon
 * features. Rotation uses a rotation handle placed at a configurable
 * offset from the feature centre; scaling uses the corner vertices.
 * Individual vertex dragging is also supported for rectangles.
 *
 * Based on mapbox-gl-draw-scale-rotate-mode, adapted for MapLibre 5.x
 * with async image loading and custom vertex-drag logic for rectangles.
 */

// ══════════════════════════════════════════════════════════════════════
//  Imports and dependencies
// ══════════════════════════════════════════════════════════════════════

const Constants = MapboxDraw.constants;
const CommonSelectors = MapboxDraw.lib.CommonSelectors;
const doubleClickZoom = MapboxDraw.lib.doubleClickZoom;
const createSupplementaryPoints = MapboxDraw.lib.createSupplementaryPoints;
const moveFeatures = MapboxDraw.lib.moveFeatures;

let lineString = turf.lineString;
let point = turf.point;
let bearing = turf.bearing;
let center = turf.center;
let midpoint = turf.midpoint;
let distance = turf.distance;
let destination = turf.destination;
let transformRotate = turf.transformRotate;
let transformScale = turf.transformScale;

var rotate = '/js/img/rotate.png';
var scale = '/js/img/scale.png';

// ══════════════════════════════════════════════════════════════════════
//  Exports: mode object and enumerations
// ══════════════════════════════════════════════════════════════════════

/** The scale/rotate mode object. Methods are attached below. */
export const SRMode = {};

/**
 * Enum for pivot/centre options used by rotation and scaling.
 * @enum {number}
 */
export const SRCenter = {
  /** Rotate or scale around the centre of the polygon. */
  Center: 0,
  /** Rotate or scale around the opposite side of the polygon. */
  Opposite: 1,
};

// ══════════════════════════════════════════════════════════════════════
//  Style definitions for scale/rotate mode
// ══════════════════════════════════════════════════════════════════════

/**
 * MapboxDraw style array used when scale/rotate mode is active.
 * Includes polygon, line, point, vertex, and rotation widget styles.
 */
export const SRStyle = [

  // ── Polygon fill styles ─────────────────────────────────────────

  {
    id: 'gl-draw-polygon-fill-inactive',
    type: 'fill',
    filter: [
      'all',
      ['==', 'active', 'false'],
      ['==', '$type', 'Polygon'],
      ['!=', 'user_type', 'overlay'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'fill-color': '#3bb2d0',
      'fill-outline-color': '#3bb2d0',
      'fill-opacity': 0.2,
    },
  },
  {
    id: 'gl-draw-polygon-fill-active',
    type: 'fill',
    filter: [
      'all',
      ['==', 'active', 'true'],
      ['==', '$type', 'Polygon'],
      ['!=', 'user_type', 'overlay'],
    ],
    paint: {
      'fill-color': '#fbb03b',
      'fill-outline-color': '#fbb03b',
      'fill-opacity': 0.2,
    },
  },
  {
    id: 'gl-draw-overlay-polygon-fill-inactive',
    type: 'fill',
    filter: [
      'all',
      ['==', 'active', 'false'],
      ['==', '$type', 'Polygon'],
      ['==', 'user_type', 'overlay'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'fill-color': '#3bb2d0',
      'fill-outline-color': '#3bb2d0',
      'fill-opacity': 0.01,
    },
  },
  {
    id: 'gl-draw-overlay-polygon-fill-active',
    type: 'fill',
    filter: [
      'all',
      ['==', 'active', 'true'],
      ['==', '$type', 'Polygon'],
      ['==', 'user_type', 'overlay'],
    ],
    paint: {
      'fill-color': '#fbb03b',
      'fill-outline-color': '#fbb03b',
      'fill-opacity': 0.01,
    },
  },

  // ── Polygon stroke styles ───────────────────────────────────────

  {
    id: 'gl-draw-polygon-stroke-inactive',
    type: 'line',
    filter: [
      'all',
      ['==', 'active', 'false'],
      ['==', '$type', 'Polygon'],
      ['!=', 'user_type', 'overlay'],
      ['!=', 'mode', 'static'],
    ],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#3bb2d0',
      'line-width': 2,
    },
  },
  {
    id: 'gl-draw-polygon-stroke-active',
    type: 'line',
    filter: ['all', ['==', 'active', 'true'], ['==', '$type', 'Polygon']],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#fbb03b',
      'line-dasharray': [0.2, 2],
      'line-width': 2,
    },
  },

  // ── Midpoint styles ─────────────────────────────────────────────

  {
    id: 'gl-draw-polygon-midpoint',
    type: 'circle',
    filter: ['all', ['==', '$type', 'Point'], ['==', 'meta', 'midpoint']],
    paint: {
      'circle-radius': 3,
      'circle-color': '#fbb03b',
    },
  },

  // ── Line styles ─────────────────────────────────────────────────

  {
    id: 'gl-draw-line-inactive',
    type: 'line',
    filter: [
      'all',
      ['==', 'active', 'false'],
      ['==', '$type', 'LineString'],
      ['!=', 'mode', 'static'],
    ],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#3bb2d0',
      'line-width': 2,
    },
  },
  {
    id: 'gl-draw-line-active',
    type: 'line',
    filter: ['all', ['==', '$type', 'LineString'], ['==', 'active', 'true']],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#fbb03b',
      'line-dasharray': [0.2, 2],
      'line-width': 2,
    },
  },

  // ── Vertex styles ───────────────────────────────────────────────

  {
    id: 'gl-draw-polygon-and-line-vertex-stroke-inactive',
    type: 'circle',
    filter: [
      'all',
      ['==', 'meta', 'vertex'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'circle-radius': 4,
      'circle-color': '#fff',
    },
  },
  {
    id: 'gl-draw-polygon-and-line-vertex-inactive',
    type: 'circle',
    filter: [
      'all',
      ['==', 'meta', 'vertex'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'circle-radius': 2,
      'circle-color': '#fbb03b',
    },
  },

  // ── Scale icon on vertices ──────────────────────────────────────

  {
    id: 'gl-draw-polygon-and-line-vertex-scale-icon',
    type: 'symbol',
    filter: [
      'all',
      ['==', 'meta', 'vertex'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static'],
      ['has', 'heading'],
    ],
    layout: {
      'icon-image': 'scale',
      'icon-allow-overlap': true,
      'icon-ignore-placement': true,
      'icon-rotation-alignment': 'map',
      'icon-rotate': ['get', 'heading'],
    },
    paint: {
      'icon-opacity': 1.0,
      'icon-opacity-transition': {
        delay: 0,
        duration: 0,
      },
    },
  },

  // ── Point feature styles ────────────────────────────────────────

  {
    id: 'gl-draw-point-point-stroke-inactive',
    type: 'circle',
    filter: [
      'all',
      ['==', 'active', 'false'],
      ['==', '$type', 'Point'],
      ['==', 'meta', 'feature'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'circle-radius': 5,
      'circle-opacity': 1,
      'circle-color': '#fff',
    },
  },
  {
    id: 'gl-draw-point-inactive',
    type: 'circle',
    filter: [
      'all',
      ['==', 'active', 'false'],
      ['==', '$type', 'Point'],
      ['==', 'meta', 'feature'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'circle-radius': 23,
      'circle-color': '#3bb2d0',
    },
  },
  {
    id: 'gl-draw-point-stroke-active',
    type: 'circle',
    filter: [
      'all',
      ['==', '$type', 'Point'],
      ['==', 'active', 'true'],
      ['!=', 'meta', 'midpoint'],
    ],
    paint: {
      'circle-radius': 4,
      'circle-color': '#fff',
    },
  },
  {
    id: 'gl-draw-point-active',
    type: 'circle',
    filter: [
      'all',
      ['==', '$type', 'Point'],
      ['!=', 'meta', 'midpoint'],
      ['==', 'active', 'true'],
    ],
    paint: {
      'circle-radius': 5,
      'circle-color': '#fbb03b',
      'circle-opacity': 1,
    },
  },

  // ── Static styles (read-only) ──────────────────────────────────

  {
    id: 'gl-draw-polygon-fill-static',
    type: 'fill',
    filter: ['all', ['==', 'mode', 'static'], ['==', '$type', 'Polygon']],
    paint: {
      'fill-color': '#404040',
      'fill-outline-color': '#404040',
      'fill-opacity': 0.1,
    },
  },
  {
    id: 'gl-draw-polygon-stroke-static',
    type: 'line',
    filter: ['all', ['==', 'mode', 'static'], ['==', '$type', 'Polygon']],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#404040',
      'line-width': 2,
    },
  },
  {
    id: 'gl-draw-line-static',
    type: 'line',
    filter: ['all', ['==', 'mode', 'static'], ['==', '$type', 'LineString']],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#404040',
      'line-width': 2,
    },
  },
  {
    id: 'gl-draw-point-static',
    type: 'circle',
    filter: ['all', ['==', 'mode', 'static'], ['==', '$type', 'Point']],
    paint: {
      'circle-radius': 5,
      'circle-color': '#404040',
    },
  },

  // ── Rotation widget styles ──────────────────────────────────────

  /** Dashed line connecting rotation handle to feature edge. */
  {
    id: 'gl-draw-line-rotate-point',
    type: 'line',
    filter: [
      'all',
      ['==', 'meta', 'midpoint'],
      ['==', 'icon', 'rotate'],
      ['==', '$type', 'LineString'],
      ['!=', 'mode', 'static'],
    ],
    layout: {
      'line-cap': 'round',
      'line-join': 'round',
    },
    paint: {
      'line-color': '#fbb03b',
      'line-dasharray': [0.2, 2],
      'line-width': 2,
    },
  },

  /** White outline for rotation handle circle. */
  {
    id: 'gl-draw-polygon-rotate-point-stroke',
    type: 'circle',
    filter: [
      'all',
      ['==', 'meta', 'midpoint'],
      ['==', 'icon', 'rotate'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'circle-radius': 4,
      'circle-color': '#fff',
    },
  },

  /** Inner fill for rotation handle circle. */
  {
    id: 'gl-draw-polygon-rotate-point',
    type: 'circle',
    filter: [
      'all',
      ['==', 'meta', 'midpoint'],
      ['==', 'icon', 'rotate'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static'],
    ],
    paint: {
      'circle-radius': 2,
      'circle-color': '#fbb03b',
    },
  },

  /** Rotation icon symbol on the rotation handle. */
  {
    id: 'gl-draw-polygon-rotate-point-icon',
    type: 'symbol',
    filter: [
      'all',
      ['==', 'meta', 'midpoint'],
      ['==', 'icon', 'rotate'],
      ['==', '$type', 'Point'],
      ['!=', 'mode', 'static'],
    ],
    layout: {
      'icon-image': 'rotate',
      'icon-allow-overlap': true,
      'icon-ignore-placement': true,
      'icon-rotation-alignment': 'map',
      'icon-rotate': ['get', 'heading'],
    },
    paint: {
      'icon-opacity': 1.0,
      'icon-opacity-transition': {
        delay: 0,
        duration: 0,
      },
    },
  },
];

// ══════════════════════════════════════════════════════════════════════
//  Helper functions
// ══════════════════════════════════════════════════════════════════════

/**
 * Parse a pivot/centre option into an SRCenter enum value.
 * Accepts numeric enum values or the strings "center" / "opposite".
 * @param {number|string|undefined} value - The value to parse.
 * @param {number} [defaultSRCenter=SRCenter.Center] - Fallback value.
 * @returns {number} An SRCenter enum value.
 * @throws {Error} If the value is not a valid SRCenter.
 */
function parseSRCenter(value, defaultSRCenter = SRCenter.Center) {
  if (value == undefined || value == null) return defaultSRCenter;
  if (value === SRCenter.Center || value === SRCenter.Opposite) return value;
  if (value == 'center') return SRCenter.Center;
  if (value == 'opposite') return SRCenter.Opposite;
  throw Error('Invalid SRCenter: ' + value);
}

// ══════════════════════════════════════════════════════════════════════
//  SRMode lifecycle methods
// ══════════════════════════════════════════════════════════════════════

/**
 * Initialise scale/rotate mode for the currently selected feature.
 * Loads rotation and scale icon images (async for MapLibre 5.x),
 * configures state from options, and disables double-click zoom.
 *
 * @param {Object} opts - Mode options.
 * @param {string} opts.featureId - ID of the feature to transform.
 * @param {boolean} [opts.canScale=true] - Whether scaling is enabled.
 * @param {boolean} [opts.canRotate=true] - Whether rotation is enabled.
 * @param {boolean} [opts.canTrash=true] - Whether deletion is enabled.
 * @param {boolean} [opts.singleRotationPoint=false] - Show only one rotation handle.
 * @param {number} [opts.rotationPointRadius=1.0] - Offset multiplier for the rotation handle.
 * @param {number|string} [opts.rotatePivot='center'] - Rotation pivot: 'center' or 'opposite'.
 * @param {number|string} [opts.scaleCenter='center'] - Scale centre: 'center' or 'opposite'.
 * @param {boolean} [opts.canSelectFeatures=true] - Whether clicking away exits the mode.
 * @returns {Object} The initial mode state.
 */
SRMode.onSetup = function (opts) {
  const featureId = this.getSelected()[0].id;
  const feature = this.getFeature(featureId);

  if (!feature) {
    throw new Error('You must provide a valid featureId to enter SRMode');
  }

  if (
    feature.type === Constants.geojsonTypes.POINT ||
    feature.type === Constants.geojsonTypes.MULTI_POINT
  ) {
    throw new TypeError('SRMode can not handle points');
  }

  const state = {
    featureId,
    feature,

    canTrash: opts.canTrash != undefined ? opts.canTrash : true,

    canScale: opts.canScale != undefined ? opts.canScale : true,
    canRotate: opts.canRotate != undefined ? opts.canRotate : true,

    singleRotationPoint:
      opts.singleRotationPoint != undefined ? opts.singleRotationPoint : false,
    rotationPointRadius:
      opts.rotationPointRadius != undefined ? opts.rotationPointRadius : 1.0,

    rotatePivot: parseSRCenter(opts.rotatePivot, SRCenter.Center),
    scaleCenter: parseSRCenter(opts.scaleCenter, SRCenter.Center),

    canSelectFeatures:
      opts.canSelectFeatures != undefined ? opts.canSelectFeatures : true,

    dragMoveLocation: opts.startPos || null,
    dragMoving: false,
    canDragMove: false,
    selectedCoordPaths: opts.coordPath ? [opts.coordPath] : [],
  };

  if (!(state.canRotate || state.canScale)) {
    console.warn('Non of canScale or canRotate is true');
  }

  this.setSelectedCoordinates(
    this.pathsToCoordinates(featureId, state.selectedCoordPaths)
  );
  this.setSelected(featureId);
  doubleClickZoom.disable(this);

  this.setActionableState({
    combineFeatures: false,
    uncombineFeatures: false,
    trash: state.canTrash,
  });

  // MapLibre 5.x uses promise-based loadImage instead of callback
  var _this = this;
  (async function () {
    try {
      if (!_this.map.hasImage('rotate')) {
        var rotateImg = await _this.map.loadImage('/js/img/rotate.png');
        _this.map.addImage('rotate', rotateImg.data);
      }
      if (!_this.map.hasImage('scale')) {
        var scaleImg = await _this.map.loadImage('/js/img/scale.png');
        _this.map.addImage('scale', scaleImg.data);
      }
    } catch (e) {
      console.warn('Could not load rotate/scale icons:', e);
    }
  })();

  return state;
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode display and rendering
// ══════════════════════════════════════════════════════════════════════

/**
 * Render the feature and its supplementary points (scale handles,
 * rotation handles) for the current frame.
 * @param {Object} state - Current mode state.
 * @param {Object} geojson - GeoJSON feature being rendered.
 * @param {Function} push - Callback to push features for display.
 */
SRMode.toDisplayFeatures = function (state, geojson, push) {
  if (state.featureId === geojson.properties.id) {
    geojson.properties.active = Constants.activeStates.ACTIVE;
    push(geojson);

    var suppPoints = createSupplementaryPoints(geojson, {
      map: this.map,
      midpoints: false,
      selectedPaths: state.selectedCoordPaths,
    });

    if (state.canScale) {
      this.computeBisectrix(suppPoints);
      suppPoints.forEach(push);
    }

    if (state.canRotate) {
      var rotPoints = this.createRotationPoints(state, geojson, suppPoints);
      rotPoints.forEach(push);
    }
  } else {
    geojson.properties.active = Constants.activeStates.INACTIVE;
    push(geojson);
  }

  this.setActionableState({
    combineFeatures: false,
    uncombineFeatures: false,
    trash: state.canTrash,
  });
};

/**
 * Clean up when exiting scale/rotate mode.
 * Re-enables double-click zoom and clears coordinate selections.
 */
SRMode.onStop = function () {
  doubleClickZoom.enable(this);
  this.clearSelectedCoordinates();
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode geometry helpers
// ══════════════════════════════════════════════════════════════════════

/**
 * Convert coordinate path strings to the format expected by
 * setSelectedCoordinates.
 * @param {string} featureId - The feature these paths belong to.
 * @param {string[]} paths - Array of coordinate path strings (e.g. "0.1").
 * @returns {Array<{feature_id: string, coord_path: string}>}
 */
SRMode.pathsToCoordinates = function (featureId, paths) {
  return paths.map((coord_path) => {
    return { feature_id: featureId, coord_path };
  });
};

/**
 * Compute the bisectrix heading for each vertex point, used to orient
 * the scale icon at each corner of the polygon.
 * @param {Object[]} points - Array of supplementary point GeoJSON features.
 */
SRMode.computeBisectrix = function (points) {
  for (var i1 = 0; i1 < points.length; i1++) {
    var i0 = (i1 - 1 + points.length) % points.length;
    var i2 = (i1 + 1) % points.length;

    var l1 = lineString([
      points[i0].geometry.coordinates,
      points[i1].geometry.coordinates,
    ]);
    var l2 = lineString([
      points[i1].geometry.coordinates,
      points[i2].geometry.coordinates,
    ]);
    var a1 = bearing(
      points[i0].geometry.coordinates,
      points[i1].geometry.coordinates
    );
    var a2 = bearing(
      points[i2].geometry.coordinates,
      points[i1].geometry.coordinates
    );

    var a = (a1 + a2) / 2.0;

    if (a < 0.0) a += 360;
    if (a > 360) a -= 360;

    points[i1].properties.heading = a;
  }
};

/**
 * Create a single rotation handle widget positioned between two vertices.
 * @param {Object[]} rotationWidgets - Array to push the widget feature into.
 * @param {string} featureId - ID of the parent feature.
 * @param {Object} v1 - First vertex GeoJSON point.
 * @param {Object} v2 - Second vertex GeoJSON point.
 * @param {Object} rotCenter - Centre point for rotation reference.
 * @param {number} radiusScale - Multiplier to offset the handle from the edge midpoint.
 */
SRMode._createRotationPoint = function (
  rotationWidgets,
  featureId,
  v1,
  v2,
  rotCenter,
  radiusScale
) {
  var cR0 = midpoint(v1, v2).geometry.coordinates;
  var heading = bearing(rotCenter, cR0);
  var distance0 = distance(rotCenter, cR0);
  var distance1 = radiusScale * distance0;
  var cR1 = destination(rotCenter, distance1, heading, {}).geometry.coordinates;
  rotationWidgets.push({
    type: Constants.geojsonTypes.FEATURE,
    properties: {
      meta: Constants.meta.MIDPOINT,
      icon: 'rotate',
      parent: featureId,
      lng: cR1[0],
      lat: cR1[1],
      coord_path: v1.properties.coord_path,
      heading: heading,
    },
    geometry: {
      type: Constants.geojsonTypes.POINT,
      coordinates: cR1,
    },
  });
};

/**
 * Create rotation handle widgets for the feature. If singleRotationPoint
 * is true, only one handle is created (between the first two vertices);
 * otherwise one handle per edge.
 * @param {Object} state - Current mode state.
 * @param {Object} geojson - The feature's GeoJSON.
 * @param {Object[]} suppPoints - Supplementary vertex points.
 * @returns {Object[]} Array of rotation widget GeoJSON features.
 */
SRMode.createRotationPoints = function (state, geojson, suppPoints) {
  const { type, coordinates } = geojson.geometry;
  const featureId = geojson.properties && geojson.properties.id;

  let rotationWidgets = [];
  if (
    type === Constants.geojsonTypes.POINT ||
    type === Constants.geojsonTypes.MULTI_POINT
  ) {
    return;
  }

  var corners = suppPoints.slice(0);
  corners[corners.length] = corners[0];

  var v1 = null;
  var rotCenter = this.computeRotationCenter(state, geojson);

  if (state.singleRotationPoint) {
    this._createRotationPoint(
      rotationWidgets,
      featureId,
      corners[0],
      corners[1],
      rotCenter,
      state.rotationPointRadius
    );
  } else {
    corners.forEach((v2) => {
      if (v1 != null) {
        this._createRotationPoint(
          rotationWidgets,
          featureId,
          v1,
          v2,
          rotCenter,
          state.rotationPointRadius
        );
      }
      v1 = v2;
    });
  }
  return rotationWidgets;
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode drag state management
// ══════════════════════════════════════════════════════════════════════

/**
 * Begin a drag operation: disable map panning and record the start position.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch event.
 */
SRMode.startDragging = function (state, e) {
  this.map.dragPan.disable();
  state.canDragMove = true;
  state.dragMoveLocation = e.lngLat;
};

/**
 * End a drag operation: re-enable map panning and clear drag state.
 * @param {Object} state - Current mode state.
 */
SRMode.stopDragging = function (state) {
  this.map.dragPan.enable();
  state.dragMoving = false;
  state.canDragMove = false;
  state.dragMoveLocation = null;
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode input event handlers
// ══════════════════════════════════════════════════════════════════════

/** Selector: true when the event target is a rotation midpoint. */
const isRotatePoint = CommonSelectors.isOfMetaType(Constants.meta.MIDPOINT);

/** Selector: true when the event target is a vertex point. */
const isVertex = CommonSelectors.isOfMetaType(Constants.meta.VERTEX);

/**
 * Handle mouse-down / touch-start: dispatch to vertex, rotation, or
 * feature drag handler depending on what was clicked.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch event.
 */
SRMode.onTouchStart = SRMode.onMouseDown = function (state, e) {
  if (isVertex(e)) return this.onVertex(state, e);
  if (isRotatePoint(e)) return this.onRotatePoint(state, e);
  if (CommonSelectors.isActiveFeature(e)) return this.onFeature(state, e);
};

/**
 * Enum for the type of transformation being performed during a drag.
 * @enum {number}
 */
const TxMode = {
  Scale: 1,
  Rotate: 2,
  Vertex: 3,
};

/**
 * Handle clicking on a vertex: prepare for individual vertex dragging.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch event on a vertex.
 */
SRMode.onVertex = function (state, e) {
  this.computeAxes(state, state.feature.toGeoJSON());
  this.startDragging(state, e);
  const about = e.featureTarget.properties;
  state.selectedCoordPaths = [about.coord_path];
  state.txMode = TxMode.Vertex;
};

/**
 * Handle clicking on a rotation point: prepare for rotation dragging.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch event on a rotation handle.
 */
SRMode.onRotatePoint = function (state, e) {
  this.computeAxes(state, state.feature.toGeoJSON());
  this.startDragging(state, e);
  const about = e.featureTarget.properties;
  state.selectedCoordPaths = [about.coord_path];
  state.txMode = TxMode.Rotate;
};

/**
 * Handle clicking on the feature body: prepare for translation dragging.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch event on the feature.
 */
SRMode.onFeature = function (state, e) {
  state.selectedCoordPaths = [];
  this.startDragging(state, e);
};

/**
 * Extract the coordinate index from the first selected coordinate path.
 * @param {string[]} coordPaths - Array of coordinate path strings.
 * @returns {number} The parsed coordinate index.
 */
SRMode.coordinateIndex = function (coordPaths) {
  if (coordPaths.length >= 1) {
    var parts = coordPaths[0].split('.');
    return parseInt(parts[parts.length - 1]);
  } else {
    return 0;
  }
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode transformation computations
// ══════════════════════════════════════════════════════════════════════

/**
 * Compute the rotation centre for the polygon.
 * Currently returns the geometric centre (centroid).
 * @param {Object} state - Current mode state.
 * @param {Object} polygon - GeoJSON polygon feature.
 * @returns {Object} Turf point at the rotation centre.
 */
SRMode.computeRotationCenter = function (state, polygon) {
  var center0 = center(polygon);
  return center0;
};

/**
 * Pre-compute rotation and scaling axes/distances for the polygon.
 * Stores initial headings, centres, and distances in state.rotation
 * and state.scaling so that drag operations can compute deltas
 * without re-reading the original geometry each frame.
 * @param {Object} state - Current mode state.
 * @param {Object} polygon - GeoJSON polygon feature (initial state).
 */
SRMode.computeAxes = function (state, polygon) {
  const center0 = this.computeRotationCenter(state, polygon);
  let corners;
  if (polygon.geometry.type === Constants.geojsonTypes.POLYGON)
    corners = polygon.geometry.coordinates[0].slice(0);
  else if (polygon.geometry.type === Constants.geojsonTypes.MULTI_POLYGON) {
    let temp = [];
    polygon.geometry.coordinates.forEach((c) => {
      c.forEach((c2) => {
        c2.forEach((c3) => {
          temp.push(c3);
        });
      });
    });
    corners = temp;
  } else if (polygon.geometry.type === Constants.geojsonTypes.LINE_STRING)
    corners = polygon.geometry.coordinates;
  else if (polygon.geometry.type === Constants.geojsonTypes.MULTI_LINE_STRING) {
    let temp = [];
    polygon.geometry.coordinates.forEach((c) => {
      c.forEach((c2) => {
        temp.push(c2);
      });
    });
    corners = temp;
  }

  const n = corners.length - 1;
  const iHalf = Math.floor(n / 2);

  // Compute rotation centres and initial headings per vertex
  var rotateCenters = [];
  var headings = [];

  for (var i1 = 0; i1 < n; i1++) {
    var i0 = i1 - 1;
    if (i0 < 0) i0 += n;

    const c0 = corners[i0];
    const c1 = corners[i1];
    const rotPoint = midpoint(point(c0), point(c1));

    var rotCenter = center0;
    if (SRCenter.Opposite === state.rotatePivot) {
      var i3 = (i1 + iHalf) % n;
      var i2 = i3 - 1;
      if (i2 < 0) i2 += n;

      const c2 = corners[i2];
      const c3 = corners[i3];
      rotCenter = midpoint(point(c2), point(c3));
    }

    rotateCenters[i1] = rotCenter.geometry.coordinates;
    headings[i1] = bearing(rotCenter, rotPoint);
  }

  state.rotation = {
    feature0: polygon,
    centers: rotateCenters,
    headings: headings,
  };

  // Compute scale centres and initial distances per vertex
  var scaleCenters = [];
  var distances = [];
  for (var i = 0; i < n; i++) {
    var c1 = corners[i];
    var c0 = center0.geometry.coordinates;
    if (SRCenter.Opposite === state.scaleCenter) {
      var i2 = (i + iHalf) % n;
      c0 = corners[i2];
    }
    scaleCenters[i] = c0;
    distances[i] = distance(point(c0), point(c1), { units: 'meters' });
  }

  state.scaling = {
    feature0: polygon,
    centers: scaleCenters,
    distances: distances,
  };
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode drag handlers
// ══════════════════════════════════════════════════════════════════════

/**
 * Main drag handler: dispatches to rotate, scale, vertex-drag, or
 * feature-translate depending on the current transformation mode.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch drag event.
 */
SRMode.onDrag = function (state, e) {
  if (state.canDragMove !== true) return;
  state.dragMoving = true;
  e.originalEvent.stopPropagation();

  const delta = {
    lng: e.lngLat.lng - state.dragMoveLocation.lng,
    lat: e.lngLat.lat - state.dragMoveLocation.lat,
  };
  if (state.selectedCoordPaths.length > 0 && state.txMode) {
    switch (state.txMode) {
      case TxMode.Rotate:
        this.dragRotatePoint(state, e, delta);
        break;
      case TxMode.Scale:
        this.dragScalePoint(state, e, delta);
        break;
      case TxMode.Vertex:
        this.dragVertexPoint(state, e, delta);
        break;
    }
  } else {
    this.dragFeature(state, e, delta);
  }

  state.dragMoveLocation = e.lngLat;
};

/**
 * Rotate the feature by computing the bearing delta between the initial
 * heading and the current cursor position relative to the rotation centre.
 * Shift-key snaps to 5-degree increments.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch drag event.
 * @param {Object} delta - Lng/lat delta from last position.
 */
SRMode.dragRotatePoint = function (state, e, delta) {
  if (state.rotation === undefined || state.rotation == null) {
    throw new Error('state.rotation required');
  }

  var polygon = state.feature.toGeoJSON();
  var m1 = point([e.lngLat.lng, e.lngLat.lat]);

  const n = state.rotation.centers.length;
  var cIdx = (this.coordinateIndex(state.selectedCoordPaths) + 1) % n;
  var cCenter = state.rotation.centers[cIdx];
  var center = point(cCenter);

  var heading1 = bearing(center, m1);
  var heading0 = state.rotation.headings[cIdx];
  var rotateAngle = heading1 - heading0;
  if (CommonSelectors.isShiftDown(e)) {
    rotateAngle = 5.0 * Math.round(rotateAngle / 5.0);
  }

  var rotatedFeature = transformRotate(state.rotation.feature0, rotateAngle, {
    pivot: center,
    mutate: false,
  });

  state.feature.incomingCoords(rotatedFeature.geometry.coordinates);
};

/**
 * Scale the feature by computing the distance ratio between the initial
 * vertex distance and the current cursor distance from the scale centre.
 * Shift-key snaps to 5% increments.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch drag event.
 * @param {Object} delta - Lng/lat delta from last position.
 */
SRMode.dragScalePoint = function (state, e, delta) {
  if (state.scaling === undefined || state.scaling == null) {
    throw new Error('state.scaling required');
  }

  var polygon = state.feature.toGeoJSON();

  var cIdx = this.coordinateIndex(state.selectedCoordPaths);
  var cCenter = state.scaling.centers[cIdx];
  var center = point(cCenter);
  var m1 = point([e.lngLat.lng, e.lngLat.lat]);

  var dist = distance(center, m1, { units: 'meters' });
  var scale = dist / state.scaling.distances[cIdx];

  if (CommonSelectors.isShiftDown(e)) {
    scale = 0.05 * Math.round(scale / 0.05);
  }

  var scaledFeature = transformScale(state.scaling.feature0, scale, {
    origin: cCenter,
    mutate: false,
  });

  state.feature.incomingCoords(scaledFeature.geometry.coordinates);
};

/**
 * Move a rectangle vertex while keeping the shape rectangular.
 * Works for both axis-aligned and rotated rectangles.
 *
 * Strategy: the opposite corner stays fixed. We use the rectangle's
 * edge directions (computed from the opposite corner) to project the
 * cursor and rebuild all four corners. Then we set all coordinates
 * at once via incomingCoords to avoid inserting extra vertices.
 *
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch drag event.
 * @param {Object} delta - Lng/lat delta from last position.
 */
SRMode.dragVertexPoint = function (state, e, delta) {
  var coordIdx = this.coordinateIndex(state.selectedCoordPaths);
  var coords = state.feature.getCoordinates()[0].slice(); // copy
  var n = coords.length - 1; // last index is closing vertex

  // Treat closing vertex as vertex 0
  if (coordIdx >= n) coordIdx = 0;
  if (coordIdx < 0 || coordIdx >= 4) return;

  // Opposite corner (diagonally across in a 4-vertex rectangle)
  var oppIdx = (coordIdx + 2) % 4;
  // The two neighbours of the opposite corner
  var adjA = (oppIdx + 1) % 4;
  var adjB = (oppIdx + 3) % 4; // same as (oppIdx - 1 + 4) % 4

  var anchor = coords[oppIdx];

  // Edge unit vectors from the fixed anchor to its two neighbours
  var eA = [coords[adjA][0] - anchor[0], coords[adjA][1] - anchor[1]];
  var eB = [coords[adjB][0] - anchor[0], coords[adjB][1] - anchor[1]];

  var lenA = Math.sqrt(eA[0] * eA[0] + eA[1] * eA[1]);
  var lenB = Math.sqrt(eB[0] * eB[0] + eB[1] * eB[1]);
  if (lenA < 1e-12 || lenB < 1e-12) return;

  var uA = [eA[0] / lenA, eA[1] / lenA];
  var uB = [eB[0] / lenB, eB[1] / lenB];

  // Project cursor onto the two edge directions
  var cursor = [e.lngLat.lng - anchor[0], e.lngLat.lat - anchor[1]];
  var projA = cursor[0] * uA[0] + cursor[1] * uA[1];
  var projB = cursor[0] * uB[0] + cursor[1] * uB[1];

  // Compute new positions for the 4 corners
  var newCoords = new Array(4);
  newCoords[oppIdx] = [anchor[0], anchor[1]]; // stays fixed
  newCoords[adjA] = [anchor[0] + projA * uA[0], anchor[1] + projA * uA[1]];
  newCoords[adjB] = [anchor[0] + projB * uB[0], anchor[1] + projB * uB[1]];
  newCoords[coordIdx] = [
    anchor[0] + projA * uA[0] + projB * uB[0],
    anchor[1] + projA * uA[1] + projB * uB[1],
  ];

  // Close the ring (vertex 4 = vertex 0)
  newCoords.push([newCoords[0][0], newCoords[0][1]]);

  // Set all coordinates at once -- avoids inserting extra vertices
  state.feature.incomingCoords([newCoords]);
};

/**
 * Translate the entire feature by the given delta.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Mouse/touch drag event.
 * @param {Object} delta - Lng/lat delta from last position.
 */
SRMode.dragFeature = function (state, e, delta) {
  moveFeatures(this.getSelected(), delta);
  state.dragMoveLocation = e.lngLat;
};

// ══════════════════════════════════════════════════════════════════════
//  SRMode update and click handlers
// ══════════════════════════════════════════════════════════════════════

/**
 * Fire an UPDATE event with the current feature coordinates.
 * Called at the end of drag operations to notify the map.
 */
SRMode.fireUpdate = function () {
  this.map.fire(Constants.events.UPDATE, {
    action: Constants.updateActions.CHANGE_COORDINATES,
    features: this.getSelected().map((f) => f.toGeoJSON()),
  });
};

/**
 * When the mouse leaves the canvas during a drag, fire an update
 * so the feature state is not lost.
 * @param {Object} state - Current mode state.
 */
SRMode.onMouseOut = function (state) {
  if (state.dragMoving) {
    this.fireUpdate();
  }
};

/**
 * Handle mouse-up / touch-end: fire update if dragging, then stop.
 * @param {Object} state - Current mode state.
 */
SRMode.onTouchEnd = SRMode.onMouseUp = function (state) {
  if (state.dragMoving) {
    this.fireUpdate();
  }
  this.stopDragging(state);
};

/**
 * Handle clicking on the active feature: deselect coordinates.
 * @param {Object} state - Current mode state.
 */
SRMode.clickActiveFeature = function (state) {
  state.selectedCoordPaths = [];
  this.clearSelectedCoordinates();
  state.feature.changed();
};

/**
 * Main click handler: dispatches to no-target, active-feature, or
 * inactive-feature click handlers.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Click event.
 */
SRMode.onClick = function (state, e) {
  if (CommonSelectors.noTarget(e)) return this.clickNoTarget(state, e);
  if (CommonSelectors.isActiveFeature(e))
    return this.clickActiveFeature(state, e);
  if (CommonSelectors.isInactiveFeature(e)) return this.clickInactive(state, e);
  this.stopDragging(state);
};

/**
 * Handle clicking on empty space: exit to simple_select if allowed.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Click event.
 */
SRMode.clickNoTarget = function (state, e) {
  if (state.canSelectFeatures) this.changeMode(Constants.modes.SIMPLE_SELECT);
};

/**
 * Handle clicking on an inactive feature: select it if allowed.
 * @param {Object} state - Current mode state.
 * @param {Object} e - Click event.
 */
SRMode.clickInactive = function (state, e) {
  if (state.canSelectFeatures)
    this.changeMode(Constants.modes.SIMPLE_SELECT, {
      featureIds: [e.featureTarget.properties.id],
    });
};

/**
 * Handle the trash action: delete the selected feature.
 */
SRMode.onTrash = function () {
  this.deleteFeature(this.getSelectedIds());
};
