/**
 * MapLibre GL Ruler Control
 *
 * Click to set a start point, move the mouse to see a great-circle line
 * and distance. Click again to finish. Press Escape to cancel.
 * The control button sits on the right side of the map.
 */

/**
 * Deactivate the ruler if it is currently active.
 * Called from setMouseDefault to ensure the ruler does not interfere
 * with other map interactions.
 */
export function deactivateRuler() {
  if (window.rulerControl && window.rulerControl._active) {
    window.rulerControl._deactivate();
  }
}

/**
 * A MapLibre GL control that measures great-circle distances on the map.
 * Two clicks define a measurement; Escape cancels. The measured line is
 * drawn as a great-circle arc with a popup showing the distance.
 */
export class RulerControl {
  constructor() {
    this._active = false;
    this._startPoint = null;
    this._map = null;
    this._popup = null;
    this._sourceId = '__ruler_line';
    this._layerId = '__ruler_line_layer';
    this._pointLayerId = '__ruler_point_layer';

    // Bound handlers (so we can remove them later)
    this._onClick = this._onClick.bind(this);
    this._onMouseMove = this._onMouseMove.bind(this);
    this._onKeyDown = this._onKeyDown.bind(this);
  }

  /**
   * Called by MapLibre when the control is added to the map.
   * Creates the button element with a ruler SVG icon.
   * @param {Object} map - The MapLibre map instance.
   * @returns {HTMLElement} The control container element.
   */
  onAdd(map) {
    this._map = map;

    this._container = document.createElement('div');
    this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group';

    const button = document.createElement('button');
    button.type = 'button';
    button.title = 'Measure distance';
    button.setAttribute('aria-label', 'Measure distance');
    button.innerHTML = `<svg viewBox="0 0 24 24" width="22" height="22" style="fill:none;stroke:currentColor;stroke-width:1.5;stroke-linecap:round;stroke-linejoin:round;">
      <rect x="2" y="9" width="20" height="6" rx="1" transform="rotate(-45 12 12)"/>
      <line x1="6.5" y1="12.5" x2="8.5" y2="10.5"/>
      <line x1="9" y1="15" x2="12" y2="12"/>
      <line x1="11.5" y1="12.5" x2="13.5" y2="10.5"/>
      <line x1="14" y1="15" x2="17" y2="12"/>
    </svg>`;

    button.addEventListener('click', () => this._toggle());
    this._button = button;
    this._container.appendChild(button);

    return this._container;
  }

  /**
   * Called by MapLibre when the control is removed from the map.
   */
  onRemove() {
    this._deactivate();
    this._container.parentNode.removeChild(this._container);
    this._map = null;
  }

  /** Toggle ruler activation state. */
  _toggle() {
    if (this._active) {
      this._deactivate();
    } else {
      this._activate();
    }
  }

