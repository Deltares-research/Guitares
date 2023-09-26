import os

import geojson

from .layer import Layer
from geopandas import GeoDataFrame
import matplotlib.colors as mcolors

class CycloneTrackLayer(Layer):
    def __init__(self, mapbox, id, map_id, **kwargs):
        super().__init__(mapbox, id, map_id, **kwargs)
        pass

    def set_data(self,
                 data):

        # Make sure this is not an empty GeoDataFrame
        if isinstance(data, GeoDataFrame):
            # Data is GeoDataFrame
            if len(data) == 0:
                return
        else:
            print("Data is not a GeoDataFrame")
            return    

        # Need to add the track to the GeoDataFrame
        # Loop through geometries in GeoDataFrame and make LineString of the points
        # Add this LineString to the GeoDataFrame
        points = []
        for i, row in data.iterrows():
            # Get the point
            points.append(row["geometry"])
            # Add icon and html to popup
            time = row['datetime']
            lon = row['geometry'].x
            lat = row['geometry'].y
            vmax = row['vmax']
            pc = row['pc']
            if vmax<64.0:
                cat = "TS"
                icon = "./icons/tropical_storm_icon_24x48.png"
            elif vmax<83.0:
                cat = "1"
                icon = "./icons/category_1_hurricane_icon_24x48.png"
            elif vmax<96.0:    
                cat = "2"
                icon = "./icons/category_2_hurricane_icon_24x48.png"
            elif vmax<113.0:    
                cat = "3"
                icon = "./icons/category_3_hurricane_icon_24x48.png"
            elif vmax<137.0:    
                cat = "4"
                icon = "./icons/category_4_hurricane_icon_24x48.png"
            else:    
                cat = "5"
                icon = "./icons/category_5_hurricane_icon_24x48.png"
            row["icon_url"] = icon
            # Make html (&#9; is tab)
            html = 'Time: &#9;' + timestr + '<br />' + \
                   'Category: &#9;' + cat + ' &#9;' + '<br />' + \
                   'Latitude: &#9;' + latstr + ' &#9;' + '<br />' + \
                   'Longitude: &#9;' + lonstr + ' &#9;' + '<br />' + \
                   'Vmax: &#9;' + vmaxstr + ' knots &#9;' + '<br />' + \
                   'Pressure: &#9;' + pcstr + ' mbar &#9;' + '<br />'
            row["hover_html"] = html

        # Create LineString
        line = geojson.LineString(points)
        # Add LineString to GeoDataFrame
        data = data.append({"geometry": line}, ignore_index=True)

        # This is a composite layer with a line and icons

        # First add the line layer
        id = self.map_id + ".track_line"
        self.mapbox.runjs("./js/geojson_layer_line.js", "addLayer", arglist=[id,
                                                                             data.to_crs(4326),
                                                                             self.line_color,
                                                                             self.line_width,
                                                                             self.line_opacity,
                                                                             self.fill_color,
                                                                             self.fill_opacity,
                                                                             0])

        # First add the line layer
        id = self.map_id + ".track_points"
        self.mapbox.runjs("./js/marker_layer.js", "addLayer", arglist=[self.map_id,
                                                                       data.to_crs(4326),
                                                                       self.line_color,
                                                                       self.line_width,
                                                                       self.line_opacity,
                                                                       self.fill_color,
                                                                       self.fill_opacity,
                                                                       self.circle_radius])

    def redraw(self):
        if isinstance(self.data, GeoDataFrame):
            self.set_data(self.data)

    def activate(self):
        self.mapbox.runjs("./js/geojson_layer_line.js", "setPaintProperties", arglist=[self.map_id,
                                                                                       self.line_color,
                                                                                       self.line_width,
                                                                                       self.line_opacity,
                                                                                       self.fill_color,
                                                                                       self.fill_opacity,
                                                                                       self.circle_radius])
  
    def deactivate(self):
        self.mapbox.runjs("./js/geojson_layer_line.js", "setPaintProperties", arglist=[self.map_id,
                                                                                       self.line_color_inactive,
                                                                                       self.line_width_inactive,
                                                                                       self.line_opacity_inactive,
                                                                                       self.fill_color_inactive,
                                                                                       self.fill_opacity_inactive,
                                                                                       self.circle_radius_inactive])

    def set_visibility(self, true_or_false):
        # This is a composite layer. set_visibility overrides method in Layer class
        if true_or_false:
            self.mapbox.runjs(self.main_js, "showLayer", arglist=[self.map_id + ".track_line", self.side])
            self.mapbox.runjs(self.main_js, "showLayer", arglist=[self.map_id + ".track_points", self.side])
        else:
            self.mapbox.runjs(self.main_js, "hideLayer", arglist=[self.map_id + ".track_line", self.side])
            self.mapbox.runjs(self.main_js, "hideLayer", arglist=[self.map_id + ".track_points", self.side])

