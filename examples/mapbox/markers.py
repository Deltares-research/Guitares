import shapely
import geopandas as gpd
import pandas as pd

from mpbox import mpbox

def select(*args):
    mpbox.map.fly_to(4.5, 52.0, 8)

def add_marker_layer():

    layer = mpbox.map.layer["main"]
    marker_layer = layer.add_geojson_layer("marker_layer",
                                           type="marker_selector",
                                           circle_radius=15,
                                           fill_color="orange")

    # Create GeoDataFrame with two markers
    point = shapely.geometry.Point(4.359, 52.011)
    d = {"name": "Delft", "long_name": None, "geometry": point}
    mpbox.markers = pd.concat([mpbox.markers, gpd.GeoDataFrame([d], crs=4326)], axis=0, ignore_index=True)

    point = shapely.geometry.Point(4.5074, 51.9307)
    d = {"name": "Rotterdam", "long_name": None, "geometry": point}
    mpbox.markers = pd.concat([mpbox.markers, gpd.GeoDataFrame([d], crs=4326)], axis=0, ignore_index=True)

    # Add gdf to layer
    marker_layer.set_data(mpbox.markers)

def add_marker(*args):
    mpbox.map.click_point(point_clicked)

def point_clicked(coords):
    point = shapely.geometry.Point(coords["lng"], coords["lat"])
    d = {"name": "Where the heck am I ?!", "long_name": None, "geometry": point}
    # Merge existing and new gdf
    mpbox.markers = pd.concat([mpbox.markers, gpd.GeoDataFrame([d], crs=4326)], axis=0, ignore_index=True)
    mpbox.map.layer["main"].layer["marker_layer"].set_data(mpbox.markers)

def update():
    pass
