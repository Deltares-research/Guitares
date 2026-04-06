/**
 * Mapbox basemap styles.
 *
 * These styles require a Mapbox access token set in
 * ``window.mapboxToken`` (written by Python via defaults.js).
 * If no token is available, the styles are not registered.
 */

if (window.mapboxToken) {
  var token = window.mapboxToken;

  window.mapStyles["mapbox-streets"] = {
    name: "Mapbox Streets",
    version: 8,
    sources: {
      "mapbox-streets": {
        type: "raster",
        tiles: [
          "https://api.mapbox.com/styles/v1/mapbox/streets-v12/tiles/{z}/{x}/{y}?access_token=" + token,
        ],
        tileSize: 512,
        attribution: "&copy; Mapbox &copy; OpenStreetMap",
        maxzoom: 22,
      },
    },
    layers: [{ id: "mapbox-streets", type: "raster", source: "mapbox-streets" }],
  };

  window.mapStyles["mapbox-satellite"] = {
    name: "Mapbox Satellite",
    version: 8,
    sources: {
      "mapbox-satellite": {
        type: "raster",
        tiles: [
          "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/tiles/{z}/{x}/{y}?access_token=" + token,
        ],
        tileSize: 512,
        attribution: "&copy; Mapbox &copy; DigitalGlobe",
        maxzoom: 22,
      },
    },
    layers: [{ id: "mapbox-satellite", type: "raster", source: "mapbox-satellite" }],
  };

  window.mapStyles["mapbox-satellite-streets"] = {
    name: "Mapbox Satellite Streets",
    version: 8,
    sources: {
      "mapbox-satellite-streets": {
        type: "raster",
        tiles: [
          "https://api.mapbox.com/styles/v1/mapbox/satellite-streets-v12/tiles/{z}/{x}/{y}?access_token=" + token,
        ],
        tileSize: 512,
        attribution: "&copy; Mapbox &copy; OpenStreetMap &copy; DigitalGlobe",
        maxzoom: 22,
      },
    },
    layers: [{ id: "mapbox-satellite-streets", type: "raster", source: "mapbox-satellite-streets" }],
  };

  window.mapStyles["mapbox-light"] = {
    name: "Mapbox Light",
    version: 8,
    sources: {
      "mapbox-light": {
        type: "raster",
        tiles: [
          "https://api.mapbox.com/styles/v1/mapbox/light-v11/tiles/{z}/{x}/{y}?access_token=" + token,
        ],
        tileSize: 512,
        attribution: "&copy; Mapbox &copy; OpenStreetMap",
        maxzoom: 22,
      },
    },
    layers: [{ id: "mapbox-light", type: "raster", source: "mapbox-light" }],
  };

  window.mapStyles["mapbox-dark"] = {
    name: "Mapbox Dark",
    version: 8,
    sources: {
      "mapbox-dark": {
        type: "raster",
        tiles: [
          "https://api.mapbox.com/styles/v1/mapbox/dark-v11/tiles/{z}/{x}/{y}?access_token=" + token,
        ],
        tileSize: 512,
        attribution: "&copy; Mapbox &copy; OpenStreetMap",
        maxzoom: 22,
      },
    },
    layers: [{ id: "mapbox-dark", type: "raster", source: "mapbox-dark" }],
  };

  window.mapStyles["mapbox-outdoors"] = {
    name: "Mapbox Outdoors",
    version: 8,
    sources: {
      "mapbox-outdoors": {
        type: "raster",
        tiles: [
          "https://api.mapbox.com/styles/v1/mapbox/outdoors-v12/tiles/{z}/{x}/{y}?access_token=" + token,
        ],
        tileSize: 512,
        attribution: "&copy; Mapbox &copy; OpenStreetMap",
        maxzoom: 22,
      },
    },
    layers: [{ id: "mapbox-outdoors", type: "raster", source: "mapbox-outdoors" }],
  };
}
