"""Line layer with optional circle vertices and optional selection.

When ``selector=True`` is passed as a keyword argument, the layer supports
hover popups and click-based feature selection (single or multiple).
"""

from typing import Any, List, Optional

from geopandas import GeoDataFrame

from .layer import Layer


class LineLayer(Layer):
    """Line layer with optional interactive selection."""

    def __init__(self, map: Any, id: str, map_id: str, **kwargs: Any) -> None:
        super().__init__(map, id, map_id, **kwargs)
        # Default to no circles and no selection
        self.circle_radius = kwargs.get("circle_radius", 0)
        # Selector mode is enabled when a select callback is provided
        self.selector = "select" in kwargs and kwargs["select"] is not None
        self.index = 0

    def _get_map_layer_ids(self) -> List[str]:
        """Line layer creates .line and optionally .circle sub-layers."""
        return [f"{self.map_id}.line", f"{self.map_id}.circle"]

    def set_data(self, data: GeoDataFrame, index: Optional[int] = None) -> None:
        """Set the GeoJSON data and render the line layer.

        Parameters
        ----------
        data : GeoDataFrame
            LineString geometries to display.
        index : int, optional
            Initially selected feature index (selector mode only).
        """
        self.data = data

        if isinstance(data, GeoDataFrame):
            if len(data) == 0:
                self.map.runjs("/js/main.js", "removeLayer", arglist=[self.map_id])
                return
            data["index"] = range(len(data))
            data_in = data.to_crs(4326)
        else:
            return

        if index is not None:
            self.index = index

        pp = self.get_paint_props()

        # Add selected paint props for selector mode
        if self.selector:
            pp["lineColorSelected"] = self.line_color_selected
            pp["lineWidthSelected"] = self.line_width_selected

        options = {"beforeIds": self._get_before_ids()}
        if self.selector:
            options["selector"] = True
            options["index"] = self.index
            options["hoverProperty"] = getattr(self, "hover_property", None) or getattr(
                self, "hover_param", None
            )
            options["selectionOption"] = getattr(self, "selection_type", "single")

        self.map.runjs(
            "/js/line_layer.js",
            "addLayer",
            arglist=[self.map_id, data_in, pp, options],
        )

        if not self.active:
            self.deactivate()

    def set_selected_index(self, index: int) -> None:
        """Select a feature by index (selector mode only).

        Parameters
        ----------
        index : int
            Feature index to select.
        """
        self.index = index
        self.map.runjs(
            "/js/line_layer.js",
            "setSelectedIndex",
            arglist=[self.map_id, index],
        )

    def activate(self) -> None:
        """Set the layer to active paint style."""
        self.active = True
        pp = self.get_paint_props("active")
        if self.selector:
            pp["lineColorSelected"] = self.line_color_selected
            pp["lineWidthSelected"] = self.line_width_selected
        self.map.runjs(
            "/js/line_layer.js",
            "setPaintProperties",
            arglist=[self.map_id, pp],
        )

    def deactivate(self) -> None:
        """Set the layer to inactive paint style."""
        self.active = False
        self.map.runjs(
            "/js/line_layer.js",
            "setPaintProperties",
            arglist=[self.map_id, self.get_paint_props("inactive")],
        )

    def redraw(self) -> None:
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)
        if not self.get_visibility():
            self.set_visibility(False)
