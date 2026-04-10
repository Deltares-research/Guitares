/**
 * Custom MapboxDraw mode for drawing a smooth spline polyline.
 *
 * The user clicks to place control points. The drawn line is rendered
 * as a Bézier spline through those points using Turf.js. On finish
 * (Enter or double-click), the smoothed coordinates are emitted.
 *
 * Usage:
 *   draw.changeMode('draw_spline', { resolution: 10000, sharpness: 0.85 });
 *
 * ``resolution`` controls the number of output points (default 10000).
 * ``sharpness`` controls how closely the spline follows the control
 * points (0–1, default 0.85).
 */

const DrawSpline = {};

DrawSpline.onSetup = function (opts) {
  const state = {
    resolution: opts.resolution || 10000,
    sharpness: opts.sharpness || 0.85,
    controlPoints: [],
    currentCursor: null,
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

DrawSpline.onClick = function (state, e) {
  const pt = [e.lngLat.lng, e.lngLat.lat];

  // Double-click detection: if close to last point, finish
  if (state.controlPoints.length >= 2) {
    const last = state.controlPoints[state.controlPoints.length - 1];
    const dist = Math.sqrt(
      Math.pow(pt[0] - last[0], 2) + Math.pow(pt[1] - last[1], 2)
    );
    if (dist < 0.0001) {
      this.finishDrawing(state);
      return;
    }
  }

  state.controlPoints.push(pt);
  _updateSpline(state);
};

DrawSpline.onMouseMove = function (state, e) {
  if (state.controlPoints.length === 0) return;
  state.currentCursor = [e.lngLat.lng, e.lngLat.lat];
  _updateSpline(state);
};

DrawSpline.onKeyUp = function (state, e) {
  if (e.keyCode === 13) {
    // Enter — finish
    this.finishDrawing(state);
  } else if (e.keyCode === 27) {
    // Escape — cancel
    this.deleteFeature([state.line.id], { silent: true });
    this.changeMode('simple_select');
  }
};

DrawSpline.onStop = function (state) {
  this.updateUIClasses({ mouse: 'none' });

  if (state.controlPoints.length < 2) {
    this.deleteFeature([state.line.id], { silent: true });
    return;
  }

  // Final spline without cursor preview
  const splineCoords = _computeSpline(
    state.controlPoints, state.resolution, state.sharpness
  );
  state.line.setCoordinates(splineCoords);

  this.map.fire('draw.create', {
    features: [state.line.toGeoJSON()],
  });
};

DrawSpline.finishDrawing = function (state) {
  if (state.controlPoints.length < 2) {
    this.deleteFeature([state.line.id], { silent: true });
  }
  this.changeMode('simple_select', { featureIds: [state.line.id] });
};

DrawSpline.onTap = DrawSpline.onClick;

DrawSpline.toDisplayFeatures = function (state, geojson, display) {
  display(geojson);

  // Draw control points as vertices
  for (let i = 0; i < state.controlPoints.length; i++) {
    display({
      type: 'Feature',
      properties: { meta: 'vertex', active: 'true' },
      geometry: {
        type: 'Point',
        coordinates: state.controlPoints[i],
      },
    });
  }
};

// ── Internal helpers ─────────────────────────────────────────────

function _updateSpline(state) {
  // Build points array including cursor for preview
  const pts = [...state.controlPoints];
  if (state.currentCursor && pts.length >= 1) {
    pts.push(state.currentCursor);
  }

  if (pts.length < 2) {
    state.line.setCoordinates(pts);
    return;
  }

  const splineCoords = _computeSpline(pts, state.resolution, state.sharpness);
  state.line.setCoordinates(splineCoords);
}

function _computeSpline(controlPoints, resolution, sharpness) {
  if (controlPoints.length < 2) return controlPoints;

  const lineString = turf.lineString(controlPoints);
  try {
    const spline = turf.bezierSpline(lineString, {
      resolution: resolution,
      sharpness: sharpness,
    });
    return spline.geometry.coordinates;
  } catch (e) {
    // Fall back to straight line if spline fails
    return controlPoints;
  }
}

export { DrawSpline };
