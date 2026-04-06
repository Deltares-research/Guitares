"""Legacy choropleth layer for polygon fill colouring with binned values.

This layer is maintained for backward compatibility. New code should prefer
``PolygonLayer`` which supports the same choropleth features via
``color_by_attribute`` and ``bins``/``colors`` options.
"""

from typing import Any, Dict, List, Optional, Union

from geopandas import GeoDataFrame
from pyogrio import read_dataframe

from .layer import Layer


class ChoroplethLayer(Layer):
    """Choropleth polygon layer with binned colour fills and legends.

    Parameters
    ----------
    map : Any
        The parent map object.
    id : str
        Logical layer identifier.
    map_id : str
        Fully qualified JS-side layer identifier.
    **kwargs : Any
        Passed through to ``Layer.__init__``.
    """

    def __init__(self, map: Any, id: str, map_id: str, **kwargs: Any) -> None:
        super().__init__(map, id, map_id, **kwargs)

    def set_data(
        self,
        data: Union[GeoDataFrame, str],
        color_by_attribute: Optional[Dict[str, Any]] = None,
        legend_items: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """Set polygon data and render the choropleth layer.

        Parameters
        ----------
        data : GeoDataFrame or str
            Polygon geometries, or a file path to read via pyogrio.
        color_by_attribute : dict, optional
            Custom MapLibre paint expression for data-driven fill colours.
        legend_items : list of dict, optional
            Pre-built legend items ``[{style, label}]``.
        """
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            if len(data) == 0:
                data = GeoDataFrame()
            if data.crs != 4326:
                data = data.to_crs(4326)
        else:
            # Read geodataframe from shape file
            data = read_dataframe(data)

        self.data = data

        if not self.big_data:
            if color_by_attribute is None:
                # Add new layer
                self.map.runjs(
                    "/js/polygon_layer.js",
                    "addLayerBins",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.min_zoom,
                        self.hover_property,
                        self.color_property,
                        self.line_color,
                        self.line_width,
                        self.line_opacity,
                        self.fill_opacity,
                        self.legend_title,
                        self.unit,
                        self.legend_position,
                        self.side,
                        self.bins,
                        self.colors,
                        self.color_labels,
                    ],
                )
            elif isinstance(color_by_attribute, dict) and isinstance(
                legend_items, list
            ):
                # Color by attribute
                self.map.runjs(
                    "/js/polygon_layer.js",
                    "addLayerCustom",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.min_zoom,
                        color_by_attribute,
                        legend_items,
                        self.legend_position,
                        self.legend_title,
                    ],
                )
            elif isinstance(color_by_attribute, dict):
                # Color by attribute
                self.map.runjs(
                    "/js/polygon_layer.js",
                    "addLayerCustomNoLegend",
                    arglist=[
                        self.map_id,
                        self.data,
                        self.hover_property,
                        self.min_zoom,
                        color_by_attribute,
                        legend_items,
                        self.legend_position,
                        self.legend_title,
                    ],
                )
        else:
            self.update()

    def update(self) -> None:
        """Update for big-data mode (clip to viewport)."""
        if self.data is None:
            return
        if len(self.data) == 0:
            return
        # Only need to update this layer if it use big data and is visible
        if self.big_data and self.get_visibility():
            if self.map.zoom > self.min_zoom:
                # Zoomed in
                coords = self.map.map_extent
                xl0 = coords[0][0]
                xl1 = coords[1][0]
                yl0 = coords[0][1]
                yl1 = coords[1][1]
                # Limits WGS 84
                gdf = self.data.cx[xl0:xl1, yl0:yl1]
                # Add new layer
                self.map.runjs(
                    "/js/polygon_layer.js",
                    "addLayer",
                    arglist=[
                        self.map_id,
                        gdf,
                        self.min_zoom,
                        self.hover_property,
                        self.color_property,
                        self.line_color,
                        self.line_width,
                        self.line_opacity,
                        self.fill_opacity,
                        self.legend_title,
                        self.unit,
                        self.legend_position,
                        self.side,
                        self.bins,
                        self.colors,
                        self.color_labels,
                    ],
                )
            else:
                # Zoomed out
                # Choropleths are automatically invisible, but legend is not
                self.map.runjs(self.main_js, "hideLegend", arglist=[self.map_id])

    def activate(self) -> None:
        """Set the layer to active mode."""
        self.active = True
        self.map.runjs(
            "/js/polygon_layer.js",
            "activate",
            arglist=[
                self.map_id,
                self.line_color,
                self.fill_color,
                self.line_color_selected,
                self.fill_color_selected,
            ],
        )

    def deactivate(self) -> None:
        """Set the layer to inactive mode."""
        self.active = False
        self.map.runjs(
            "/js/polygon_layer.js",
            "deactivate",
            arglist=[
                self.map_id,
                self.line_color_inactive,
                self.line_width_inactive,
                self.line_style_inactive,
                self.line_opacity_inactive,
                self.fill_color_inactive,
                self.fill_opacity_inactive,
                self.line_color_selected_inactive,
                self.fill_color_selected_inactive,
            ],
        )

    def redraw(self) -> None:
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)
