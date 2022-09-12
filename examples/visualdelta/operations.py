from visualdelta import visualdelta
import pandas as pd
import numpy as np
import os
from PIL import Image
from matplotlib import cm
# from osgeo import gdal


def add_option():

    # Update all GUI elements
    visualdelta.gui.update()

def calculate_slr():
    ssp = visualdelta.gui.getvar("visualdelta", "ssp")
    year = visualdelta.gui.getvar("visualdelta", "year")
    slr_ts = pd.read_csv('slr\\SLR_{}.csv'.format(ssp), index_col=0, header=0)
    slr_val = np.interp(year,slr_ts.index, slr_ts['0.5'])
    slr_low = np.interp(year,slr_ts.index, slr_ts['0.17'])
    slr_high = np.interp(year, slr_ts.index, slr_ts['0.83'])
    # print('Median SLR for SSP{} in year {} is {:.2f} (likely range {:.2f} - {:.2f})'.format(ssp,year,slr_val, slr_low, slr_high))
    visualdelta.gui.setvar("visualdelta", "year", year)
    visualdelta.gui.setvar("visualdelta", "slr", round(slr_val,2))
    visualdelta.gui.setvar("visualdelta", "slr_string", "{} m ({} - {} m)".format(round(slr_val,2),round(slr_low,2),round(slr_high,2)))

    # Update all GUI elements
    visualdelta.gui.update()
    
def show_geotiff():
    image_path = r"c:\Users\winter_ga\OneDrive - Stichting Deltares\Project_data\Visual Delta\floodmaps"

    server_path = visualdelta.gui.map_widget["main_map"].server_path

#    visualdelta.gui.map_widget["main_map"].show_image_layer()
    dataset = rasterio.open(image_file)
    band1 = dataset.read(1)
    isn = np.where(band1 < 0.001)
    band1[isn] = np.nan
    cmin = np.nanmin(band1)
    cmax = np.nanmax(band1)

    norm = matplotlib.colors.Normalize(vmin=cmin, vmax=cmax)
    v = norm(band1)

    im = Image.fromarray(np.uint8(cm.gist_earth(v) * 255))
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
    visualdelta.gui.map_widget["main_map"].add_layer_group("flood_map_layer_group")

    bounds = [[dataset.bounds[0], dataset.bounds[2]], [dataset.bounds[1], dataset.bounds[3]]]

#    visualdelta.gui.map_widget["main_map"].remove_layer("flood_map_layer", "flood_map_layer_group")

    visualdelta.gui.map_widget["main_map"].add_image_layer(image_file, "flood_map_layer", "flood_map_layer_group", bounds)