from .layer import Layer

class ImageLayer(Layer):
    def __init__(self, mapbox, id):
        super().__init__(mapbox, id)
        self.active = False
        self.type   = "image"

    def activate(self):
        self.active = True

    def deactivate(self):
        self.active = False


    def clear(self):
        self.active = False
        js_string = "import('/main.js').then(module => {module.removeLayer('" + self.id + "')});"
        self.mapbox.view.page().runJavaScript(js_string)

    def update(self):
#        print("Updating image layer")
        pass

    def set_image(self,
                  image_file=None,
                  legend_title="",
                  cmin=None,
                  cmax=None,
                  cstep=None,
                  decimals=None,
                  colormap="jet"):

        id_string = self.id

        dataset = rasterio.open(image_file)

        src_crs = 'EPSG:4326'
        dst_crs = 'EPSG:3857'

        with rasterio.open(image_file) as src:
            transform, width, height = calculate_default_transform(
                src.crs, dst_crs, src.width, src.height, *src.bounds)
            kwargs = src.meta.copy()
            kwargs.update({
                'crs': dst_crs,
                'transform': transform,
                'width': width,
                'height': height
            })
            bnds = src.bounds

            mem_file = MemoryFile()
            with mem_file.open(**kwargs) as dst:
                for i in range(1, src.count + 1):
                    reproject(
                        source=rasterio.band(src, i),
                        destination=rasterio.band(dst, i),
                        src_transform=src.transform,
                        src_crs=src.crs,
                        dst_transform=transform,
                        dst_crs=dst_crs,
                        resampling=Resampling.nearest)

                band1 = dst.read(1)

        new_bounds = transform_bounds(dst_crs, src_crs,
                                      dst.bounds[0],
                                      dst.bounds[1],
                                      dst.bounds[2],
                                      dst.bounds[3])
        isn = np.where(band1 < 0.001)
        band1[isn] = np.nan

        band1 = np.flipud(band1)
        cminimum = np.nanmin(band1)
        cmaximum = np.nanmax(band1)

        norm = matplotlib.colors.Normalize(vmin=cminimum, vmax=cmaximum)
        vnorm = norm(band1)

        cmap = cm.get_cmap(colormap)
        im = Image.fromarray(np.uint8(cmap(vnorm) * 255))

        overlay_file = "overlay.png"
        im.save(os.path.join(self.mapbox.server_path, overlay_file))

        # # Make new layer
        # layer = Layer(name=layer_name, type="image")
        # layer.id = id_string
        # layer_group = self.find_layer_group(layer_group_name)
        # layer_group[layer_name] = layer

        # Bounds
        bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]
        bounds_string = "[[" + str(bounds[0][0]) + "," + str(bounds[0][1]) + "],[" + str(bounds[1][0]) + "," + str(bounds[1][1]) + "]]"

        # Legend
        clrbar = ColorBar(colormap=colormap, legend_title=legend_title)
        clrbar.make(cmin, cmax, cstep=cstep, decimals=decimals)
        clrmap_string = clrbar.to_json()

        js_string = "import('/main.js').then(module => {module.addImageLayer('" + overlay_file + "','" + id_string + "'," + bounds_string + "," + clrmap_string + ")});"
        self.mapbox.view.page().runJavaScript(js_string)
