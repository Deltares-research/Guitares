import rasterio
import rasterio.features
from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
from rasterio import MemoryFile

import numpy as np
import matplotlib
import os
from PIL import Image
from matplotlib import cm

from mapbox_example import mpbox

def draw_polygon():
    mpbox.gui.olmap["main_map"].draw_polygon("layer1",
                                       create=add_polygon,
                                       modify=modify_polygon)

def add_polygon(polid, coords):
    print("Polygon added")
    print(polid)
    print(coords)

def modify_polygon(polid, coords):
    print("Polygon modified")
    print(polid)
    print(coords)

def draw_polyline():
    mpbox.gui.olmap["main_map"].draw_polyline("layer1",
                                       create=add_polyline,
                                       modify=modify_polyline)

def add_polyline(polid, coords):
    print("Polyline added")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))

def modify_polyline(polid, coords):
    print("Polyline modified")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))

def draw_rectangle():
    mpbox.gui.mapbox["main_map"].draw_rectangle("layer1",
                                             create=add_rectangle,
                                             modify=modify_rectangle)

def add_rectangle(polid, coords):
    print("Rectangle added")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))

def modify_rectangle(polid, coords):
    print("Rectangle modified")
    print("ID= " + str(polid))
    print("Coords = " + str(coords))

def import_geotiff():
    image_file = "d:/CFRSS/database/charleston/output/results/current_test_set_frequent_doNothing/Flood_frequency.tif"
#    image_file = "./Flood_frequency.tif"
#    image_file = "./logo_blue.png"
#    image_file = "d:/cosmos/webviewers/nopp_event_viewer/img/logos/logo_blue.png"
    layer_name = "geotiff"
#    mpbox.map.add_image_overlay(layer_name, image_file)
#    mpbox.map.add_layer_group("layer_group_1")
#    mpbox.gui.map_widget["main_map"].add_image_overlay(layer_name, image_file)
    mpbox.gui.map_widget["main_map"].add_layer_group("layer_group_1")
    mpbox.gui.map_widget["main_map"].add_layer_group("layer_group_2", parent="layer_group_1")
    image_file = "logo_blue.png"
    mpbox.gui.map_widget["main_map"].add_image_layer(image_file, "image_layer", "layer_group_2")

def delete_layer():
    print("Deleting layer")
    mpbox.gui.map_widget["main_map"].remove_layer("flood_map_layer", "flood_map_layer_group")

def show_geotiff():
    image_file = "d:\\temp\\van_gundula\\flood_withprot_slr=1.00m_rp=0100.tif"

    server_path = mpbox.gui.map_widget["main_map"].server_path

#    mpbox.gui.map_widget["main_map"].show_image_layer()
    dataset = rasterio.open(image_file)

    src_crs = 'EPSG:4326'
    dst_crs = 'EPSG:3857'

    with rasterio.open(image_file) as src:
        transform, width, height = calculate_default_transform(
            src.crs, dst_crs, src.width, src.height, *src.bounds)
        kwargs = src.meta.copy()
        kwargs.update({
            'crs': dst_crs,
            'transform': transform,
            'width': width,
            'height': height
        })
        bnds = src.bounds
#         dst_shape = (width, height)
#         dst = np.zeros(dst_shape, src.dtypes[0])
#
#         for i in range(1, src.count + 1):
#             reproject(
#                 rasterio.band(src, i),
# #                destination=rasterio.band(dst, i),
#                 dst,
#                 src_transform=src.transform,
#                 src_crs=src.crs,
#                 dst_transform=transform,
#                 dst_crs=dst_crs,
#                 resampling=Resampling.nearest)

        # calculate_default_transform(src_crs, dst_crs, width, height, left=None, bottom=None, right=None,
        #                                           top=None, gcps=None, rpcs=None, resolution=None, dst_width=None,
        #                                           dst_height=None, **kwargs)
        mem_file = MemoryFile()
        with mem_file.open(**kwargs) as dst:
            for i in range(1, src.count + 1):
                reproject(
                    source=rasterio.band(src, i),
                    destination=rasterio.band(dst, i),
                    src_transform=src.transform,
                    src_crs=src.crs,
                    dst_transform=transform,
                    dst_crs=dst_crs,
                    resampling=Resampling.nearest)

            band1 = dst.read(1)

    new_bounds = transform_bounds(dst_crs, src_crs,
                                  dst.bounds[0],
                                  dst.bounds[1],
                                  dst.bounds[2],
                                  dst.bounds[3])
    isn = np.where(band1 < 0.001)
    band1[isn] = np.nan

    band1 = np.flipud(band1)
    cmin = np.nanmin(band1)
    cmax = np.nanmax(band1)

    norm = matplotlib.colors.Normalize(vmin=cmin, vmax=cmax)
    vnorm = norm(band1)

    im = Image.fromarray(np.uint8(cm.gist_earth(vnorm) * 255))
    # cmin = np.nanmin(band1)
    # cmax = -cmin
    #
    # ls = LightSource(azdeg=315, altdeg=30)
    #
    # cmap = settings.color_map_earth
    # #        cmap = plt.get_cmap('gist_earth')
    # dx = (x[1] - x[0]) / 2
    # dy = (y[1] - y[0]) / 2
    # rgb = ls.shade(np.flipud(z), cmap,
    #                vmin=cmin,
    #                vmax=cmax,
    #                dx=dx * 50000,
    #                dy=dy * 50000,
    #                vert_exag=10.0,
    #                blend_mode="soft")
    # rgb = rgb[:, :, 0:3] * 255
    # rgb = rgb.astype(np.uint8)
    # alpha = Image.fromarray(rgb, "RGB")

    # Remove old overlay
#    if os.path.exists(os.path.join("d:/projects/python/openlayers_v03", settings.image_file)):
#        os.remove(os.path.join("d:/projects/python/openlayers_v03", settings.image_file))

#    rnd = int(1000000 * random.uniform(0, 1))

    image_file = "overlay.png"
    im.save(os.path.join(server_path, image_file))

#    extent = [x[0], y[0], x[-1], y[-1]]
    mpbox.gui.map_widget["main_map"].add_layer_group("flood_map_layer_group")

    bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]

#    mpbox.gui.map_widget["main_map"].remove_layer("flood_map_layer", "flood_map_layer_group")

    mpbox.gui.map_widget["main_map"].add_image_layer(image_file, "flood_map_layer", "flood_map_layer_group", bounds)
