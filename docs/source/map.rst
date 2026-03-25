The Map Widget
==============

Guitares includes an interactive web-based map widget powered by either **MapLibre GL**
(open-source, recommended) or **Mapbox GL** (requires an API token).
The map is embedded in the Qt window via a ``QWebEngineView`` and communicates with Python
through a bidirectional bridge.

Adding the map widget
---------------------

Add the map to your YAML config like any other element:

.. code-block:: yaml

   - style: map
     id: map
     position: {x: 10, y: 180, width: -10, height: -10}
     module: map_callbacks
     map_style: osm
     map_lat: 0.0
     map_lon: 0.0
     map_zoom: 2

Map element keys
^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **id**
     - str
     -
     - Unique ID — required to access the map object later
   * - map_style
     - str
     - ``"osm"``
     - Initial basemap style (see basemap styles below)
   * - map_lat
     - float
     - ``0.0``
     - Initial map center latitude
   * - map_lon
     - float
     - ``0.0``
     - Initial map center longitude
   * - map_zoom
     - float
     - ``2``
     - Initial zoom level
   * - map_projection
     - str
     - ``"mercator"``
     - Map projection: ``"mercator"`` or ``"globe"``

Accessing the map object
------------------------

The map object becomes available after the map has finished loading.
Use the ``map_ready`` callback (triggered automatically) to store a reference:

.. code-block:: python

   # map_callbacks.py
   from app import app

   def map_ready(*args):
       element = app.gui.window.find_element_by_id("map")
       app.map = element.widget

       # Set up layers
       main = app.map.add_layer("main")
       main.add_layer("polygons", type="polygon")

   def map_moved(*args):
       # Called when the user pans or zooms
       pass

Map navigation methods
----------------------

.. list-table::
   :widths: 45 55
   :header-rows: 1

   * - Method
     - Description
   * - ``map.fly_to(lon, lat, zoom)``
     - Animate the map to a location
   * - ``map.fit_bounds(lon1, lat1, lon2, lat2)``
     - Zoom to fit a bounding box
   * - ``map.set_layer_style(style)``
     - Change the basemap style
   * - ``map.set_projection(projection)``
     - Switch between ``"mercator"`` and ``"globe"``
   * - ``map.set_terrain(enabled, exaggeration)``
     - Enable or disable 3D terrain
   * - ``map.click_point(callback)``
     - Register a one-shot click handler that returns ``(lon, lat)``
   * - ``map.take_screenshot(path)``
     - Save the current map view as a PNG

Basemap styles (MapLibre)
^^^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Style name
     - Description
   * - ``"osm"``
     - OpenStreetMap (default)
   * - ``"satellite"``
     - Satellite imagery
   * - ``"topo"``
     - Topographic map

Layer system
------------

All map data is organized into a **tree of layers**.
There are two kinds of layer objects:

* **Container layers** — grouping nodes with no visual output, created with ``add_layer(id)``
* **Data layers** — visual layers with a ``type``, created with ``add_layer(id, type="...")``

Creating layers
^^^^^^^^^^^^^^^

.. code-block:: python

   # Container layer
   main = app.map.add_layer("main")

   # Data layers inside the container
   main.add_layer("grid", type="polygon")
   main.add_layer("boundaries", type="line")
   main.add_layer("stations", type="circle")

Available layer types
^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - Type
     - Description
   * - ``polygon``
     - Filled/outlined polygons from a GeoDataFrame
   * - ``polygon_selector``
     - Polygons with click-selection support
   * - ``line``
     - Polylines from a GeoDataFrame
   * - ``line_selector``
     - Polylines with click-selection support
   * - ``circle``
     - Point circles from a GeoDataFrame or coordinate lists
   * - ``circle_selector``
     - Circles with click-selection support
   * - ``choropleth``
     - Attribute-colored polygons (colored by a data column)
   * - ``heatmap``
     - Heatmap from point data
   * - ``draw``
     - Interactive drawing layer (polygon, polyline, rectangle)
   * - ``marker``
     - PNG icon markers at point locations
   * - ``raster``
     - Raster image overlay (numpy array + extent)
   * - ``raster_image``
     - Direct image overlay
   * - ``raster_tile``
     - Tile-based raster (URL template)
   * - ``image``
     - Generic image overlay
   * - ``cyclone_track``
     - Specialized storm track visualization

