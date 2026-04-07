"""Cyclone track layer combining a line track with category-coloured marker icons.

Renders a hurricane/cyclone track as a composite of a ``LineLayer``
(the track path) and a ``MarkerLayer`` (category icons with hover popups).
"""

import copy
import datetime
from typing import Any

import shapely
from geopandas import GeoDataFrame

from .layer import Layer


class CycloneTrackLayer(Layer):
    """Composite layer showing a cyclone track line with category icons.

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

    def set_data(self, data: GeoDataFrame) -> None:
        """Set cyclone track data and render on the map.

        Parameters
        ----------
        data : GeoDataFrame
            Point features with columns ``datetime``, ``vmax``, ``pc``,
            and point geometries along the track.
        """
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            if len(data) == 0:
                return
        else:
            print("Data is not a GeoDataFrame")
            return

        # We need to make a copy, because we will add columns for icon_url and hover_html
        self.data = copy.deepcopy(data)

        # Need to add the track to the GeoDataFrame
        points = []
        # Add columns for icon_url and html
        self.data["icon_url"] = None
        self.data["hover_html"] = None
        for i, row in data.iterrows():
            # Get the point (used to make LineString for new gdf)
            points.append(row["geometry"])
            # Add icon and html to popup
            timestr = row["datetime"]
            t = datetime.datetime.strptime(timestr, "%Y%m%d %H%M%S")
            timestr = f"{t.strftime('%Y-%m-%d %H:%M:%S')} UTC"
            lon = row["geometry"].x
            lat = row["geometry"].y
            vmax = row["vmax"]
            pc = row["pc"]
            if vmax < 64.0:
                cat = "TS"
                icon = "/icons/tropical_storm_icon_24x48.png"
            elif vmax < 83.0:
                cat = "1"
                icon = "/icons/category_1_hurricane_icon_24x48.png"
            elif vmax < 96.0:
                cat = "2"
                icon = "/icons/category_2_hurricane_icon_24x48.png"
            elif vmax < 113.0:
                cat = "3"
                icon = "/icons/category_3_hurricane_icon_24x48.png"
            elif vmax < 137.0:
                cat = "4"
                icon = "/icons/category_4_hurricane_icon_24x48.png"
            else:
                cat = "5"
                icon = "/icons/category_5_hurricane_icon_24x48.png"
            # Make html (&#9; is tab)
            if lat > 0.0:
                latstr = f"{abs(lat):.2f} N"
            else:
                latstr = f"{abs(lat):.2f} S"
            if lon > 0.0 and lon < 180.0:
                lonstr = f"{abs(lon):.2f} E"
            elif lon > 180.0:
                lonstr = f"{abs(lon - 360.0):.2f} W"
            else:
                lonstr = f"{abs(lon):.2f} W"
            vmaxstr = f"{vmax:.1f}"
            if pc > 0.0:
                pcstr = f"{pc:.0f} mbar"
            else:
                pcstr = "N/A"

            html = (
                f"Time: &#9;{timestr}<br />"
                f"Category: &#9;{cat} &#9;<br />"
                f"Latitude: &#9;{latstr} &#9;<br />"
                f"Longitude: &#9;{lonstr} &#9;<br />"
                f"Vmax: &#9;{vmaxstr} knots &#9;<br />"
                f"Pressure: &#9;{pcstr} &#9;<br />"
            )

            # Add icon and html to row
            self.data.at[i, "icon_size"] = self.icon_size
            self.data.at[i, "icon_url"] = icon
            self.data.at[i, "hover_html"] = html

        # Create shapely LineString with geometries in points
        line = shapely.geometry.LineString(points)
        # Now make new gdf with LineString
        track_gdf = GeoDataFrame([{"geometry": line}]).set_crs(4326)

        # This is a composite layer with a line and icons

        # First add the line layer
        line_id = f"{self.map_id}.track_line"
        pp = self.get_paint_props()
        self.map.runjs(
            "/js/line_layer.js",
            "addLayer",
            arglist=[line_id, track_gdf, pp, {}],
        )

        if self.show_icons:
            points_id = f"{self.map_id}.track_points"
            self.map.runjs(
                "/js/marker_layer.js",
                "addLayer",
                arglist=[points_id, self.data.to_crs(4326)],
            )

    def redraw(self) -> None:
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)

    # TODO: Implement activate and deactivate

    def set_visibility(self, true_or_false: bool) -> None:
        """Show or hide the composite track layer.

        Parameters
        ----------
        true_or_false : bool
            *True* to show, *False* to hide.
        """
        if true_or_false:
            self.map.runjs(
                self.main_js,
                "showLayer",
                arglist=[f"{self.map_id}.track_line", self.side],
            )
            self.map.runjs(
                self.main_js,
                "showLayer",
                arglist=[f"{self.map_id}.track_points", self.side],
            )
        else:
            self.map.runjs(
                self.main_js,
                "hideLayer",
                arglist=[f"{self.map_id}.track_line", self.side],
            )
            self.map.runjs(
                self.main_js,
                "hideLayer",
                arglist=[f"{self.map_id}.track_points", self.side],
            )

    def delete_from_map(self) -> None:
        """Remove the composite track layer from the map."""
        self.map.runjs(
            self.main_js,
            "removeLayer",
            arglist=[f"{self.map_id}.track_line", self.side],
        )
        self.map.runjs(
            self.main_js,
            "removeLayer",
            arglist=[f"{self.map_id}.track_points", self.side],
        )

    def clear(self) -> None:
        """Clear the track data and remove from the map."""
        self.data = None
        self.delete_from_map()
