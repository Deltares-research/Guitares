window.mapStyles["carto-voyager"] = {
  name: "CartoDB Voyager",
  version: 8,
  sources: {
    "carto-voyager": {
      type: "raster",
      tiles: [
        "https://basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}.png",
      ],
      tileSize: 256,
      attribution: "&copy; CARTO &copy; OpenStreetMap Contributors",
      maxzoom: 19,
    },
  },
  layers: [{ id: "carto-voyager", type: "raster", source: "carto-voyager" }],
};