Setting layer data
^^^^^^^^^^^^^^^^^^

Call ``set_data()`` on a data layer to pass it new content.
The input type depends on the layer type:

.. code-block:: python

   import geopandas as gpd

   # Polygon / line / circle layers: pass a GeoDataFrame
   gdf = gpd.read_file("boundaries.geojson")
   app.map.layer["main"].layer["boundaries"].set_data(gdf)

   # Raster layer: pass a numpy array and extent
   app.map.layer["main"].layer["flood_depth"].set_data(
       data=depth_array,         # 2D numpy array
       x0=lon_min, y0=lat_min,
       x1=lon_max, y1=lat_max
   )

Layer styling
^^^^^^^^^^^^^

Layer appearance is controlled by attributes set directly on the layer object
before or after ``set_data()``:

.. code-block:: python

   layer = app.map.layer["main"].layer["polygons"]
   layer.fill_color = "blue"
   layer.fill_opacity = 0.5
   layer.line_color = "black"
   layer.line_width = 1.0

Common style attributes:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Attribute
     - Description
   * - ``fill_color``
     - Fill color (color name, hex string, or ``"transparent"``)
   * - ``fill_opacity``
     - Fill opacity (0.0 – 1.0)
   * - ``line_color``
     - Outline/line color
   * - ``line_width``
     - Line width in pixels
   * - ``circle_radius``
     - Circle radius in pixels (circle layers)
   * - ``hover_color``
     - Color when the mouse hovers over a feature
   * - ``selected_color``
     - Color when a feature is selected

Layer visibility
^^^^^^^^^^^^^^^^

.. code-block:: python

   layer.set_visible(True)   # show
   layer.set_visible(False)  # hide

Draw layer
^^^^^^^^^^

The draw layer lets users draw features interactively on the map.
The drawn features are stored as a GeoDataFrame accessible via ``layer.gdf``.

.. code-block:: python

   draw = app.map.layer["main"].layer["drawing"]

   # Start drawing
   draw.draw_polygon()
   draw.draw_polyline()
   draw.draw_rectangle()

   # Stop drawing and switch to select mode
   draw.stop_drawing()

   # Access drawn features
   gdf = draw.gdf   # GeoDataFrame with all drawn features

Map event callbacks
-------------------

The map module in your YAML config can define callback functions that are called
for map events:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - Function name
     - When called
   * - ``map_ready``
     - Map has loaded and is ready; set up layers here
   * - ``map_moved``
     - User panned or zoomed the map
   * - ``mouse_moved``
     - Mouse cursor moved over the map (receives ``lon``, ``lat``)

Click and selection events are delivered to Python via the layer's callback attributes:

.. code-block:: python

   layer = app.map.layer["main"].layer["polygons"]
   layer.callback_click = my_click_callback   # called with feature index

Using Mapbox
------------

To use Mapbox GL instead of MapLibre, set ``map_engine="mapbox"`` when creating the GUI:

.. code-block:: python

   self.gui = GUI(self, config_file="myapp.yml", map_engine="mapbox")

You must also place a file named ``mapbox_token.txt`` in the same directory as your
config file, containing your Mapbox public access token on a single line.

Mapbox supports additional basemap styles:

.. code-block:: yaml

   map_style: mapbox://styles/mapbox/streets-v12
   map_style: mapbox://styles/mapbox/satellite-v9
   map_style: mapbox://styles/mapbox/outdoors-v12
   map_style: mapbox://styles/mapbox/light-v11
   map_style: mapbox://styles/mapbox/dark-v11
