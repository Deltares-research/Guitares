"""Marker layer for displaying icon-based point features on the map.

Supports custom icons per feature, hover popups, and click popups
(including embedded HTML and iframes).
"""

from typing import Any, Union

from geopandas import GeoDataFrame
from pyogrio import read_dataframe

from .layer import Layer


class MarkerLayer(Layer):
    """Marker layer displaying icon-based point features.

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

    def set_data(self, data: Union[GeoDataFrame, str]) -> None:
        """Set data for the marker layer and render on the map.

        Parameters
        ----------
        data : GeoDataFrame or str
            Point geometries, or a file path to read via pyogrio.
        """
        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                return
            if data.crs != 4326:
                data = data.to_crs(4326)
        else:
            # Read geodataframe from shape file
            data = read_dataframe(data)

        self.data = data

        # Over-ride properties in rows
        if self.icon_file:
            # All markers get the same icon
            data["icon_url"] = self.icon_file
        if self.click_popup_width:
            data["click_popup_width"] = self.click_popup_width
        data["icon_size"] = self.icon_size

        # Add relative path to icon_file
        # Check if there is a column in the dataframe data called "icon_file"
        if "icon_url" in data.columns:
            # Loop through all rows and add the relative path "/icons/" to the icon_file
            for i, row in data.iterrows():
                if not row["icon_url"].startswith("http"):
                    data.at[i, "icon_url"] = f"/icons/{row['icon_url']}"
        else:
            # Use default icon for all markers
            data["icon_url"] = f"/icons/map-marker-icon-20px-{self.marker_color}.png"

        if self.click_popup_width:
            wdtstr = f"{self.click_popup_width}px"
        else:
            wdtstr = "100%"
        if self.click_popup_height:
            hgtstr = f"{self.click_popup_height}px"
        else:
            hgtstr = "100%"

        # Check if there is a column in the geodataframe called "click_html"
        if self.click_property:
            # Add click_html column to data
            data["click_html"] = ""
            # Loop through all rows
            for i, row in data.iterrows():
                if row[self.click_property].endswith(".html") and not row[
                    self.click_property
                ].startswith("http"):
                    # Must be a local html file
                    data.at[i, "click_html"] = (
                        f'<div><iframe width="{wdtstr}" height="{hgtstr}" '
                        f'src="./overlays/{row[self.click_property]}"></iframe></div>'
                    )
                elif row[self.click_property].startswith("http"):
                    # External url (may fail due to X-Frame-Options)
                    data.at[i, "click_html"] = (
                        f'<div><iframe width="{wdtstr}" height="{hgtstr}" '
                        f'src="{row[self.click_property]}"></iframe></div>'
                    )
                else:
                    # Get click_html from click_property
                    data.at[i, "click_html"] = row[self.click_property]

        # Do the same for hover_property and hover_html
        if self.hover_property:
            data["hover_html"] = ""
            for i, row in data.iterrows():
                if row[self.hover_property].endswith(".html") and not row[
                    self.hover_property
                ].startswith("http"):
                    data.at[i, "hover_html"] = (
                        f'<div><iframe src="./overlays/{row[self.hover_property]}">'
                        f"</iframe></div>"
                    )
                elif row[self.hover_property].startswith("http"):
                    data.at[i, "hover_html"] = (
                        f'<div><iframe src="{row[self.hover_property]}"></iframe></div>'
                    )
                else:
                    data.at[i, "hover_html"] = row[self.hover_property]

        # Add new layer
        self.map.runjs(
            "/js/marker_layer.js",
            "addLayer",
            arglist=[self.map_id, data],
        )

    # TODO: Implement activate and deactivate

    def redraw(self) -> None:
        """Redraw the layer (e.g. after a style change)."""
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)
