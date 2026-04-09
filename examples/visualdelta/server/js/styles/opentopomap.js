window.mapStyles["opentopomap"] = {
  name: "OpenTopoMap",
  version: 8,
  sources: {
    opentopomap: {
      type: "raster",
      tiles: [
        "https://a.tile.opentopomap.org/{z}/{x}/{y}.png",
        "https://b.tile.opentopomap.org/{z}/{x}/{y}.png",
        "https://c.tile.opentopomap.org/{z}/{x}/{y}.png",
      ],
      tileSize: 256,
      attribution: "&copy; OpenTopoMap &copy; OpenStreetMap Contributors",
      maxzoom: 17,
    },
  },
  layers: [{ id: "opentopomap", type: "raster", source: "opentopomap" }],
};
