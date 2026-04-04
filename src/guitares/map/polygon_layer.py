"""Polygon layer with optional fill, choropleth, selection, and legend.

Handles simple outlines, flat fills, data-driven choropleths with bins,
custom paint expressions, and interactive polygon selection. All modes
use the unified ``polygon_layer.js`` via a single ``addLayer`` call.

Selector mode is auto-detected from the ``select`` callback kwarg.
Also serves as backend for types ``"choropleth"`` and ``"polygon_selector"``.
"""

from geopandas import GeoDataFrame

from .layer import Layer


class PolygonLayer(Layer):
    """Polygon layer with optional selection and choropleth support."""

    def __init__(self, map, id, map_id, **kwargs):
        super().__init__(map, id, map_id, **kwargs)
        self.selector = "select" in kwargs and kwargs["select"] is not None
        self.index = []
        self.color_by_attribute = {}
        self.legend_items_list = []

    def set_data(self, data, index=None, color_by_attribute=None, legend_items=None):
        """Set GeoJSON data and render the polygon layer.

        Parameters
        ----------
        data : GeoDataFrame or str
            Polygon geometries, or a file path.
        index : int, list, or None
            Selected feature index/indices (selector mode).
        color_by_attribute : dict, optional
            Custom MapLibre paint dict for fill.
        legend_items : list, optional
            Pre-built legend items [{style, label}].
        """
        if not isinstance(data, GeoDataFrame):
            from pyogrio import read_dataframe
            data = read_dataframe(data)

        if isinstance(data, GeoDataFrame) and len(data) == 0:
            data = GeoDataFrame()

        if isinstance(data, GeoDataFrame) and len(data) > 0:
            if data.crs and data.crs != 4326:
                data = data.to_crs(4326)

        self.data = data

        if color_by_attribute is not None:
            self.color_by_attribute = color_by_attribute
        if legend_items is not None:
            self.legend_items_list = legend_items

        # Normalize index to a list
        if index is None:
            self.index = []
        elif isinstance(index, int):
            self.index = [index]
        else:
            self.index = list(index)

        # Add index column for selector mode
        if self.selector and len(data) > 0:
            data["index"] = range(len(data))

        if self.big_data:
            self.update()
            return

        self._render(data)

    def _render(self, data):
        """Build pp and options dicts and call polygon_layer.js addLayer."""
        pp = self.get_paint_props()

        options = {
            "lineStyle": getattr(self, "line_style", "-"),
            "minZoom": getattr(self, "min_zoom", 0),
        }

        # Fill and choropleth options
        if self.color_by_attribute:
            options["paintDict"] = self.color_by_attribute
            options["hoverProperty"] = self.hover_property
            if self.legend_items_list:
                options["legendItems"] = self.legend_items_list
                options["legendTitle"] = getattr(self, "legend_title", "")
                options["legendPosition"] = self.legend_position

        elif hasattr(self, "bins") and self.bins and hasattr(self, "colors") and self.colors:
            options["bins"] = self.bins
            options["colors"] = self.colors
            options["colorProperty"] = self.color_property
            options["hoverProperty"] = self.hover_property
            options["unit"] = getattr(self, "unit", "")
            options["side"] = getattr(self, "side", "")
            if hasattr(self, "color_labels") and self.color_labels:
                options["colorLabels"] = self.color_labels
                options["legendTitle"] = getattr(self, "legend_title", "")
                options["legendPosition"] = self.legend_position

        # Selector options
        if self.selector:
            options["selector"] = True
            options["index"] = self.index
            options["hoverProperty"] = self.hover_property
            options["selectionOption"] = getattr(self, "selection_type", "single")
            pp_selected = self.get_paint_props("selected")
            options["lineColorSelected"] = pp_selected["lineColor"]
            options["lineWidthSelected"] = pp_selected["lineWidth"]
            options["lineOpacitySelected"] = pp_selected["lineOpacity"]
            options["fillColorSelected"] = pp_selected["fillColor"]
            options["fillOpacitySelected"] = pp_selected["fillOpacity"]
            pp_hover = self.get_paint_props("hover")
            options["fillColorHover"] = pp_hover["fillColor"]
            options["fillOpacityHover"] = pp_hover["fillOpacity"]
            options["lineWidthHover"] = pp_hover["lineWidth"]

        self.map.runjs(
            "/js/polygon_layer.js", "addLayer",
            arglist=[self.map_id, data, pp, options],
        )

    def update(self):
        """Update for big-data mode (clip to viewport)."""
        if self.data is None or len(self.data) == 0:
            return
        if not self.big_data or not self.get_visibility():
            return
        if self.map.zoom > self.min_zoom:
            coords = self.map.map_extent
            gdf = self.data.cx[coords[0][0]:coords[1][0], coords[0][1]:coords[1][1]]
            self._render(gdf)
        else:
            self.map.runjs(self.main_js, "hideLegend", arglist=[self.map_id])

    def select_by_index(self, index):
        """Select features by index (selector mode).

        Parameters
        ----------
        index : int or list
            Feature index or list of indices.
        """
        if isinstance(index, int):
            index = [index]
        self.index = index
        self.map.runjs(
            "/js/polygon_layer.js", "selectByIndex",
            arglist=[self.map_id, index],
        )

    def select_by_property(self, property_name, value):
        """Select features by matching a property value.

        Parameters
        ----------
        property_name : str
            GeoDataFrame column name.
        value
            Value to match.
        """
        if not isinstance(self.data, GeoDataFrame):
            return
        if property_name not in self.data.columns:
            return
        index = self.data[self.data[property_name] == value].index.tolist()
        if index:
            self.select_by_index(index)

    def set_hover_property(self, hover_property):
        """Change the hover property and redraw."""
        self.hover_property = hover_property
        self.set_data(self.data, self.index)

    def activate(self):
        """Set the layer to active mode."""
        self.active = True
        if self.data is None:
            return
        self.map.runjs(
            "/js/polygon_layer.js", "activate",
            arglist=[self.map_id, self.line_color],
        )

    def deactivate(self):
        """Set the layer to inactive mode."""
        self.active = False
        if self.data is None:
            return
        self.map.runjs(
            "/js/polygon_layer.js", "deactivate",
            arglist=[self.map_id, self.line_color_inactive],
        )

    def redraw(self):
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data, self.index)
        if not self.get_visibility():
            self.set_visibility(False)
