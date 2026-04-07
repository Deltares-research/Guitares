/**
 * Custom MapboxDraw mode for drawing a polyline with fixed-distance
 * segments. Each new point is placed at exactly ``distance`` km from
 * the previous point, along the bearing from the previous point to
 * the cursor.
 *
 * Uses Turf.js for geodetically correct distance/bearing calculations.
 *
 * Usage:
 *   draw.changeMode('draw_fixed_distance', { distance: 100 });
 *
 * where ``distance`` is the segment length in kilometres.
 */

const DrawFixedDistance = {};

DrawFixedDistance.onSetup = function (opts) {
  const state = {
    distance: opts.distance || 100,  // km
    points: [],                       // array of [lon, lat]
    currentVertex: null,              // snapped preview point
    line: this.newFeature({
      type: 'Feature',
      properties: {},
      geometry: {
        type: 'LineString',
        coordinates: [],
      },
    }),
  };
  this.addFeature(state.line);
  this.setActionableState({ trash: true });
  return state;
};

DrawFixedDistance.onClick = function (state, e) {
  // Double-click detection
  const now = Date.now();
  if (state.lastClickTime && (now - state.lastClickTime) < 300) {
    // Double-click — finish drawing
    if (state.points.length >= 2) {
      this.finishDrawing(state);
      return;
    }
  }
  state.lastClickTime = now;

  if (state.points.length === 0) {
    // First click — place freely
    const pt = [e.lngLat.lng, e.lngLat.lat];
    state.points.push(pt);
    state.line.updateCoordinate(0, pt[0], pt[1]);
  } else if (state.currentVertex) {
    // Subsequent clicks — use the snapped position
    const pt = state.currentVertex;
    state.points.push(pt);
    const idx = state.points.length - 1;
    state.line.updateCoordinate(idx, pt[0], pt[1]);
  }
};

DrawFixedDistance.onMouseMove = function (state, e) {
  if (state.points.length === 0) return;

  // Compute bearing from last point to cursor
  const lastPt = state.points[state.points.length - 1];
  const cursorPt = [e.lngLat.lng, e.lngLat.lat];

  const from = turf.point(lastPt);
  const to = turf.point(cursorPt);
  const bearing = turf.bearing(from, to);

  // Place the preview point at exactly `distance` km along that bearing
  const dest = turf.destination(from, state.distance, bearing, { units: 'kilometers' });
  const snapped = dest.geometry.coordinates;

  state.currentVertex = snapped;

  // Update the line preview (all existing points + snapped preview)
  const idx = state.points.length;
  state.line.updateCoordinate(idx, snapped[0], snapped[1]);
};

DrawFixedDistance.onKeyUp = function (state, e) {
  if (e.keyCode === 13) {
    // Enter — finish drawing
    this.finishDrawing(state);
  } else if (e.keyCode === 27) {
    // Escape — cancel
    this.deleteFeature([state.line.id], { silent: true });
    this.changeMode('simple_select');
  }
};

DrawFixedDistance.onStop = function (state) {
  this.updateUIClasses({ mouse: 'none' });

  // Remove trailing coordinate used for preview
  const coords = state.line.getCoordinates();
  if (coords.length > state.points.length) {
    state.line.removeCoordinate(state.points.length);
  }

  if (state.points.length < 2) {
    this.deleteFeature([state.line.id], { silent: true });
    return;
  }

  // Clean up coordinates
  state.line.setCoordinates(state.points);

  this.map.fire('draw.create', {
    features: [state.line.toGeoJSON()],
  });
};

DrawFixedDistance.finishDrawing = function (state) {
  if (state.points.length < 2) {
    this.deleteFeature([state.line.id], { silent: true });
  }
  this.changeMode('simple_select', { featureIds: [state.line.id] });
};

DrawFixedDistance.onTap = DrawFixedDistance.onClick;

DrawFixedDistance.toDisplayFeatures = function (state, geojson, display) {
  display(geojson);

  // Draw circles at each placed point
  for (let i = 0; i < state.points.length; i++) {
    display({
      type: 'Feature',
      properties: {
        meta: 'vertex',
        active: 'true',
      },
      geometry: {
        type: 'Point',
        coordinates: state.points[i],
      },
    });
  }

  // Draw preview point
  if (state.currentVertex) {
    display({
      type: 'Feature',
      properties: {
        meta: 'vertex',
        active: 'true',
      },
      geometry: {
        type: 'Point',
        coordinates: state.currentVertex,
      },
    });
  }
};

export { DrawFixedDistance };
