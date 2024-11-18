from .layer import Layer
from geopandas import GeoDataFrame
from pyogrio import read_dataframe

class MarkerLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self, data):
        """Set data for layer"""
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
            # Loop through all rows and add the relative path "./icons/" to the icon_file
            for i, row in data.iterrows():
                if not row["icon_url"].startswith("http"):
                    data.at[i, "icon_url"] = "./icons/" + row["icon_url"]
        else:
            # Use default icon for all markers
            data["icon_url"] = "./icons/mapbox-marker-icon-20px-" + self.marker_color + ".png"

        if self.click_popup_width:
            wdtstr = str(self.click_popup_width) + "px"
        else:
            wdtstr = "100%"
        if self.click_popup_height:
            hgtstr = str(self.click_popup_height) + "px"
        else:
            hgtstr = "100%"
                
        # Check if there is a column in the geodataframe called "click_html"
        if self.click_property:
            # Add click_html column to data
            data["click_html"] = ""
            # Loop through all rows
            for i, row in data.iterrows():
                # Loop through all rows and check if click_html ends with .html and does not start with http
                # If so, replace with relative path in server folder
                if row[self.click_property].endswith(".html") and not row[self.click_property].startswith("http"):
                    # Must be a local html file
                    data.at[i, "click_html"] = '<div><iframe width="' + wdtstr + '" height="' + hgtstr + '" src="' + './overlays/' + row[self.click_property] + '"></iframe></div>'
                elif row[self.click_property].startswith("http"):
                    # Must be an external url (this often does not work and results in an error: Refused to display in a frame because it set 'X-Frame-Options' to 'sameorigin)
                    data.at[i, "click_html"] = '<div><iframe width="' + wdtstr + '" height="' + hgtstr + '" src="' + row[self.click_property] + '"></iframe></div>'
                else:
                    # Get click_html from click_property
                    data.at[i, "click_html"] = row[self.click_property]    

        # Do the same for hover_property and hover_html
        if self.hover_property:
            data["hover_html"] = ""
            for i, row in data.iterrows():
                if row[self.hover_property].endswith(".html") and not row[self.hover_property].startswith("http"):
                    data.at[i, "hover_html"] = '<div><iframe src="' + './overlays/' + row[self.hover_property] + '"></iframe></div>'
                elif row[self.hover_property].startswith("http"):
                    data.at[i, "hover_html"] = '<div><iframe src="' + row[self.hover_property] + '"></iframe></div>'
                else:
                    data.at[i, "hover_html"] = row[self.hover_property]
         
        # Add new layer
        self.mapbox.runjs(
            "./js/marker_layer.js",
            "addLayer",
            arglist=[
                self.map_id,
                data
            ],
        )
        pass

    # TODO: Implement activate and deactivate

    # 
    # def activate(self):
    #     self.show()
    #     self.mapbox.runjs(
    #         "./js/geojson_layer_circle.js",
    #         "setPaintProperties",
    #         arglist=[
    #             self.map_id,
    #             self.line_color,
    #             self.line_width,
    #             self.line_opacity,
    #             self.fill_color,
    #             self.fill_opacity,
    #             self.circle_radius,
    #         ],
    #     )

    # def deactivate(self):
    #     self.mapbox.runjs(
    #         "./js/geojson_layer_circle.js",
    #         "setPaintProperties",
    #         arglist=[
    #             self.map_id,
    #             self.line_color_inactive,
    #             self.line_width_inactive,
    #             self.line_opacity_inactive,
    #             self.fill_color_inactive,
    #             self.fill_opacity_inactive,
    #             self.circle_radius_inactive,
    #         ],
    #     )

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)
        if not self.get_visibility():
            self.set_visibility(False)
