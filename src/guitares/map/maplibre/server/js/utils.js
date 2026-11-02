/**
 * utils.js — Shared helpers for map layer modules.
 *
 * Import from layer modules:
 *   import { getMap, findBeforeId, getDashArray, cleanUp } from './utils.js';
 */

/**
 * Return the map object for the given side panel.
 * @param {string} [side] - Panel identifier ("a", "b", or undefined for default).
 * @returns {object} The corresponding map instance.
 */
export function getMap(side) {
  if (side === 'a') return window.mapA || map;
  if (side === 'b') return window.mapB || map;
  return map;
}

/**
 * Find the first layer ID from a list that already exists on the map.
 * Used as the ``beforeId`` argument to ``map.addLayer()`` to maintain
 * sibling z-order.
 * @param {object} mp - Map instance.
 * @param {string[]} beforeIds - Candidate layer IDs from later siblings.
 * @returns {string|undefined}
 */
export function findBeforeId(mp, beforeIds) {
  if (!beforeIds || beforeIds.length === 0) return undefined;
  for (const id of beforeIds) {
    if (mp.getLayer(id)) return id;
  }
  return undefined;
}

/**
 * Convert a dash style string to a MapLibre line-dasharray value.
 * @param {string} style - "-" (solid), "--" (dashed), ".." (dotted).
 * @returns {number[]}
 */
/**
 * Whether a layer holds the topmost feature under the cursor among the
 * layers in a registry. Stacked features (e.g. a point on the end of a
 * line) would otherwise all react to the same mouse event: layers with a
 * hover popup register in window.hoverLayers and layers with click
 * selection in window.clickLayers, and only the topmost one responds.
 *
 * @param {object} mp - Map instance.
 * @param {object} point - Screen point of the mouse event (e.point).
 * @param {string} layerId - Map layer id of the feature of this layer.
 * @param {Object} registry - window.hoverLayers or window.clickLayers.
 * @returns {boolean}
 */
export function isTopmost(mp, point, layerId, registry) {
  const ids = Object.keys(registry || {}).filter((id) => mp.getLayer(id));
  if (ids.length < 2) return true;
  const top = mp.queryRenderedFeatures(point, { layers: ids })[0];
  return !top || top.layer.id === layerId;
}

/** Hover variant of isTopmost. */
export function isTopmostHover(mp, point, layerId) {
  return isTopmost(mp, point, layerId, window.hoverLayers);
}

/** Click-selection variant of isTopmost. */
export function isTopmostClick(mp, point, layerId) {
  return isTopmost(mp, point, layerId, window.clickLayers);
}

export function getDashArray(style) {
  if (style === '--') return [2, 1];
  if (style === '..') return [0.5, 1];
  return [1];
}

/**
 * Remove existing sub-layers and source for a given layer ID.
 * @param {object} mp - Map instance.
 * @param {string} id - Base layer ID.
 * @param {string[]} [suffixes] - Sub-layer suffixes to remove.
 */
export function cleanUp(mp, id, suffixes = ['.line', '.fill', '.circle']) {
  for (const suffix of suffixes) {
    if (mp.getLayer(id + suffix)) mp.removeLayer(id + suffix);
  }
  if (mp.getSource(id)) mp.removeSource(id);
  const legend = document.getElementById('legend' + id);
  if (legend) legend.remove();
}
