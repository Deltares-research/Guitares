window.mapStyles["esri-ocean"] = {
  name: "ESRI Ocean",
  version: 8,
  sources: {
    "esri-ocean": {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/Ocean/World_Ocean_Base/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      attribution: "&copy; Esri, GEBCO, NOAA, National Geographic, DeLorme",
      maxzoom: 16,
    },
  },
  layers: [{ id: "esri-ocean", type: "raster", source: "esri-ocean" }],
};
