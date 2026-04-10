/**
 * shared.js - Window-level globals shared across all JavaScript modules.
 *
 * These are set on `window` so that every module (main.js, layer modules,
 * draw modules, etc.) can read and write them without circular imports.
 */

/** @type {object} Primary map instance (set to the maplibregl.Map in main.js). */
window.map  = 'main';

/** @type {string} Identifier for the left split-view map pane. */
window.mapA = 'A';

/** @type {string} Identifier for the right split-view map pane. */
window.mapB = 'B';

/** @type {Function|null} Callback invoked when a map feature is clicked. */
window.featureClicked = null;

/** @type {Function|null} Callback invoked after a new layer is added to the map. */
window.layerAdded = null;

/** @type {Object} Registry of active map layers, keyed by layer id. */
window.layers = {};

/** @type {string|null} The currently active cursor style (e.g. 'crosshair'). */
window.currentCursor = null;

/** @type {object|null} MapLibre Draw instance for interactive feature editing. */
window.draw = null;

/** @type {Function|null} Callback invoked when a feature is drawn. */
window.featureDrawn = null;

/** @type {Function|null} Callback invoked when a drawn feature is selected. */
window.featureSelected = null;

/** @type {Function|null} Callback invoked when a drawn feature is modified. */
window.featureModified = null;

/** @type {Function|null} Callback invoked when a feature is added to a draw layer. */
window.featureAdded = null;

/** @type {Function|null} Callback invoked when a drawn feature is deselected. */
window.featureDeselected = null;
