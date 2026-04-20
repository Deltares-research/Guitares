"""Interactive drawing layer for creating and editing map features.

Supports polygon, polyline, and rectangle shapes with per-feature
selection, modification, and deletion callbacks.
"""

import logging
import math
import random
import string
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

import geopandas as gpd
import matplotlib.colors as mcolors
import pandas as pd
import pyproj
import shapely
from shapely.geometry import Polygon
from shapely.ops import transform

from .layer import Layer

logger = logging.getLogger(__name__)


class DrawLayer(Layer):
    def __init__(
        self,
        map: Any,
        layer_id: str,
        map_id: str,
        columns: Optional[Dict[str, Any]] = None,
        shape: str = "polygon",
        create: Optional[Callable] = None,
        modify: Optional[Callable] = None,
        select: Optional[Callable] = None,
        deselect: Optional[Callable] = None,
        add: Optional[Callable] = None,
        rotate: bool = True,
        polygon_line_color: str = "dodgerblue",
        polygon_line_width: int = 2,
        polygon_line_style: str = "-",
        polygon_line_opacity: float = 1.0,
        polygon_fill_color: str = "dodgerblue",
        polygon_fill_opacity: float = 0.5,
        polyline_line_color: str = "limegreen",
        polyline_line_width: int = 2,
        polyline_line_style: str = "-",
        polyline_line_opacity: float = 1.0,
        circle_line_color: str = "black",
        circle_line_opacity: float = 1.0,
        circle_fill_color: str = "orangered",
        circle_fill_opacity: float = 0.5,
        circle_radius: int = 4,
        show_endpoints: bool = False,
        endpoint_start_color: str = "blue",
        endpoint_end_color: str = "red",
        endpoint_radius: int = 5,
        **kwargs: Any,
    ) -> None:
        super().__init__(map, layer_id, map_id, **kwargs)

        self.active = False
        self.type = "draw"
        self.shape = shape
        self.mode = (
            "active"  # Draw layers can have three modes: active, inactive, invisible
        )
        self.gdf = gpd.GeoDataFrame()
        self.columns = columns if columns is not None else {}
        self.create = create
        self.modify = modify
        self.select = select
        self.deselect = deselect
        self.add = add

        # Get Hex values for colors
        self.paint_props = {}
        self.paint_props["polygon_line_color"] = mcolors.to_hex(polygon_line_color)
        self.paint_props["polygon_line_width"] = polygon_line_width
        self.paint_props["polygon_line_style"] = polygon_line_style
        self.paint_props["polygon_line_opacity"] = polygon_line_opacity
        self.paint_props["polygon_fill_color"] = mcolors.to_hex(polygon_fill_color)
        self.paint_props["polygon_fill_opacity"] = polygon_fill_opacity
        self.paint_props["polyline_line_color"] = mcolors.to_hex(polyline_line_color)
        self.paint_props["polyline_line_width"] = polyline_line_width
        self.paint_props["polyline_line_style"] = polyline_line_style
        self.paint_props["polyline_line_opacity"] = polyline_line_opacity
        self.paint_props["circle_line_color"] = mcolors.to_hex(circle_line_color)
        self.paint_props["circle_line_opacity"] = circle_line_opacity
        self.paint_props["circle_fill_color"] = mcolors.to_hex(circle_fill_color)
        self.paint_props["circle_fill_opacity"] = circle_fill_opacity
        self.paint_props["circle_radius"] = circle_radius
        self.paint_props["rotate"] = rotate
        self.paint_props["show_endpoints"] = show_endpoints
        if show_endpoints:
            self.paint_props["endpoint_start_color"] = mcolors.to_hex(
                endpoint_start_color
            )
            self.paint_props["endpoint_end_color"] = mcolors.to_hex(endpoint_end_color)
            self.paint_props["endpoint_radius"] = endpoint_radius
            self.paint_props["endpoint_labels"] = {"start": "Start", "end": "End"}

        # Add this layer
        self.map.runjs(
            "/js/draw_layer.js",
            "addLayer",
            arglist=[self.map_id, "active", self.paint_props, self.shape],
        )

    def _derive_legend_items(self) -> List[Dict[str, str]]:
        """Build a swatch reflecting this draw layer's shape + paint props.

        Returns an empty list when no ``legend_label`` / ``legend_title``
        is set (layer opts out of the legend by default) or when the
        layer currently has no features, so the swatch is only shown
        while there is something on the map to represent. Fills and
        borders use ``rgba(...)`` so the swatch inherits the layer's
        on-map opacity values.
        """
        label = getattr(self, "legend_label", "") or getattr(self, "legend_title", "")
        if not label:
            return []
        if len(self.gdf) == 0:
            return []
        from .layer import _css_rgba

        pp = self.paint_props
        shape = self.shape
        if shape == "polygon" or shape == "rectangle":
            fill = _css_rgba(
                pp.get("polygon_fill_color", "#888"),
                pp.get("polygon_fill_opacity", 0.5),
            )
            line = _css_rgba(
                pp.get("polygon_line_color", "#000"),
                pp.get("polygon_line_opacity", 1.0),
            )
            style = (
                f"background:{fill}; "
                f"border:{pp.get('polygon_line_width', 2)}px solid {line};"
            )
        elif shape == "polyline":
            # Horizontal strip centred in the swatch box via a
            # linear-gradient background.
            color = _css_rgba(
                pp.get("polyline_line_color", "#000"),
                pp.get("polyline_line_opacity", 1.0),
            )
            w = int(pp.get("polyline_line_width", 2) or 2)
            top = 9 - max(1, w // 2)
            bottom = top + max(2, w)
            style = (
                f"background:linear-gradient(to bottom, transparent {top}px, "
                f"{color} {top}px, {color} {bottom}px, transparent {bottom}px); "
                "border:none;"
            )
        elif shape == "circle":
            fill = _css_rgba(
                pp.get("circle_fill_color", "#888"),
                pp.get("circle_fill_opacity", 0.5),
            )
            line = _css_rgba(
                pp.get("circle_line_color", "#000"),
                pp.get("circle_line_opacity", 1.0),
            )
            style = (
                f"background:{fill}; border:2px solid {line}; "
                "border-radius:50%; width:12px; height:12px; margin:3px;"
            )
        else:
            style = (
                f"background:{pp.get('polygon_fill_color', '#888')}; "
                "border:1px solid #000;"
            )
        return [{"style": style, "label": label}]

    def set_paint_property(self, key: str, value: Any) -> None:
        """Update a paint property on this draw layer.

        Parameters
        ----------
        key : str
            Property name (e.g. ``"rotate"``).
        value : Any
            New value.
        """
        self.paint_props[key] = value
        self.map.runjs(
            "/js/draw_layer.js",
            "setPaintProperty",
            arglist=[self.map_id, key, value],
        )

    def set_mode(self, mode: str) -> None:
        """Set mode of layer. Can be active, inactive or invisible."""
        self.mode = mode
        if mode == "active":
            self.active = True
            self.visible = True
        elif mode == "inactive":
            self.active = False
            self.visible = True
        else:
            self.active = False
            self.visible = False
        self.map.runjs("/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, mode])

    def activate(self) -> None:
        """Activate the draw layer so it can be edited by the user."""
        self.visible = True
        self.active = True
        self.map.runjs(
            "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"]
        )
        owner = self._get_shared_legend_owner()
        if owner is not None:
            owner._set_shared_legend_items(self, self._derive_legend_items())

    def deactivate(self) -> None:
        """Deactivate the draw layer so it can not be edited by the user."""
        self.active = False
        self.map.runjs(
            "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "inactive"]
        )
        owner = self._get_shared_legend_owner()
        if owner is not None:
            owner._set_shared_legend_items(self, [])

    def set_visibility(self, true_or_false: bool) -> None:
        """Show or hide the draw layer on the map.

        Parameters
        ----------
        true_or_false : bool
            *True* to show, *False* to hide.
        """
        if true_or_false:
            if self.active:
                self.map.runjs(
                    "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "active"]
                )
            else:
                self.map.runjs(
                    "/js/draw_layer.js",
                    "setLayerMode",
                    arglist=[self.map_id, "inactive"],
                )
        else:
            # Make layer invisible
            self.map.runjs(
                "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, "invisible"]
            )

        # Hide-cascades don't propagate ``self.visible`` to children,
        # so explicitly register/clear this layer's shared-legend
        # entry from inside set_visibility itself.
        owner = self._get_shared_legend_owner()
        if owner is not None:
            if true_or_false:
                owner._set_shared_legend_items(self, self._derive_legend_items())
            else:
                owner._set_shared_legend_items(self, [])

    def _sync_shared_legend(self) -> None:
        """Push the current swatch (or empty) up to the shared-legend owner.

        Called on every feature mutation so the legend follows data
        existence. :meth:`deactivate` independently clears the swatch,
        and the owner's rebuild filters by child visibility, so no
        active-state gate is needed here — draw layers that never get
        an explicit ``.activate()`` call (e.g. ``self.active`` defaults
        to ``False`` in the constructor) still register correctly.
        """
        owner = self._get_shared_legend_owner()
        if owner is not None:
            owner._set_shared_legend_items(self, self._derive_legend_items())

    def set_data(self, gdf: gpd.GeoDataFrame) -> None:
        """Clear the draw layer and add data. Data must be a GeoDataFrame."""
        self.clear()
        self.add_feature(gdf)

    def add_feature(self, gdf: gpd.GeoDataFrame) -> None:
        """Add data to draw layer. Data must be a GeoDataFrame."""

        if len(gdf) == 0:
            return

        # Append to self.gdf (which doesn't have to have CRS=4326)
        if not self.gdf.empty:
            self.gdf = pd.concat(
                [self.gdf, gdf.to_crs(self.gdf.crs)], ignore_index=True
            )
        else:
            self.gdf = gdf

        for index, row in gdf.to_crs(4326).iterrows():
            # Add feature to draw layer, which has CRS=4326
            gdf2plot = gpd.GeoDataFrame(geometry=[row["geometry"]])
            # Get feature ID
            feature_id = makeid(8)
            # Set the id in self.gdf
            self.gdf.loc[index, "id"] = feature_id
            self.map.runjs(
                "/js/draw_layer.js",
                "addFeature",
                arglist=[gdf2plot, self.map_id, feature_id],
            )

        self._sync_shared_legend()

    def add_rectangle(
        self, x0: float, y0: float, lenx: float, leny: float, rotation: float
    ) -> None:
        """Add a rectangle to the draw layer.

        Parameters
        ----------
        x0 : float
            X-coordinate of the origin corner (in map CRS).
        y0 : float
            Y-coordinate of the origin corner (in map CRS).
        lenx : float
            Length along the x-direction.
        leny : float
            Length along the y-direction.
        rotation : float
            Rotation angle in degrees.
        """
        x = [x0]
        y = [y0]
        x.append(x[0] + lenx * math.cos(math.pi * rotation / 180))
        y.append(y[0] + lenx * math.sin(math.pi * rotation / 180))
        x.append(x[1] + leny * math.cos(math.pi * (rotation + 90.0) / 180))
        y.append(y[1] + leny * math.sin(math.pi * (rotation + 90.0) / 180))
        x.append(x[2] + lenx * math.cos(math.pi * (rotation + 180.0) / 180))
        y.append(y[2] + lenx * math.sin(math.pi * (rotation + 180.0) / 180))
        x.append(x0)
        y.append(y0)
        polygon_crs = Polygon(zip(x, y))
        # Transform to WGS 84
        project = pyproj.Transformer.from_crs(
            self.map.crs, pyproj.CRS(4326), always_xy=True
        ).transform
        polygon_wgs84 = transform(project, polygon_crs)
        gdf = gpd.GeoDataFrame(geometry=[polygon_wgs84], crs=4326)
        gdf["x0"] = x0
        gdf["y0"] = y0
        gdf["dx"] = lenx
        gdf["dy"] = leny
        gdf["rotation"] = rotation
        self.add_feature(gdf)

    def draw(
        self,
        fixed_distance: Optional[float] = None,
        spline: bool = False,
    ) -> None:
        """Activate drawing mode.

        Parameters
        ----------
        fixed_distance : float, optional
            If provided, draw polyline segments of exactly this length
            in kilometres. Only applicable to polyline shape.
        spline : bool, optional
            If True, draw a smooth Bézier spline through control points.
            Only applicable to polyline shape.
        """
        if self.shape == "polygon":
            self.map.runjs("/js/draw_layer.js", "drawPolygon", arglist=[self.map_id])
        elif self.shape == "polyline":
            if fixed_distance is not None:
                self.map.runjs(
                    "/js/draw_layer.js",
                    "drawPolylineFixedDistance",
                    arglist=[self.map_id, fixed_distance],
                )
            elif spline:
                self.map.runjs(
                    "/js/draw_layer.js",
                    "drawSpline",
                    arglist=[self.map_id],
                )
            else:
                self.map.runjs(
                    "/js/draw_layer.js", "drawPolyline", arglist=[self.map_id]
                )
        elif self.shape == "rectangle":
            self.map.runjs("/js/draw_layer.js", "drawRectangle", arglist=[self.map_id])

    def set_gdf(self, feature_collection: Dict[str, Any], index: int) -> None:
        """Update the internal GeoDataFrame from a JS feature collection.

        Parameters
        ----------
        feature_collection : dict
            GeoJSON FeatureCollection from the JS draw control.
        index : int
            Index of the feature that was drawn or modified.
        """
        gdf = gpd.GeoDataFrame.from_features(feature_collection, crs=4326).to_crs(
            self.map.crs
        )

        feature_id = feature_collection["features"][index]["id"]

        if index > len(self.gdf) - 1:
            # Add new row to self.gdf
            d = {"geometry": [gdf.iloc[index]["geometry"]], "id": [feature_id]}
            if self.columns:
                for col in self.columns:
                    d[col] = [self.columns[col]]
            new_row = gpd.GeoDataFrame(d).set_crs(self.map.crs)
            # Add new row to self.gdf (this means that the dataframe will get a new memory address)
            self.gdf = pd.concat([self.gdf, new_row], ignore_index=True)
        else:
            # Only change the geometry of the selected feature and copy the id
            # self.gdf.at[index, "id"] = gdf.at[index, "id"]
            self.gdf.loc[index, "id"] = feature_id
            self.gdf.loc[index, "geometry"] = gdf.loc[index, "geometry"]

        # Interactive draws / edits land here, so the shared legend
        # needs to re-sync even when the create/modify callbacks
        # don't go through ``set_data``.
        self._sync_shared_legend()

    def get_feature_index(self, feature_id: str) -> Optional[int]:
        """Get a feature's index by ID in the GeoDataFrame."""
        feature_index = None
        if len(self.gdf) > 0:
            indx = self.gdf.index[self.gdf["id"] == feature_id].tolist()
            if indx:
                feature_index = indx[0]
        if feature_index is None:
            logger.error("Could not find feature ...")
        return feature_index

    def get_feature_id(self, feature_index: int) -> Optional[str]:
        """Get a feature's ID by index in the GeoDataFrame."""
        feature_id = None
        if len(self.gdf) > 0 and len(self.gdf) >= feature_index + 1:
            feature_id = self.gdf.loc[feature_index, "id"]
        return feature_id

    def feature_drawn(
        self, feature_collection: Dict[str, Any], feature_id: str
    ) -> None:
        """Handle a newly drawn feature from the JS draw control.

        Parameters
        ----------
        feature_collection : dict
            GeoJSON FeatureCollection from the JS draw control.
        feature_id : str
            The ID assigned to the new feature.
        """
        # Feature index is always the last in the feature collection
        feature_index = len(feature_collection["features"]) - 1

        # Called after a feature has been drawn by the user
        if self.shape == "rectangle":
            # Need to make sure that the rectangle is drawn in ccw direction
            # with the lower left corner as the first point
            geom = feature_collection["features"][feature_index]["geometry"]
            geom = fix_rectangle_geometry(geom)
            feature_collection["features"][feature_index]["geometry"] = geom

        # Create geodataframe from feature collection
        self.set_gdf(feature_collection, feature_index)

        # Check if this is a rectangle. If so, we need to compute the geometry and redraw it,
        # since the polygon may have been changed.
        if self.shape == "rectangle":
            # Now compute geometry for rectangle that was just drawn
            # Not geom is in the map CRS, not necessarily 4326
            geom = self.gdf.loc[feature_index, "geometry"]
            x0, y0, dx, dy, rotation = get_rectangle_geometry(geom)
            self.gdf.loc[feature_index, "x0"] = x0
            self.gdf.loc[feature_index, "y0"] = y0
            self.gdf.loc[feature_index, "dx"] = dx
            self.gdf.loc[feature_index, "dy"] = dy
            self.gdf.loc[feature_index, "rotation"] = (
                0.0  # When drawing a rectangle, the rotation is always 0.0
            )
            # Need to set the corrected rectangle geometry, but it has to be in 4326
            # Transform to WGS 84
            project = pyproj.Transformer.from_crs(
                self.map.crs, pyproj.CRS(4326), always_xy=True
            ).transform
            geom = transform(project, geom)
            self.set_feature_geometry(feature_id, geom)

        # Check if there is a create method
        if self.create:
            # Call the create method sending the gdf with all features and the index of the new feature
            self.create(self.gdf, feature_index, feature_id)

    def feature_added(
        self, feature_collection: Dict[str, Any], feature_id: str
    ) -> None:
        """Handle a feature added programmatically."""
        index = len(feature_collection["features"]) - 1
        self.set_gdf(feature_collection, index)
        if self.add:
            feature_index = self.get_feature_index(feature_id)
            if feature_index is not None:
                self.add(self.gdf, feature_index, feature_id)

    def feature_modified(
        self, feature_collection: Dict[str, Any], feature_id: str
    ) -> None:
        """Handle a feature modified by the user."""
        index = self.get_feature_index(feature_id)
        if index is None:
            return
        self.set_gdf(feature_collection, index)

        if self.shape == "rectangle":
            # Compute x0, y0, dx, dy from the map CRS geometry
            geom = self.gdf.loc[index, "geometry"]
            x0, y0, dx, dy, _ = get_rectangle_geometry(geom)

            # Compute rotation using geodetic bearing of the first edge
            # in EPSG:4326. This avoids meridian convergence issues that
            # arise when computing atan2 on projected coordinates.
            geom_4326 = (
                gpd.GeoDataFrame.from_features(feature_collection, crs=4326)
                .iloc[index]
                .geometry
            )
            rotation = _geodetic_edge_bearing(geom_4326)

            self.gdf.loc[index, "x0"] = x0
            self.gdf.loc[index, "y0"] = y0
            self.gdf.loc[index, "dx"] = dx
            self.gdf.loc[index, "dy"] = dy
            self.gdf.loc[index, "rotation"] = rotation

        if self.modify:
            self.modify(self.gdf, index, feature_id)

    def feature_selected(
        self, feature_collection: Dict[str, Any], feature_id: str
    ) -> None:
        """Handle a feature selected by the user."""
        if self.select:
            feature_index = self.get_feature_index(feature_id)
            if feature_index is not None:
                self.select(feature_index)

    def feature_deselected(self) -> None:
        """Handle a feature deselected by the user."""
        if self.deselect:
            self.deselect()

    def activate_feature(self, feature_id_or_index: Union[int, str]) -> None:
        """Activate a feature by ID or index so it can be edited by the user."""
        if isinstance(feature_id_or_index, int):
            # It's an index
            index = feature_id_or_index
            feature_id = self.get_feature_id(index)
        else:
            feature_id = feature_id_or_index
        if self.mode != "active":
            self.mode = "active"
            self.map.runjs(
                "/js/draw_layer.js", "setLayerMode", arglist=[self.map_id, self.mode]
            )
        self.map.runjs("/js/draw_layer.js", "activateFeature", arglist=[feature_id])

    def set_feature_geometry(self, feature_id: str, geom: Any) -> None:
        """Update a feature's geometry on the map.

        Parameters
        ----------
        feature_id : str
            The feature ID.
        geom : shapely geometry or dict
            New geometry (in EPSG:4326).
        """
        if hasattr(geom, "__geo_interface__"):
            geom = geom.__geo_interface__
        # Ensure coordinates are lists, not tuples (JSON serialization)
        geom = _geometry_to_lists(geom)
        self.map.runjs(
            "/js/draw_layer.js",
            "setFeatureGeometry",
            arglist=[self.map_id, feature_id, geom],
        )

    def delete_feature(self, feature_id_or_index: Union[int, str]) -> gpd.GeoDataFrame:
        """Delete a feature by ID or index.

        Parameters
        ----------
        feature_id_or_index : int or str
            Feature index (int) or feature ID (str).

        Returns
        -------
        GeoDataFrame
            The updated GeoDataFrame after deletion.
        """
        if isinstance(feature_id_or_index, int):
            # It's an index
            index = feature_id_or_index
            feature_id = self.get_feature_id(index)
            # Remove from gdf
            self.gdf = self.gdf.drop(index)
            if len(self.gdf) > 0:
                self.gdf = self.gdf.reset_index(drop=True)
            else:
                self.gdf = gpd.GeoDataFrame()
            # Remove from map
            self.map.runjs("/js/draw_layer.js", "deleteFeature", arglist=[feature_id])
        else:
            feature_id = feature_id_or_index
            # Remove from gdf
            for index, row in self.gdf.iterrows():
                if row["id"] == feature_id:
                    self.gdf = self.gdf.drop(index)
                    if len(self.gdf) > 0:
                        self.gdf = self.gdf.reset_index(drop=True)
                    else:
                        self.gdf = gpd.GeoDataFrame()
                    break
            self.map.runjs("/js/draw_layer.js", "deleteFeature", arglist=[feature_id])
        self._sync_shared_legend()
        return self.gdf

    def delete_from_map(self) -> None:
        """Delete the draw layer from the map."""
        self.active = False
        self.map.runjs("/js/draw_layer.js", "deleteLayer", arglist=[self.map_id])
        self.gdf = gpd.GeoDataFrame()

    def clear(self) -> None:
        """Clear the draw layer."""
        for index, row in self.gdf.iterrows():
            self.map.runjs("/js/draw_layer.js", "deleteFeature", arglist=[row["id"]])
        self.gdf = gpd.GeoDataFrame()
        self._sync_shared_legend()

    def get_gdf(self, id: Optional[str] = None) -> gpd.GeoDataFrame:
        """Return the GeoDataFrame for this layer.

        Parameters
        ----------
        id : str, optional
            If specified, return only the row with that feature ID.

        Returns
        -------
        GeoDataFrame
        """
        if id:
            for index, row in self.gdf.iterrows():
                if row["id"] == id:
                    return self.gdf[index]
        else:
            return self.gdf

    def redraw(self) -> None:
        """Redraw the draw layer on the map."""
        self.map.runjs(
            "/js/draw_layer.js",
            "addLayer",
            arglist=[self.map_id, "active", self.paint_props, self.shape],
        )
        self.add_feature(self.gdf)
        self.set_mode(self.mode)
        if not self.get_visibility():
            self.set_visibility(False)


def _geodetic_edge_bearing(geom: Any) -> float:
    """Compute the rotation of a rectangle from its first edge in EPSG:4326.

    Uses ``atan2`` on the coordinate differences with a cos(lat)
    correction for longitude, giving the great-circle initial bearing.
    This matches what the user sees on a Web Mercator map: a horizontal
    edge at constant latitude gives exactly 0 rotation.

    Parameters
    ----------
    geom : shapely.geometry.Polygon
        Rectangle polygon in EPSG:4326.

    Returns
    -------
    float
        Rotation in radians (CCW from east). Zero means the first edge
        points east.
    """
    xx, yy = geom.exterior.coords.xy
    # Use lower-left (vertex 0) to upper-left (vertex 3) edge.
    # For an unrotated rectangle this edge is due north (dlon=0),
    # so atan2 gives exactly pi/2 with no cos(lat) correction needed.
    lon0, lat0 = float(xx[0]), float(yy[0])
    lon3, lat3 = float(xx[3]), float(yy[3])

    mid_lat = math.radians((lat0 + lat3) / 2)
    dx = (lon3 - lon0) * math.cos(mid_lat)
    dy = lat3 - lat0

    # atan2(dy, dx) gives angle from east; subtract pi/2 to get
    # rotation relative to north-pointing edge
    rotation = math.atan2(dy, dx) - math.pi / 2

    # Snap small angles to zero
    if abs(rotation) < 1e-6:
        rotation = 0.0

    return rotation


def get_rectangle_geometry(geom: Any) -> Tuple[float, float, float, float, float]:
    """Extract origin, dimensions, and rotation from a rectangle polygon.

    Parameters
    ----------
    geom : shapely.geometry.Polygon
        Rectangle polygon geometry.

    Returns
    -------
    tuple of float
        ``(x0, y0, dx, dy, rotation)`` where rotation is in radians.
    """
    xx, yy = geom.exterior.coords.xy
    x0 = float(xx[0])
    y0 = float(yy[0])
    dx = math.sqrt(float(xx[1] - xx[0]) ** 2 + float(yy[1] - yy[0]) ** 2)
    dy = math.sqrt(float(xx[2] - xx[1]) ** 2 + float(yy[2] - yy[1]) ** 2)
    rotation = float(math.atan2(yy[1] - yy[0], xx[1] - xx[0]))
    if abs(rotation * 180 / math.pi) < 0.1:
        rotation = 0.0
    return x0, y0, dx, dy, rotation


def fix_rectangle_geometry(geom: Dict[str, Any]) -> Dict[str, Any]:
    """Normalise a rectangle to CCW winding with lower-left as first vertex.

    Parameters
    ----------
    geom : dict
        GeoJSON geometry dict with ``type`` and ``coordinates``.

    Returns
    -------
    dict
        Normalised GeoJSON geometry dict.
    """
    # Check if the geometry is a polygon
    # Check if this ccw
    if not shapely.is_ccw(shapely.LineString(geom["coordinates"][0])):
        # Reverse the order of the coordinates
        geom["coordinates"][0] = geom["coordinates"][0][::-1]
    coords = geom["coordinates"][0]
    # Remove the last point which is the same as the first
    coords = coords[0:-1]
    # Get lower left corner by taking minimum x and y values
    min_x = min([x for x, y in coords])
    min_y = min([y for x, y in coords])
    # Now find the index of the point closest to the lower left corner
    dst = [(x - min_x) ** 2 + (y - min_y) ** 2 for x, y in coords]
    index = dst.index(min(dst))
    new_first_point = coords[
        index
    ]  # Assuming you want the third point as the new first point
    new_coords = [new_first_point] + coords[index + 1 :] + coords[0:index]
    new_coords.append(new_coords[0])
    # Create a new polygon with the updated coordinates
    new_polygon = Polygon(new_coords)
    # Update the geometry
    geom = new_polygon.__geo_interface__
    return geom


def makeid(length: int) -> str:
    """Generate a random alphanumeric string of the given length.

    Parameters
    ----------
    length : int
        Number of characters.

    Returns
    -------
    str
    """
    characters = string.ascii_letters + string.digits
    return "".join(random.choices(characters, k=length))


def _geometry_to_lists(geom: Dict[str, Any]) -> Dict[str, Any]:
    """Convert a GeoJSON geometry dict so all coordinate tuples are lists.

    Shapely's ``__geo_interface__`` returns tuples, but ``json.dumps``
    in ``runjs`` replaces double quotes with single quotes — tuples
    serialise as ``(x, y)`` which is invalid JSON.  Converting to lists
    ensures correct ``[x, y]`` output.
    """

    def _convert(obj):
        if isinstance(obj, (list, tuple)):
            if obj and isinstance(obj[0], (list, tuple, float, int)):
                return [_convert(item) for item in obj]
            return list(obj)
        return obj

    geom = dict(geom)
    if "coordinates" in geom:
        geom["coordinates"] = _convert(geom["coordinates"])
    return geom
