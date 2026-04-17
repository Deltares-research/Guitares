"""Base map layer class and layer-tree utilities.

Provides the ``Layer`` class that all specialized layer types inherit from,
along with helper functions for traversing the layer hierarchy.
"""

import logging
from typing import Any, Dict, List, Optional

import matplotlib.colors as mcolors

logger = logging.getLogger(__name__)


class Layer:
    """Base class for all map layers.

    Manages visibility, paint properties, z-ordering, and the nested
    layer hierarchy used by the map widget.

    Parameters
    ----------
    map : Any
        The parent map object (MapLibre, Mapbox, etc.).
    id : str
        Logical layer identifier within its parent container.
    map_id : str
        Fully qualified dot-separated identifier used on the JS side.
    **kwargs : Any
        Override any default attribute (e.g. ``line_color``, ``fill_opacity``).
    """

    def __init__(self, map: Any, id: str, map_id: str, **kwargs: Any) -> None:
        self.map = map
        self.id = id
        self.map_id = map_id
        self.map_ids = [map_id]
        self.visible = True
        self.active = True
        self.type = "container"
        self.layer = {}
        self.parent = None
        self.data = None
        self.index = None
        self.select = None
        self.crs = 4326
        self.color_values = None
        self.color_map = "jet"
        self.color_property = "value"
        self.selection_type = "single"
        self.min_zoom = 0
        self.max_zoom = 22
        self.zoom_switch = 999
        self.decimals = 1
        self.big_data = False
        self.opacity = 0.9
        self.url = None
        self.option = None
        self.zbmax = 0.1
        self.get_data = None  # Function to get data for this layer, if needed
        self.map_overlay_options = {}  # Dict or callable returning dict, passed to map_overlay()

        # Legend
        self.legend_position = "bottom-right"  # Options are "top-left", "top-right", "bottom-left", "bottom-right"
        self.legend_title = (
            ""  # The text that appears at the top of the legend (e.g. Topography)
        )
        self.legend_label = (
            ""  # The text that appears next to the legend (e.g. elevation [m])
        )
        self.legend_units = ""  # The unit string that may appear in the individual tick labels (e.g. "m")
        self.legend_decimals = -1  # -1 means automatic
        self.legend_dict = None  # A dictionary with the legend values and colors

        # Raster layers
        self.color_scale_auto = True  # automatically scale from min to max
        self.color_scale_cmin = -1000.0
        self.color_scale_cmax = 1000.0
        self.color_scale_symmetric = True
        self.color_scale_symmetric_side = "min"
        self.hillshading = False
        self.hillshading_exaggeration = 10.0
        self.hillshading_azimuth = 315.0
        self.hillshading_altitude = 30.0
        self.quality = "high"
        self.scale_factor = 1.0

        # Cyclone track layer
        self.show_icons = True

        # Marker layer
        self.icon_file = None
        self.icon_size = 1.0
        self.marker_color = "blue"
        self.hover_property = None
        self.click_property = None
        self.click_popup_width = None
        self.click_popup_height = None

        # Paint properties

        # Active paint properties
        self.line_color = "dodgerblue"
        self.line_width = 2
        self.line_style = "-"
        self.line_opacity = 1.0
        self.fill_color = "dodgerblue"
        self.fill_opacity = 0.25
        self.circle_radius = 4

        # Inactive paint properties
        self.line_color_inactive = "lightgrey"
        self.line_width_inactive = 2
        self.line_style_inactive = "-"
        self.line_opacity_inactive = 1.0
        self.fill_color_inactive = "lightgrey"
        self.fill_opacity_inactive = 0.0
        self.circle_radius_inactive = 2

        # Selected paint properties
        self.line_color_selected = "red"
        self.line_width_selected = 3
        self.line_style_selected = "-"
        self.line_opacity_selected = 1.0
        self.fill_color_selected = "red"
        self.fill_opacity_selected = 0.75
        self.circle_radius_selected = 5

        # Selected inactive paint properties
        self.line_color_selected_inactive = "lightgrey"
        self.line_width_selected_inactive = 2
        self.line_style_selected_inactive = "-"
        self.line_opacity_selected_inactive = 1.0
        self.fill_color_selected_inactive = "lightgrey"
        self.fill_opacity_selected_inactive = 0.0
        self.circle_radius_selected_inactive = 2

        # Hover paint properties
        self.line_color_hover = "dodgerblue"
        self.line_width_hover = 3
        self.line_style_hover = "-"
        self.line_opacity_hover = 1.0
        self.fill_color_hover = "dodgerblue"
        self.fill_opacity_hover = 0.5
        self.circle_radius_hover = 5

        # Determine which main.js file to use
        map_type = type(self.map).__name__.lower()
        if map_type == "maplibre" or map_type == "mapbox":
            # Regular map
            self.main_js = "/js/main.js"
            self.side = "main"
        elif map_type == "maplibrecompare" or map_type == "mapboxcompare":
            # Compare map
            self.main_js = "/js/compare.js"
            self.side = "a"

        # Set attributes based on kwargs
        for key, value in kwargs.items():
            setattr(self, key, value)

        # Convert colors to hex
        if self.line_color != "transparent":
            self.line_color = mcolors.to_hex(self.line_color)
        if self.fill_color != "transparent":
            self.fill_color = mcolors.to_hex(self.fill_color)
        if self.line_color_inactive != "transparent":
            self.line_color_inactive = mcolors.to_hex(self.line_color_inactive)
        if self.fill_color_inactive != "transparent":
            self.fill_color_inactive = mcolors.to_hex(self.fill_color_inactive)
        if self.line_color_selected != "transparent":
            self.line_color_selected = mcolors.to_hex(self.line_color_selected)
        if self.fill_color_selected != "transparent":
            self.fill_color_selected = mcolors.to_hex(self.fill_color_selected)
        if self.line_color_selected_inactive != "transparent":
            self.line_color_selected_inactive = mcolors.to_hex(
                self.line_color_selected_inactive
            )
        if self.fill_color_selected_inactive != "transparent":
            self.fill_color_selected_inactive = mcolors.to_hex(
                self.fill_color_selected_inactive
            )
        if self.line_color_hover != "transparent":
            self.line_color_hover = mcolors.to_hex(self.line_color_hover)
        if self.fill_color_hover != "transparent":
            self.fill_color_hover = mcolors.to_hex(self.fill_color_hover)

        # For use in javascript
        self.paint_properties = {
            "lineColor": self.line_color,
            "lineWidth": self.line_width,
            "lineOpacity": self.line_opacity,
            "fillColor": self.fill_color,
            "fillOpacity": self.fill_opacity,
            "circleRadius": self.circle_radius,
            "lineColorInactive": self.line_color_inactive,
            "lineWidthInactive": self.line_width_inactive,
            "lineStyleInactive": self.line_style_inactive,
            "lineOpacityInactive": self.line_opacity_inactive,
            "fillColorInactive": self.fill_color_inactive,
            "fillOpacityInactive": self.fill_opacity_inactive,
            "circleRadiusInactive": self.circle_radius_inactive,
            "lineColorSelected": self.line_color_selected,
            "lineWidthSelected": self.line_width_selected,
            "lineStyleSelected": self.line_style_selected,
            "lineOpacitySelected": self.line_opacity_selected,
            "fillColorSelected": self.fill_color_selected,
            "fillOpacitySelected": self.fill_opacity_selected,
            "circleRadiusSelected": self.circle_radius_selected,
            "lineColorSelectedInactive": self.line_color_selected_inactive,
            "lineWidthSelectedInactive": self.line_width_selected_inactive,
            "lineStyleSelectedInactive": self.line_style_selected_inactive,
            "lineOpacitySelectedInactive": self.line_opacity_selected_inactive,
            "fillColorSelectedInactive": self.fill_color_selected_inactive,
            "fillOpacitySelectedInactive": self.fill_opacity_selected_inactive,
            "circleRadiusSelectedInactive": self.circle_radius_selected_inactive,
            "lineColorHover": self.line_color_hover,
            "lineWidthHover": self.line_width_hover,
            "lineStyleHover": self.line_style_hover,
            "lineOpacityHover": self.line_opacity_hover,
            "fillColorHover": self.fill_color_hover,
            "fillOpacityHover": self.fill_opacity_hover,
            "circleRadiusHover": self.circle_radius_hover,
        }

    def _get_map_layer_ids(self) -> List[str]:
        """Return the MapLibre layer IDs this layer creates on the map.

        Subclasses override this to list the actual sub-layer IDs they use
        (e.g. ``[id + '.fill', id + '.line']`` for polygons).

        Returns
        -------
        list of str
            MapLibre layer IDs.
        """
        return [self.map_id]

    def _get_before_ids(self) -> List[str]:
        """Return MapLibre layer IDs from later siblings for z-ordering.

        When a layer is (re-)added to MapLibre, it should be inserted
        before the first of these IDs that already exists on the map.
        This preserves the intended stacking order defined by the Python
        layer tree.

        Layers may also set ``self.before_layer_ids`` (list of MapLibre
        layer IDs) to force placement under specific external layers
        (e.g. ``"dummy_layer_0"`` to pin a background raster to the
        bottom of the stack regardless of sibling order).

        Returns
        -------
        list of str
            MapLibre layer IDs that should appear above this layer.
        """
        before_ids: List[str] = []
        if self.parent is not None:
            siblings = list(self.parent.layer.values())
            found_self = False
            for sibling in siblings:
                if sibling is self:
                    found_self = True
                    continue
                if found_self:
                    before_ids.extend(sibling._get_map_layer_ids())
                    # Also recurse into container children
                    if sibling.layer:
                        for child in sibling.layer.values():
                            before_ids.extend(child._get_map_layer_ids())
        # Honour an explicit forced placement target.
        forced = getattr(self, "before_layer_ids", None)
        if forced:
            before_ids.extend(forced)
        return before_ids

    def get_paint_props(self, state: str = "active") -> Dict[str, Any]:
        """Return a paint properties dict for the given state.

        Parameters
        ----------
        state : str
            One of "active", "inactive", "selected", "selected_inactive", "hover".

        Returns
        -------
        dict
            Paint properties with camelCase keys matching the JS conventions.
        """
        suffix = "" if state == "active" else f"_{state}"
        return {
            "lineColor": getattr(self, f"line_color{suffix}"),
            "lineWidth": getattr(self, f"line_width{suffix}"),
            "lineStyle": getattr(self, f"line_style{suffix}", "-"),
            "lineOpacity": getattr(self, f"line_opacity{suffix}"),
            "fillColor": getattr(self, f"fill_color{suffix}"),
            "fillOpacity": getattr(self, f"fill_opacity{suffix}"),
            "circleRadius": getattr(self, f"circle_radius{suffix}"),
        }

    def add_layer(
        self, layer_id: str, type: Optional[str] = None, **kwargs: Any
    ) -> Optional["Layer"]:
        """Add a child layer to this container.

        Parameters
        ----------
        layer_id : str
            Identifier for the new child layer.
        type : str, optional
            Layer type (e.g. ``"circle"``, ``"line"``, ``"polygon"``).
            If *None*, a generic container layer is created.
        **kwargs : Any
            Passed through to the layer constructor.

        Returns
        -------
        Layer or None
            The newly created (or existing) layer, or *None* on error.
        """

        if layer_id in self.layer:
            # Layer already exists
            return self.layer[layer_id]

        map_id = f"{self.map_id}.{layer_id}"

        if type is None:
            # Add containing layer
            self.layer[layer_id] = Layer(self.map, layer_id, map_id)
            self.layer[layer_id].parent = self
            return self.layer[layer_id]

        else:
            if self.type != "container":
                logger.error(f"Error! Can not add layer to layer of type: {self.type}")
                return None

            if (
                type == "circle" or type == "circle_selector"
            ):  # keep circle_selector for backward compatibility
                from .circle_layer import CircleLayer

                self.layer[layer_id] = CircleLayer(self.map, layer_id, map_id, **kwargs)

            elif (
                type == "line" or type == "line_selector"
            ):  # keep line_selector for backward compatibility
                from .line_layer import LineLayer

                self.layer[layer_id] = LineLayer(self.map, layer_id, map_id, **kwargs)

            elif (
                type == "polygon" or type == "choropleth" or type == "polygon_selector"
            ):  # keep choropleth and polygon_selector for backward compatibility
                from .polygon_layer import PolygonLayer

                self.layer[layer_id] = PolygonLayer(
                    self.map, layer_id, map_id, **kwargs
                )

            elif type == "heatmap":
                from .heatmap_layer import HeatmapLayer

                self.layer[layer_id] = HeatmapLayer(
                    self.map, layer_id, map_id, **kwargs
                )

            elif type == "draw":
                from .draw_layer import DrawLayer

                self.layer[layer_id] = DrawLayer(self.map, layer_id, map_id, **kwargs)

            elif (
                type == "raster_image" or type == "raster" or type == "image"
            ):  # keep raster and image for backward compatibility
                from .raster_image_layer import RasterImageLayer

                self.layer[layer_id] = RasterImageLayer(
                    self.map, layer_id, map_id, **kwargs
                )

            # elif type == "raster_from_tiles":
            #    from .raster_from_tiles_layer import RasterFromTilesLayer
            #    self.layer[layer_id] = RasterFromTilesLayer(self.map, layer_id, map_id, **kwargs)

            # elif type == "deck_geojson":
            #     from .deck_geojson_layer import DeckGeoJSONLayer
            #     self.layer[layer_id] = DeckGeoJSONLayer(self.map, layer_id, map_id, **kwargs)

            # elif type == "datashader_choropleth":
            #     from .datashader_choropleth_layer import DatashaderChoroplethLayer
            #     self.layer[layer_id] = DatashaderChoroplethLayer(self.map, layer_id, map_id, **kwargs)

            elif type == "cyclone_track":
                from .cyclone_track_layer import CycloneTrackLayer

                self.layer[layer_id] = CycloneTrackLayer(
                    self.map, layer_id, map_id, **kwargs
                )

            elif type == "marker":
                from .marker_layer import MarkerLayer

                self.layer[layer_id] = MarkerLayer(self.map, layer_id, map_id, **kwargs)

            # elif type == "raster_tile":
            #    from .raster_tile_layer import RasterTileLayer
            #    self.layer[layer_id] = RasterTileLayer(self.map, layer_id, map_id, **kwargs)

            else:
                logger.error(f"Layer type {self.type} not recognized!")
                return None

            self.layer[layer_id].type = type
            self.layer[layer_id].parent = self

            return self.layer[layer_id]

    def layer_added(self) -> None:
        """Apply initial visibility and active state after the layer is added."""
        if not self.visible:
            self.hide()
        if not self.active:
            self.deactivate()

    def update(self) -> None:
        """Re-render the layer after a map zoom or pan change.

        Subclasses override this for viewport-dependent rendering.
        """
        pass

    def delete(self) -> None:
        """Remove this layer and all nested children from the map."""
        # First clear layers on map
        self.clear()

        # And now remove layer from layer dict
        if self.parent:
            self.parent.layer.pop(self.id)
        else:
            self.map.layer.pop(self.id)

    def clear(self) -> None:
        """Clear this layer and all nested layers from the map."""
        if self.layer:
            # Container layer
            layers = list_layers(self.layer)
            for layer in layers:
                layer.clear()
        else:
            self.map.runjs(
                self.main_js, "removeLayer", arglist=[self.map_id, self.side]
            )
            # self.delete_from_map()
            self.data = None

    # def delete_from_map(self):
    #     self.map.runjs(self.main_js, "removeLayer", arglist=[self.map_id, self.side])

    def set_mode(self, mode: str) -> None:
        """Set the layer mode to ``"active"``, ``"inactive"``, or ``"invisible"``.

        Parameters
        ----------
        mode : str
            One of ``"active"``, ``"inactive"``, or ``"invisible"``.
        """
        if not self.layer:
            # Data layer
            if mode == "active":
                self.show()
                self.activate()
            elif mode == "inactive":
                self.show()
                self.deactivate()
            else:  # Invisible
                self.hide()
                self.deactivate()

    def show(self) -> None:
        """Show layer on map. Any child layers that are set to visible will also be shown."""
        self.visible = True
        self.set_visibility(True)

    def hide(self) -> None:
        """Hide layer on map. Any child layers will also be hidden."""
        self.visible = False
        self.set_visibility(False)

    def set_visibility(self, true_or_false: bool) -> None:
        """Recursively show or hide layers in the hierarchy.

        Parameters
        ----------
        true_or_false : bool
            *True* to show, *False* to hide.
        """
        if self.layer:
            # Container layer
            for name in self.layer:
                if true_or_false and self.layer[name].visible:
                    self.layer[name].set_visibility(True)
                else:
                    self.layer[name].set_visibility(False)

        else:
            # Data layer
            if true_or_false:
                # Child may be visible, but of parents may be invisible, so check here
                if self.get_visibility():
                    self.map.runjs(
                        self.main_js, "showLayer", arglist=[self.map_id, self.side]
                    )
                else:
                    self.map.runjs(
                        self.main_js, "hideLayer", arglist=[self.map_id, self.side]
                    )
            else:
                self.map.runjs(
                    self.main_js, "hideLayer", arglist=[self.map_id, self.side]
                )

    # def set_visibility(self, true_or_false):
    #     # Loop down through the layer hierarchy to show or hide layers
    #     if self.layer:
    #         # Container layer
    #         for name in self.layer:
    #             if true_or_false and self.layer[name].visible:
    #                 self.layer[name].show()
    #             else:
    #                 self.layer[name].hide()
    #     else:
    #         # Data layer
    #         if true_or_false:
    #             self.visible = True
    #             # Child may be visible, but of parents may be invisible, so check here
    #             if self.get_visibility():
    #                 self.map.runjs(self.main_js, "showLayer", arglist=[self.map_id, self.side])
    #             else:
    #                 self.map.runjs(self.main_js, "hideLayer", arglist=[self.map_id, self.side])
    #         else:
    #             self.visible = False
    #             self.map.runjs(self.main_js, "hideLayer", arglist=[self.map_id, self.side])

    def set_opacity(self, opacity: float) -> None:
        """Set the layer opacity.

        Parameters
        ----------
        opacity : float
            Opacity value between 0.0 (transparent) and 1.0 (opaque).
        """
        self.opacity = opacity
        self.map.runjs(
            self.main_js, "setOpacity", arglist=[self.map_id, self.side, opacity]
        )

    def get_visibility(self) -> bool:
        """Check whether the layer is visible, walking up the parent chain.

        Returns
        -------
        bool
            *True* if this layer and all its ancestors are visible.
        """
        if self.visible:
            if self.parent:
                return self.parent.get_visibility()
            else:
                return True
        else:
            return False

    def activate(self) -> None:
        """Activate the layer. Subclasses override for custom behaviour."""
        pass

    def deactivate(self) -> None:
        """Deactivate the layer. Subclasses override for custom behaviour."""
        pass

    def get(self, layer_id: str) -> Optional["Layer"]:
        """Return a child layer by its identifier, or *None* if not found.

        Parameters
        ----------
        layer_id : str
            Child layer identifier.

        Returns
        -------
        Layer or None
        """
        if layer_id in self.layer:
            return self.layer[layer_id]
        else:
            return None

    def redraw(self) -> None:
        """Redraw the layer after a style change. Subclasses override."""
        pass


