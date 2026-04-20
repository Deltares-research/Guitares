"""Circle layer with optional selection and custom paint.

When a ``select`` callback is provided, the layer supports hover popups
and click-based feature selection (single or multiple). Also supports
custom paint dicts for data-driven colouring.
"""

from typing import Any, Dict, List, Optional, Union

from geopandas import GeoDataFrame

from .layer import Layer


class CircleLayer(Layer):
    """Circle layer with optional interactive selection."""

    def __init__(self, map: Any, id: str, map_id: str, **kwargs: Any) -> None:
        super().__init__(map, id, map_id, **kwargs)
        self.selector = "select" in kwargs and kwargs["select"] is not None
        self.index = 0
        self.color_by_attribute: Dict[str, Any] = {}
        self.legend_items: List[Dict[str, Any]] = []

    def _get_map_layer_ids(self) -> List[str]:
        """Circle layer uses a single MapLibre layer with the base id."""
        return [self.map_id]

    def _apply_legend_options(self, options: Dict[str, Any]) -> None:
        """Populate ``options`` with legend keys.

        Prefers caller-supplied ``self.legend_items``. When those are
        empty, auto-derives a single swatch from the layer's own paint
        props so the caller can get a legend with just one kwarg on
        ``add_layer``:

        * ``legend_label="..."`` — preferred; rendered as the single
          swatch's label, no title line above it.
        * ``legend_title="..."`` — back-compat; treated as the label
          (folded into the single swatch). ``legend_title`` is named
          for raster / multi-entry layers where it genuinely labels
          a title line; on a single-entry circle legend it's really
          a label, so ``legend_label`` is the cleaner spelling.
        """
        legend_items = self.legend_items
        legend_title = getattr(self, "legend_title", "")
        legend_label = getattr(self, "legend_label", "")
        if not legend_items and (legend_label or legend_title):
            line_color = getattr(self, "line_color", None)
            line_width = getattr(self, "line_width", 0) or 0
            border = (
                f"{line_width}px solid {line_color}"
                if line_color and line_width
                else "none"
            )
            legend_items = [
                {
                    "style": (
                        f"background-color:{self.fill_color}; "
                        f"border:{border}; border-radius:50%;"
                    ),
                    "label": legend_label or legend_title,
                }
            ]
            legend_title = ""
        if legend_items:
            options["legendItems"] = legend_items
            options["legendTitle"] = legend_title
            options["legendPosition"] = self.legend_position

    def set_data(
        self,
        data: Union[GeoDataFrame, str],
        index: Optional[int] = None,
        color_by_attribute: Optional[Dict[str, Any]] = None,
        legend_items: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Set the GeoJSON data and render the circle layer.

        Parameters
        ----------
        data : GeoDataFrame or str
            Point geometries, or a file path to read.
        index : int, optional
            Initially selected feature index (selector mode only).
        color_by_attribute : dict, optional
            Custom MapLibre paint dict for data-driven colouring.
        legend_items : list, optional
            Pre-built legend items [{style, label}].
        """
        if not isinstance(data, GeoDataFrame):
            from pyogrio import read_dataframe

            data = read_dataframe(data)

        if isinstance(data, GeoDataFrame) and len(data) == 0:
            if self.selector:
                self.clear()
            return

        if data.crs and data.crs != 4326:
            data = data.to_crs(4326)

        self.data = data

        if color_by_attribute is not None:
            self.color_by_attribute = color_by_attribute
        if legend_items is not None:
            self.legend_items = legend_items

        if index is not None:
            self.index = index

        if self.selector:
            # Drop any pre-existing 'index' column to avoid conflicts with promoteId
            if "index" in data.columns:
                data = data.drop(columns=["index"])
            data["index"] = range(len(data))

        pp = self.get_paint_props()
        if self.selector:
            pp["lineColorSelected"] = self.line_color_selected
            pp["fillColorSelected"] = self.fill_color_selected
            pp["circleRadiusSelected"] = self.circle_radius_selected

        options = {
            "minZoom": getattr(self, "min_zoom", 0),
            "beforeIds": self._get_before_ids(),
        }

        if self.selector:
            options["selector"] = True
            options["index"] = self.index
            options["hoverProperty"] = self.hover_property
            options["selectionOption"] = getattr(self, "selection_type", "single")
        elif self.hover_property:
            options["hoverProperty"] = self.hover_property
            options["unit"] = getattr(self, "unit", "")

        if self.color_by_attribute:
            options["paintDict"] = self.color_by_attribute
        self._apply_legend_options(options)

        if not self.big_data:
            self.map.runjs(
                "/js/circle_layer.js",
                "addLayer",
                arglist=[self.map_id, data, pp, options],
            )
        else:
            self.update()

        if self.selector and not self.active:
            self.deactivate()

    def update(self) -> None:
        """Update for big-data mode (clip to viewport)."""
        if not self.map.zoom or self.data is None or len(self.data) == 0:
            return
        if not self.big_data or not self.get_visibility():
            return
        if self.map.zoom > self.min_zoom:
            coords = self.map.map_extent
            gdf = self.data.cx[coords[0][0] : coords[1][0], coords[0][1] : coords[1][1]]
            if len(gdf) == 0:
                return
            pp = self.get_paint_props()
            options = {"minZoom": self.min_zoom, "beforeIds": self._get_before_ids()}
            if self.hover_property:
                options["hoverProperty"] = self.hover_property
                options["unit"] = getattr(self, "unit", "")
            if self.color_by_attribute:
                options["paintDict"] = self.color_by_attribute
            self._apply_legend_options(options)
            self.map.runjs(
                "/js/circle_layer.js",
                "addLayer",
                arglist=[self.map_id, gdf, pp, options],
            )

    def select_by_index(self, index: int) -> None:
        """Select a feature by index (selector mode only)."""
        self.index = index
        self.map.runjs(
            "/js/circle_layer.js",
            "selectByIndex",
            arglist=[self.map_id, index],
        )

    def activate(self) -> None:
        """Set the layer to active paint style."""
        self.active = True
        if self.data is None or len(self.data) == 0:
            return
        self.show()
        pp = self.get_paint_props("active")
        if self.selector:
            pp["lineColorSelected"] = self.line_color_selected
            pp["fillColorSelected"] = self.fill_color_selected
            pp["circleRadiusSelected"] = self.circle_radius_selected
        self.map.runjs(
            "/js/circle_layer.js",
            "activate" if self.selector else "setPaintProperties",
            arglist=[self.map_id, pp],
        )
        # Re-select the current index so the active point is highlighted
        if self.selector and self.index is not None:
            self.select_by_index(self.index)
        if self.big_data:
            self.update()

    def deactivate(self) -> None:
        """Set the layer to inactive paint style."""
        self.active = False
        if self.data is None or len(self.data) == 0:
            return
        pp = self.get_paint_props("inactive")
        if self.selector:
            pp["lineColorSelected"] = self.line_color_inactive
            pp["fillColorSelected"] = self.fill_color_inactive
            pp["circleRadiusSelected"] = self.circle_radius_inactive
        self.map.runjs(
            "/js/circle_layer.js",
            "deactivate" if self.selector else "setPaintProperties",
            arglist=[self.map_id, pp],
        )

    def redraw(self) -> None:
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)
        if not self.get_visibility():
            self.set_visibility(False)
