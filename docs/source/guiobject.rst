The GUI Object
==============

The ``GUI`` class is the central object of a Guitares application.
It is instantiated once in ``app.py`` and holds all configuration, variables, and references to
the window and widgets.

Creating the GUI object
-----------------------

.. code-block:: python

   from guitares.gui import GUI

   class Application:
       def __init__(self):
           self.gui = GUI(
               self,
               config_file="myapp.yml",
               framework="pyside6",      # only PySide6 is actively maintained
               map_engine="maplibre",    # "maplibre" (default) or "mapbox"
               server_path="server",     # folder where map JS assets are copied
               resize_factor=1.0,        # scale factor for high-DPI screens
           )
           # Define variables before building
           self.gui.setvar("myapp", "dx", 100.0)
           self.gui.setvar("myapp", "dy", 100.0)

   app = Application()

Building and running
--------------------

After creating the object and setting variables, call ``build()`` to create the window and
start the Qt event loop:

.. code-block:: python

   # myapp.py
   from app import app

   if __name__ == "__main__":
       app.gui.build()

Variable methods
----------------

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - Method
     - Description
   * - ``gui.setvar(group, name, value)``
     - Set a variable value. Creates the group and variable if they do not exist.
   * - ``gui.getvar(group, name)``
     - Get a variable value. Returns ``None`` if the variable does not exist.

Window methods
--------------

These methods are available on ``gui.window`` (the main window object):

.. list-table::
   :widths: 40 60
   :header-rows: 1

   * - Method
     - Description
   * - ``gui.window.update()``
     - Refresh all elements to reflect current variable values. Called automatically after each callback.
   * - ``gui.window.find_element_by_id(id)``
     - Find an element by its ``id`` key from the YAML config.

Popup windows
-------------

Use ``gui.popup()`` to open a modal dialog that reads and returns data:

.. code-block:: python

   okay, data = app.gui.popup("popup_config.yml", "my_popup", initial_data)

* The first argument is a YAML config file for the popup window.
* The second argument is a string ID for the popup.
* The third argument is data passed into the popup (accessible in the popup's callbacks).
* Returns ``(True, data)`` when the user clicks OK, or ``(False, data)`` on Cancel.

The popup config uses the same ``window`` and ``element`` YAML structure as the main window,
but the window is displayed as a modal dialog with automatic OK and Cancel buttons.

See :doc:`popup_window` for a full example.

Map access
----------

After the map widget has loaded, the map object is typically stored on ``app.map`` by the
``map_ready`` callback:

.. code-block:: python

   def map_ready(*args):
       element = app.gui.window.find_element_by_id("map")
       app.map = element.widget
       main_layer = app.map.add_layer("main")
       # ...

See :doc:`map` for full map API documentation.

Resize factor
-------------

On high-DPI screens (e.g. 4K monitors), set ``resize_factor`` to scale all pixel positions from the
YAML config:

.. code-block:: python

   self.gui = GUI(self, config_file="myapp.yml", resize_factor=1.5)

All ``x``, ``y``, ``width``, ``height`` values in the YAML are multiplied by this factor at
runtime.