def list_layers(
    layer_dict: Dict[str, Layer],
    layer_type: str = "all",
    layer_list: Optional[List[Layer]] = None,
) -> List[Layer]:
    """Recursively collect layers from a nested layer dictionary.

    Parameters
    ----------
    layer_dict : dict
        Dictionary of ``Layer`` objects keyed by name.
    layer_type : str, optional
        Filter by layer type (default ``"all"``).
    layer_list : list, optional
        Accumulator list (used internally for recursion).

    Returns
    -------
    list of Layer
        Flat list of matching layers.
    """
    if not layer_list:
        layer_list = []
    for layer_name in layer_dict:
        layer = layer_dict[layer_name]
        if layer_type != "all":
            if layer.type == layer_type:
                layer_list.append(layer)
        else:
            layer_list.append(layer)

        if layer.layer:
            layer_list = list_layers(
                layer.layer, layer_list=layer_list, layer_type=layer_type
            )
    return layer_list


def find_layer_by_id(
    layer_id: str,
    layer_dict: Dict[str, Layer],
    layer_type: str = "all",
    layer_list: Optional[List[Layer]] = None,
) -> Optional[Layer]:
    """Find a layer by its ``map_id`` in a nested layer dictionary.

    Parameters
    ----------
    layer_id : str
        The ``map_id`` to search for.
    layer_dict : dict
        Dictionary of ``Layer`` objects keyed by name.
    layer_type : str, optional
        Filter by layer type (default ``"all"``).
    layer_list : list, optional
        Not used (kept for API compatibility).

    Returns
    -------
    Layer or None
        The matching layer, or *None* if not found.
    """
    layer_list = list_layers(layer_dict)
    for layer in layer_list:
        if layer.map_id == layer_id:
            return layer
    return None
