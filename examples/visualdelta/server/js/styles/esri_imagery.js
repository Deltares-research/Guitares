window.mapStyles["esri-imagery"] = {
  name: "ESRI World Imagery",
  version: 8,
  sources: {
    "esri-imagery": {
      type: "raster",
      tiles: [
        "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
      ],
      tileSize: 256,
      attribution: "&copy; Esri, DigitalGlobe, Earthstar Geographics, CNES/Airbus DS",
      maxzoom: 19,
    },
  },
  layers: [{ id: "esri-imagery", type: "raster", source: "esri-imagery" }],
};
