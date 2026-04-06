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