  /**
   * Activate the ruler: add map sources/layers, attach event listeners,
   * and set the cursor to crosshair.
   */
  _activate() {
    this._active = true;
    this._startPoint = null;
    this._button.classList.add('active');
    this._button.style.backgroundColor = '#ddd';

    const map = this._map;

    // Add source and layers
    if (!map.getSource(this._sourceId)) {
      map.addSource(this._sourceId, {
        type: 'geojson',
        data: { type: 'FeatureCollection', features: [] },
      });
    }
    if (!map.getLayer(this._layerId)) {
      map.addLayer({
        id: this._layerId,
        type: 'line',
        source: this._sourceId,
        filter: ['==', '$type', 'LineString'],
        paint: {
          'line-color': '#ff4444',
          'line-width': 2,
          'line-dasharray': [3, 2],
        },
      });
    }
    if (!map.getLayer(this._pointLayerId)) {
      map.addLayer({
        id: this._pointLayerId,
        type: 'circle',
        source: this._sourceId,
        filter: ['==', '$type', 'Point'],
        paint: {
          'circle-radius': 5,
          'circle-color': '#ff4444',
          'circle-stroke-color': '#ffffff',
          'circle-stroke-width': 2,
        },
      });
    }

    // Create popup for distance display
    this._popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: false,
      className: 'ruler-popup',
      offset: [15, 0],
    });

    map.getCanvas().style.cursor = 'crosshair';
    map.on('click', this._onClick);
    map.on('mousemove', this._onMouseMove);
    document.addEventListener('keydown', this._onKeyDown);
  }

  /**
   * Deactivate the ruler: remove map layers/sources, detach listeners,
   * and restore the default cursor.
   */
  _deactivate() {
    this._active = false;
    this._startPoint = null;
    this._button.classList.remove('active');
    this._button.style.backgroundColor = '';

    const map = this._map;
    if (!map) return;

    map.getCanvas().style.cursor = '';
    map.off('click', this._onClick);
    map.off('mousemove', this._onMouseMove);
    document.removeEventListener('keydown', this._onKeyDown);

    // Remove layers and source
    if (map.getLayer(this._layerId)) map.removeLayer(this._layerId);
    if (map.getLayer(this._pointLayerId)) map.removeLayer(this._pointLayerId);
    if (map.getSource(this._sourceId)) map.removeSource(this._sourceId);

    // Remove popup
    if (this._popup) {
      this._popup.remove();
      this._popup = null;
    }
  }

  /**
   * Handle map clicks: first click sets start point, second click
   * finishes the measurement.
   * @param {Object} e - MapLibre click event.
   */
  _onClick(e) {
    if (!this._startPoint) {
      // First click: set start point
      this._startPoint = [e.lngLat.lng, e.lngLat.lat];
      this._updateLine(e.lngLat);
    } else {
      // Second click: finish measurement, keep line visible, reset for next
      this._startPoint = null;
      if (this._popup) this._popup.remove();
    }
  }

  /**
   * Update the ruler line and distance popup as the mouse moves.
   * @param {Object} e - MapLibre mousemove event.
   */
  _onMouseMove(e) {
    if (!this._startPoint) return;
    this._updateLine(e.lngLat);
  }

  /**
   * Cancel the ruler on Escape key.
   * @param {KeyboardEvent} e - Keydown event.
   */
  _onKeyDown(e) {
    if (e.key === 'Escape') {
      this._deactivate();
    }
  }

  /**
   * Redraw the great-circle arc and update the distance popup.
   * @param {Object} lngLat - Current cursor position {lng, lat}.
   */
  _updateLine(lngLat) {
    const start = this._startPoint;
    const end = [lngLat.lng, lngLat.lat];

    // Generate great-circle arc with intermediate points
    const arcPoints = this._greatCircleArc(start, end, 64);

    const geojson = {
      type: 'FeatureCollection',
      features: [
        {
          type: 'Feature',
          geometry: { type: 'LineString', coordinates: arcPoints },
        },
        {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: start },
        },
        {
          type: 'Feature',
          geometry: { type: 'Point', coordinates: end },
        },
      ],
    };

    this._map.getSource(this._sourceId).setData(geojson);

    // Compute distance and show popup
    const distMetres = this._haversineDistance(start, end);
    const label = this._formatDistance(distMetres);

    this._popup
      .setLngLat(lngLat)
      .setHTML(`<div style="font-size:13px;font-weight:bold;padding:2px 6px;">${label}</div>`)
      .addTo(this._map);
  }

  /**
   * Generate points along a great-circle arc between two coordinates.
   * @param {number[]} start - [lng, lat] of the start point.
   * @param {number[]} end - [lng, lat] of the end point.
   * @param {number} nPoints - Number of intermediate points.
   * @returns {number[][]} Array of [lng, lat] coordinates along the arc.
   */
  _greatCircleArc(start, end, nPoints) {
    const toRad = Math.PI / 180;
    const toDeg = 180 / Math.PI;

    const lat1 = start[1] * toRad;
    const lon1 = start[0] * toRad;
    const lat2 = end[1] * toRad;
    const lon2 = end[0] * toRad;

    const d = 2 * Math.asin(
      Math.sqrt(
        Math.pow(Math.sin((lat2 - lat1) / 2), 2) +
        Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin((lon2 - lon1) / 2), 2)
      )
    );

    if (d < 1e-10) return [start, end];

    const points = [];
    for (let i = 0; i <= nPoints; i++) {
      const f = i / nPoints;
      const A = Math.sin((1 - f) * d) / Math.sin(d);
      const B = Math.sin(f * d) / Math.sin(d);
      const x = A * Math.cos(lat1) * Math.cos(lon1) + B * Math.cos(lat2) * Math.cos(lon2);
      const y = A * Math.cos(lat1) * Math.sin(lon1) + B * Math.cos(lat2) * Math.sin(lon2);
      const z = A * Math.sin(lat1) + B * Math.sin(lat2);
      const lat = Math.atan2(z, Math.sqrt(x * x + y * y));
      const lon = Math.atan2(y, x);
      points.push([lon * toDeg, lat * toDeg]);
    }
    return points;
  }

  /**
   * Compute the Haversine distance between two points in metres.
   * @param {number[]} start - [lng, lat] of the start point.
   * @param {number[]} end - [lng, lat] of the end point.
   * @returns {number} Distance in metres.
   */
  _haversineDistance(start, end) {
    const R = 6371000; // Earth radius in metres
    const toRad = Math.PI / 180;
    const dLat = (end[1] - start[1]) * toRad;
    const dLon = (end[0] - start[0]) * toRad;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(start[1] * toRad) * Math.cos(end[1] * toRad) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    return R * c;
  }

  /**
   * Format a distance in metres to a human-readable string.
   * @param {number} metres - Distance in metres.
   * @returns {string} Formatted distance (e.g. "123 m" or "4.56 km").
   */
  _formatDistance(metres) {
    if (metres < 1000) {
      return Math.round(metres) + ' m';
    } else if (metres < 100000) {
      return (metres / 1000).toFixed(2) + ' km';
    } else {
      return (metres / 1000).toFixed(0) + ' km';
    }
  }
}
