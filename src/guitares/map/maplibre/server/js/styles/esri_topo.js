window.mapStyles["esri-topo"] = {
  name: "ESRI World Topo",
  version: 8,
  sources: {
    "esri-topo": {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Topo_Map/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      attribution: "&copy; Esri, HERE, Garmin, FAO, NOAA, USGS",
      maxzoom: 19,
    },
  },
  layers: [{ id: "esri-topo", type: "raster", source: "esri-topo" }],
};
