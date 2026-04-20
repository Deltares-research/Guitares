import glob
import os
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import matplotlib
import numpy as np
import rasterio
import rioxarray
import xarray as xr
from matplotlib import cm
from matplotlib.colors import LightSource
from PIL import Image
from pyproj import Transformer

from guitares.colormap import cm2png

from .layer import Layer


class RasterImageLayer(Layer):
    """Raster image layer that renders data as a PNG overlay on the map.

    Supports four data modes (set via ``set_data``):

    1. **File path** — GeoTIFF, optionally with overview levels.
    2. **DataArray** — rioxarray DataArray (scalar or RGB).
    3. **map_overlay object** — any object with a ``map_overlay()`` method
       that writes a PNG and returns True/False.
    4. **Callable** — a function that returns a DataArray for the current
       view extent.
    """

    def __init__(self, map: Any, id: str, map_id: str, **kwargs: Any) -> None:
        super().__init__(map, id, map_id, **kwargs)
        self.active = False
        self.type = "raster"
        self.new = True
        self.file_name = map_id + ".png"
        self.data_has_map_overlay = False
        self.rgb = False

        # Reserve z-order position by creating blank placeholder layers.
        before_ids = self._get_before_ids()
        self.map.runjs(
            "/js/raster_image_layer.js",
            "addLayer",
            id=self.map_id + ".a",
            side=self.side,
            beforeIds=before_ids,
        )
        self.map.runjs(
            "/js/raster_image_layer.js",
            "addLayer",
            id=self.map_id + ".b",
            side=self.side,
            beforeIds=before_ids,
        )

    def _get_map_layer_ids(self) -> List[str]:
        """Raster image layer creates .a and .b sub-layers."""
        return [f"{self.map_id}.a", f"{self.map_id}.b"]

    def activate(self) -> None:
        """Activate the raster image layer."""
        self.active = True
        self.show()

    def deactivate(self) -> None:
        """Deactivate the raster image layer."""
        self.active = False

    def clear(self) -> None:
        self.active = False
        self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])
        self.new = True
        self.data = None
        self.data_has_map_overlay = False

    def set_data(
        self, data: Union[str, os.PathLike, xr.DataArray, Callable, Any], **kwargs
    ) -> None:
        """Set the data source and trigger an initial render.

        Parameters
        ----------
        data : str, PathLike, DataArray, object, or callable
            One of: file path (GeoTIFF), rioxarray DataArray,
            object with ``map_overlay()`` method, or callable
            returning a DataArray.
        """
        self.data_has_map_overlay = False
        self.data_has_overview_levels = False

        if isinstance(data, (str, os.PathLike)):
            self.data = data
            with rasterio.open(data) as src:
                self.data_has_overview_levels = len(src.overviews(1)) > 0

        elif hasattr(data, "rio") and hasattr(data.rio, "reproject"):
            self.data = data

        elif hasattr(data, "map_overlay") and callable(getattr(data, "map_overlay")):
            self.data = data
            self.data_has_map_overlay = True

        elif callable(data):
            # Callable data source — don't update immediately; the next
            # moveend event will trigger update() with correct dimensions.
            self.get_data = data
            return

        else:
            raise ValueError(
                "Data must be a file path, DataArray, object with "
                "map_overlay(), or a callable"
            )

        self.update()

    # ------------------------------------------------------------------
    # Update — called on every map pan / zoom
    # ------------------------------------------------------------------

    def update(self) -> None:
        """Re-render the overlay for the current map extent."""
        if not self.map.map_extent:
            return

        coords = self.map.map_extent
        lonlim = [coords[0][0], coords[1][0]]
        latlim = [coords[0][1], coords[1][1]]
        width = self.map.view.geometry().width()
        height = self.map.view.geometry().height()

        # Skip if window hasn't been sized yet (e.g. during maximize)
        if width <= 0 or height <= 0:
            return

        if self.data_has_map_overlay:
            result = self._update_from_map_overlay(lonlim, latlim, width)
        else:
            result = self._update_from_raster(lonlim, latlim, height)

        if result is None:
            return

        overlay_file, west, east, south, north, legend = result

        # Generate continuous colorbar PNG if needed
        if isinstance(legend, str) and legend == "__plot_png__":
            legend = self._create_legend_png()

        # Build legend from color_values if set on the layer
        if legend is None and self.color_values is not None:
            legend = self._build_legend_from_color_values()

        # Handle dateline crossing and send to map
        self._send_to_map(overlay_file, west, east, south, north, legend)

    # ------------------------------------------------------------------
    # Data mode: map_overlay object
    # ------------------------------------------------------------------

    def _update_from_map_overlay(
        self, lonlim: List[float], latlim: List[float], width: int
    ) -> Optional[Tuple[str, float, float, float, float, Any]]:
        """Delegate rendering to the data object's map_overlay method."""
        fname = os.path.join(self.map.server_path, "overlays", self.file_name)

        # Resolve map_overlay_options (dict or callable)
        opts = self.map_overlay_options
        if callable(opts):
            opts = opts()
        if not isinstance(opts, dict):
            opts = {}

        okay = self.data.map_overlay(
            fname, xlim=lonlim, ylim=latlim, width=width, **opts
        )

        if not okay:
            self.clear()
            return None

        overlay_file = f"./overlays/{self.file_name}"
        legend = self._build_legend_from_options(opts)

        return overlay_file, lonlim[0], lonlim[1], latlim[0], latlim[1], legend

    # ------------------------------------------------------------------
    # Data mode: raster DataArray / file path / callable
    # ------------------------------------------------------------------

    def _update_from_raster(
        self, lonlim: List[float], latlim: List[float], height: int
    ) -> Optional[Tuple[str, float, float, float, float, Any]]:
        """Render a raster DataArray (or file / callable) to a PNG overlay."""
        clip = True
        derefine = True

        if self.get_data is not None:
            self.data = self.get_data()
            clip = False
            derefine = False

        if self.data is None:
            return None

        # Load data from file or use in-memory DataArray
        data, data_is_rgb = self._load_raster_data(latlim, height)
        if data is None:
            data = self.data
            data_is_rgb = False

        if clip:
            data = self._clip_to_view(data, lonlim, latlim)

        if derefine:
            data = self._derefine(data, latlim, height)

        # Convert to RGBA array
        if data_is_rgb:
            x, y, rgb = self._render_rgb(data)
            legend = None
        else:
            x, y, rgb, legend = self._render_scalar(data)

        # Reproject to Web Mercator, save PNG, compute bounds
        overlay_file, west, east, south, north = self._reproject_and_save(
            x, y, rgb, data
        )

        return overlay_file, west, east, south, north, legend

    def _load_raster_data(
        self, latlim: List[float], height: int
    ) -> Tuple[Optional[xr.DataArray], bool]:
        """Load raster data from file path, detecting RGB and overview levels."""
        if not isinstance(self.data, (str, os.PathLike)):
            return None, False

        if self.data_has_overview_levels:
            max_cell_size = (latlim[1] - latlim[0]) / height * 111000
            with rasterio.open(self.data) as src:
                overview_level, _ = get_appropriate_overview_level(src, max_cell_size)
                data = rioxarray.open_rasterio(
                    self.data, masked=False, overview_level=overview_level
                )
        else:
            data = rioxarray.open_rasterio(self.data, masked=False)

        data_is_rgb = data.shape[0] in (3, 4)
        if not data_is_rgb and data.shape[0] == 1:
            data = data.squeeze("band", drop=True)

        return data, data_is_rgb

    def _clip_to_view(
        self, data: xr.DataArray, lonlim: List[float], latlim: List[float]
    ) -> xr.DataArray:
        """Clip DataArray to the current map view with a small buffer."""
        dlon = (lonlim[1] - lonlim[0]) / 10
        dlat = (latlim[1] - latlim[0]) / 10
        return data.rio.clip_box(
            minx=lonlim[0] - dlon,
            miny=latlim[0] - dlat,
            maxx=lonlim[1] + dlon,
            maxy=latlim[1] + dlat,
            crs="EPSG:4326",
        )

    def _derefine(
        self, data: xr.DataArray, latlim: List[float], height: int
    ) -> xr.DataArray:
        """Down-sample data if it's finer than the screen resolution."""
        y = data["y"].values[:]
        dy = abs(y[1] - y[0]) if len(y) > 1 else 1e6
        if data.rio.crs.is_geographic:
            dy *= 111000
        req_dy = 0.5 * 111000 * (latlim[1] - latlim[0]) / height
        if dy < req_dy:
            fact = int(np.ceil(req_dy / dy))
            # Round up to next power of 2 (max 64)
            for p2 in (2, 4, 8, 16, 32, 64):
                if fact <= p2:
                    fact = p2
                    break
            else:
                fact = 64
            data = data.isel(x=slice(0, None, fact), y=slice(0, None, fact))
        return data

    def _build_legend_from_color_values(self) -> Dict[str, Any]:
        """Build a discrete legend dict from the layer's color_values.

        Supports color_values entries with either:
        - ``color`` (hex string) and ``text`` (label)
        - ``rgb`` (tuple) and ``string`` (label)

        Returns
        -------
        dict
            Legend dict with ``title`` and ``contour`` list.
        """
        contour = []
        for cv in self.color_values:
            if "color" in cv:
                color = cv["color"]
            elif "rgb" in cv:
                r, g, b = cv["rgb"]
                color = f"#{int(r):02x}{int(g):02x}{int(b):02x}"
            elif "hex" in cv:
                color = cv["hex"]
            else:
                continue
            text = cv.get("text") or cv.get("string", "")
            if not text:
                if "lower_value" in cv and "upper_value" in cv:
                    text = f"{cv['lower_value']} - {cv['upper_value']}"
                elif "lower_value" in cv:
                    text = f">= {cv['lower_value']}"
                elif "upper_value" in cv:
                    text = f"< {cv['upper_value']}"
            contour.append({"color": color, "text": text})
        return {"title": self.legend_title, "contour": contour}

    def _build_legend_from_options(
        self, opts: Dict[str, Any]
    ) -> Optional[Union[Dict[str, Any], str]]:
        """Build a legend dict from map_overlay_options.

        Supports two legend types based on the options keys:

        - **Discrete** (``labels`` + ``colors``): builds a contour-style
          legend with colored swatches. If ``colors`` has ``shape`` info
          or the values are rendered as dots, use ``"circle"`` shape.
        - **Continuous** (``cmap`` + ``cmin`` + ``cmax``): triggers PNG
          colorbar generation.

        Returns None if the options don't contain legend info.
        """
        if opts.get("legend") is False:
            # Explicitly disabled
            if "cmin" in opts and "cmax" in opts and "cmap" in opts:
                self._cmin = opts["cmin"]
                self._cmax = opts["cmax"]
                self._cmap = cm.get_cmap(opts["cmap"])
            return None

        if "labels" in opts and "colors" in opts:
            contour = []
            for val, color in opts["colors"].items():
                text = opts["labels"].get(val, str(val))
                contour.append({"color": color, "text": text, "shape": "circle"})
            title = opts.get("legend_title", self.legend_title or "")
            return {"title": title, "contour": contour}

        if "cmin" in opts and "cmax" in opts and "cmap" in opts:
            self._cmin = opts["cmin"]
            self._cmax = opts["cmax"]
            self._cmap = cm.get_cmap(opts["cmap"])
            return "__plot_png__"

        return None

    def _render_rgb(
        self, data: xr.DataArray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Extract x, y, rgba from an RGB(A) DataArray."""
        x = data["x"].values[:]
        y = data["y"].values[:]
        rgb = data.values[:].astype(np.uint8)
        if rgb.shape[0] == 3:
            alpha = np.ones((1, rgb.shape[1], rgb.shape[2]), dtype=rgb.dtype) * 255
            rgb = np.vstack((rgb, alpha))
        return x, y, rgb

    def _render_scalar(
        self, data: xr.DataArray
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, Any]:
        """Render a scalar DataArray to an RGBA array with color mapping.

        Returns (x, y, rgb, legend) where legend is either a dict
        (discrete contour), ``"__plot_png__"`` (continuous colorbar), or None.
        """
        x = data["x"].values[:]
        y = data["y"].values[:]
        if y[0] < y[-1]:
            y = np.flipud(y)
            z = np.flipud(data.values[:])
        else:
            z = data.values[:]

        if self.color_values is not None:
            rgb, legend = self._render_discrete(z, data.shape)
        else:
            rgb, legend = self._render_continuous(x, y, z)

        rgb = np.transpose(rgb, (2, 0, 1))
        return x, y, rgb, legend

    def _render_discrete(
        self, z: np.ndarray, shape: Tuple[int, ...]
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """Map scalar values to discrete RGBA classes."""
        rgba = np.zeros((shape[0], shape[1], 4), dtype=np.float32)
        contour = []

        for color_value in self.color_values:
            cnt = {"color": color_value["color"]}
            color_rgba = cm.colors.to_rgba(color_value["color"])

            if "lower_value" in color_value and "upper_value" in color_value:
                mask = (z >= color_value["lower_value"]) & (
                    z < color_value["upper_value"]
                )
                cnt["text"] = color_value.get(
                    "text",
                    f"{color_value['lower_value']} - {color_value['upper_value']}",
                )
            elif "lower_value" in color_value:
                mask = z >= color_value["lower_value"]
                cnt["text"] = color_value.get(
                    "text", f">= {color_value['lower_value']}"
                )
            elif "upper_value" in color_value:
                mask = z < color_value["upper_value"]
                cnt["text"] = color_value.get("text", f"< {color_value['upper_value']}")
            else:
                continue

            rgba[mask, :] = color_rgba
            contour.append(cnt)

        rgb = rgba * 255
        legend = {"title": self.legend_title, "contour": contour}
        return rgb, legend

    def _render_continuous(
        self, x: np.ndarray, y: np.ndarray, z: np.ndarray
    ) -> Tuple[np.ndarray, str]:
        """Map scalar values to a continuous colormap, optionally with hillshading."""
        # Determine color scale
        if self.color_scale_auto:
            if self.color_scale_symmetric:
                if self.color_scale_symmetric_side == "min":
                    cmin = np.nanmin(z)
                    if cmin > 0:
                        cmin = -cmin
                    cmax = -cmin
                elif self.color_scale_symmetric_side == "max":
                    cmax = np.nanmax(z)
                    if cmax < 0:
                        cmax = -cmax
                    cmin = -cmax
                else:
                    cmx = max(abs(np.nanmin(z)), abs(np.nanmax(z)))
                    cmin, cmax = -cmx, cmx
            else:
                cmin = np.nanmin(z)
                cmax = np.nanmax(z)
            if cmax < cmin + 0.01:
                cmin, cmax = -0.01, 0.01
        else:
            cmin = self.color_scale_cmin
            cmax = self.color_scale_cmax

        cmap = cm.get_cmap(self.color_map)

        # Store for use by other layers (e.g. model bathymetry overlay)
        self.current_cmin = cmin
        self.current_cmax = cmax
        self.current_cmap = cmap
        self._cmin = cmin
        self._cmax = cmax
        self._cmap = cmap

        if self.hillshading:
            ls = LightSource(azdeg=315, altdeg=30)
            dx = (x[1] - x[0]) / 2
            dy = -(y[1] - y[0]) / 2
            rgb = ls.shade(
                z,
                cmap,
                vmin=cmin,
                vmax=cmax,
                dx=dx * 0.5,
                dy=dy * 0.5,
                vert_exag=10.0,
                blend_mode="soft",
            )
            rgb = rgb * 255
        else:
            norm = matplotlib.colors.Normalize(vmin=cmin, vmax=cmax)
            rgb = cmap(norm(z)) * 255

        return rgb, "__plot_png__"

    # ------------------------------------------------------------------
    # Image output helpers
    # ------------------------------------------------------------------

    def _reproject_and_save(
        self, x: np.ndarray, y: np.ndarray, rgb: np.ndarray, data: xr.DataArray
    ) -> Tuple[str, float, float, float, float]:
        """Reproject RGBA to EPSG:3857, save PNG, return overlay path and bounds."""
        rgba_da = xr.DataArray(
            rgb,
            dims=["band", "y", "x"],
            coords={"band": [0, 1, 2, 3], "y": y, "x": x},
        )

        src_crs = data.rio.crs
        rgba_da.rio.set_spatial_dims(x_dim="x", y_dim="y", inplace=True)
        rgba_da.rio.write_crs(src_crs, inplace=True)

        rgba_3857 = rgba_da.rio.reproject("EPSG:3857")

        # Export as PNG
        rgba_3857 = rgba_3857.fillna(0).clip(min=0, max=255)
        img_data = rgba_3857.values.astype(np.uint8)
        if img_data.shape[0] == 4:
            img_data = np.transpose(img_data, (1, 2, 0))

        image = Image.fromarray(img_data, mode="RGBA")
        overlay_file = "./overlays/" + self.file_name
        image.save(os.path.join(self.map.server_path, "overlays", self.file_name))

        # Compute geographic bounds from the reprojected raster
        left, bottom, right, top = rgba_3857.rio.bounds()
        transformer = Transformer.from_crs("EPSG:3857", "EPSG:4326", always_xy=True)
        west, south = transformer.transform(left, bottom)
        east, north = transformer.transform(right, top)

        # Handle full-globe edge case
        if left < -19800000.0 and right > 19800000.0:
            if west > 0.0:
                west = -180.0
            if east < 0.0:
                east = 180.0

        if west > east:
            west -= 360.0
        if west < -180.0:
            west += 360.0
            east += 360.0

        return overlay_file, west, east, south, north

    def _create_legend_png(self) -> str:
        """Generate a continuous colorbar PNG and return its relative URL."""
        overlays = os.path.join(self.map.server_path, "overlays")

        # Clean up old legend files
        for f in glob.glob(os.path.join(overlays, self.map_id + ".legend.*.png")):
            try:
                os.remove(f)
            except OSError:
                pass

        # Random suffix to bust browser cache
        rstring = str(np.random.randint(1, 1_000_000))
        legend_file = f"{self.map_id}.legend.{rstring}.png"

        cm2png(
            self._cmap,
            file_name=os.path.join(overlays, legend_file),
            orientation="vertical",
            legend_label=self.legend_label,
            vmin=self._cmin,
            vmax=self._cmax,
            width=1.0,
            height=1.5,
        )

        return "./overlays/" + legend_file

    def _send_to_map(
        self,
        overlay_file: str,
        west: float,
        east: float,
        south: float,
        north: float,
        legend: Any,
    ) -> None:
        """Send the overlay image to MapLibre, handling dateline splits."""
        before_ids = self._get_before_ids()

        if east > 180.0:
            # Dateline crossing — split into two images
            im = Image.open(os.path.join(self.map.server_path, overlay_file))
            npixx = im.size[0]
            dlon = east - west
            ipixx = int(npixx * (180.0 - west) / dlon)

            file_a = overlay_file.replace(".png", ".a.png")
            file_b = overlay_file.replace(".png", ".b.png")
            im.crop((0, 0, ipixx, im.size[1])).save(
                os.path.join(self.map.server_path, file_a)
            )
            im.crop((ipixx + 1, 0, im.size[0], im.size[1])).save(
                os.path.join(self.map.server_path, file_b)
            )

            self.map.runjs(
                self.main_js,
                "showLayer",
                arglist=[self.map_id + ".b", self.side],
            )
            self.map.runjs(
                "/js/raster_image_layer.js",
                "updateLayer",
                id=self.map_id + ".a",
                filename=file_a,
                bounds=[[west, 180.0], [south, north]],
                colorbar=legend,
                legend_position=self.legend_position or "bottom-right",
                side=self.side,
                opacity=self.opacity,
                beforeIds=before_ids,
            )
            self.map.runjs(
                "/js/raster_image_layer.js",
                "updateLayer",
                id=self.map_id + ".b",
                filename=file_b,
                bounds=[[-180.0, east - 360.0], [south, north]],
                side=self.side,
                opacity=self.opacity,
                beforeIds=before_ids,
            )
        else:
            self.map.runjs(
                "/js/raster_image_layer.js",
                "updateLayer",
                id=self.map_id + ".a",
                filename=overlay_file,
                bounds=[[west, east], [south, north]],
                colorbar=legend,
                legend_position=self.legend_position or "bottom-right",
                side=self.side,
                opacity=self.opacity,
                beforeIds=before_ids,
            )
            self.map.runjs(
                self.main_js,
                "hideLayer",
                arglist=[self.map_id + ".b", self.side],
            )


def get_appropriate_overview_level(
    src: rasterio.io.DatasetReader, max_pixel_size: float
) -> int:
    """Determine the appropriate rasterio overview level for a given pixel size.

    Parameters
    ----------
    src : rasterio.io.DatasetReader
        The rasterio dataset reader.
    max_pixel_size : float
        Maximum pixel size in metres.

    Returns
    -------
    tuple of (int, bool)
        Overview level index and whether overviews exist.
    """
    original_resolution = src.res
    if src.crs.is_geographic:
        original_resolution = (
            original_resolution[0] * 111000,
            original_resolution[1] * 111000,
        )

    overview_levels = src.overviews(1)
    if not overview_levels:
        return 0, False

    resolutions = [
        (original_resolution[0] * factor, original_resolution[1] * factor)
        for factor in overview_levels
    ]

    selected_overview = 0
    for i, (x_res, y_res) in enumerate(resolutions):
        if x_res <= max_pixel_size and y_res <= max_pixel_size:
            selected_overview = i
        else:
            break

    return selected_overview, True
