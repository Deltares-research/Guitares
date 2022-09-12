from visualdelta import visualdelta
import pandas as pd
import numpy as np
import os
# from PIL import Image
# import matplotlib
# from matplotlib import cm
# # from osgeo import gdal
# import rasterio
# import rasterio.features
# from rasterio.warp import calculate_default_transform, reproject, Resampling, transform_bounds
# from rasterio import MemoryFile


def add_option():

    # Update all GUI elements
    visualdelta.gui.update()

def change_scenario():
    visualdelta.ssp = visualdelta.gui.getvar("visualdelta", "ssp")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_impact():
    visualdelta.impact = visualdelta.gui.getvar("visualdelta", "impact")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_exposure():
    visualdelta.exposure = visualdelta.gui.getvar("visualdelta", "exposure")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_year():
    visualdelta.year = visualdelta.gui.getvar("visualdelta", "year")
    # First calculate SLR (and update GUI)
    calculate_slr()
    # Now update flood map
    update_flood_map()

def change_year_slider():
    # This method is called while the slider is being moved
    visualdelta.year = visualdelta.gui.getvar("visualdelta", "year")
    calculate_slr()

def calculate_slr():
    csv_file = os.path.join(visualdelta.main_path, "slr", 'SLR_{}.csv'.format(visualdelta.ssp))
    slr_ts = pd.read_csv(csv_file, index_col=0, header=0)
    slr_val = np.interp(visualdelta.year, slr_ts.index, slr_ts['0.5'])
    slr_low = np.interp(visualdelta.year, slr_ts.index, slr_ts['0.17'])
    slr_high = np.interp(visualdelta.year, slr_ts.index, slr_ts['0.83'])
    visualdelta.slr = round(slr_val, 2)
    visualdelta.gui.setvar("visualdelta", "slr_string", str(visualdelta.slr) + " m")
    # visualdelta.gui.setvar("visualdelta", "slr_string", "{} m ({} - {} m)".format(round(slr_val, 2),
    #                                                                               round(slr_low, 2),
    #                                                                               round(slr_high, 2)))

    # Update all GUI elements
    visualdelta.gui.update()

def update_flood_map():

    print("Updating flood map ...")

    image_path = r"d:\temp\van_gundula"

    if visualdelta.slr < 0.2:
        image_file = "flood_withprot_slr=0.00m_rp=0100.tif"
    elif visualdelta.slr < 0.5:
        image_file = "flood_withprot_slr=0.50m_rp=0100.tif"
    else:
        image_file = "flood_withprot_slr=1.00m_rp=0100.tif"

    image_file = os.path.join(image_path, image_file)

    layer_name = "flood_map_layer"
    layer_group_name = "flood_map_layer_group"

    # Add layer group
    visualdelta.gui.map_widget["main_map"].add_layer_group(layer_group_name)

    # Remove old layer from layer group
    visualdelta.gui.map_widget["main_map"].remove_layer(layer_name,
                                                        layer_group_name)

    # And now add the new image layer to the layer group
    visualdelta.gui.map_widget["main_map"].add_image_layer(image_file,
                                                           layer_name=layer_name,
                                                           layer_group_name=layer_group_name)


#     dataset = rasterio.open(image_file)
#
#     src_crs = 'EPSG:4326'
#     dst_crs = 'EPSG:3857'
#
#     with rasterio.open(image_file) as src:
#         transform, width, height = calculate_default_transform(
#             src.crs, dst_crs, src.width, src.height, *src.bounds)
#         kwargs = src.meta.copy()
#         kwargs.update({
#             'crs': dst_crs,
#             'transform': transform,
#             'width': width,
#             'height': height
#         })
#         bnds = src.bounds
#
#         mem_file = MemoryFile()
#         with mem_file.open(**kwargs) as dst:
#             for i in range(1, src.count + 1):
#                 reproject(
#                     source=rasterio.band(src, i),
#                     destination=rasterio.band(dst, i),
#                     src_transform=src.transform,
#                     src_crs=src.crs,
#                     dst_transform=transform,
#                     dst_crs=dst_crs,
#                     resampling=Resampling.nearest)
#
#             band1 = dst.read(1)
#
#     new_bounds = transform_bounds(dst_crs, src_crs,
#                                   dst.bounds[0],
#                                   dst.bounds[1],
#                                   dst.bounds[2],
#                                   dst.bounds[3])
#     isn = np.where(band1 < 0.001)
#     band1[isn] = np.nan
#
#     band1 = np.flipud(band1)
#     cmin = np.nanmin(band1)
#     cmax = np.nanmax(band1)
#
#     norm = matplotlib.colors.Normalize(vmin=cmin, vmax=cmax)
#     vnorm = norm(band1)
#
#     im = Image.fromarray(np.uint8(cm.gist_earth(vnorm) * 255))
#
#     overlay_file = "overlay.png"
#     im.save(os.path.join(server_path, overlay_file))
#
# #    extent = [x[0], y[0], x[-1], y[-1]]
#
#     bounds = [[new_bounds[0], new_bounds[2]], [new_bounds[3], new_bounds[1]]]
#
# #    mpbox.gui.map_widget["main_map"].remove_layer("flood_map_layer", "flood_map_layer_group")
