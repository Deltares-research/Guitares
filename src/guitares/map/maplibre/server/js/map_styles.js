/**
 * map_styles.js — Basemap style loader.
 *
 * Initialises ``window.mapStyles`` and loads individual style definitions
 * from the ``styles/`` folder.  To add a new basemap style, create a new
 * JS file in ``styles/`` that sets ``window.mapStyles["my-style"] = { ... }``
 * and add a ``<script>`` tag below.
 *
 * Styles that require an API token (e.g. Mapbox) should check for the
 * token in ``window.mapboxToken`` before registering themselves.
 */

window.mapStyles = new Object();

// Load individual style files.  Order determines order in the selector.
document.write('<script src="/js/styles/none.js"><\/script>');
document.write('<script src="/js/styles/osm.js"><\/script>');
document.write('<script src="/js/styles/opentopomap.js"><\/script>');
document.write('<script src="/js/styles/carto_voyager.js"><\/script>');
document.write('<script src="/js/styles/positron.js"><\/script>');
document.write('<script src="/js/styles/darkmatter.js"><\/script>');
document.write('<script src="/js/styles/esri_imagery.js"><\/script>');
document.write('<script src="/js/styles/esri_ocean.js"><\/script>');
document.write('<script src="/js/styles/esri_topo.js"><\/script>');
document.write('<script src="/js/styles/mapbox.js"><\/script>');
