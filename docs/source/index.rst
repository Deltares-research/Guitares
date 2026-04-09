Welcome to the Guitares documentation!
======================================

Guitares is a Python package for building configurable Graphical User Interfaces (GUIs) using PySide6.
GUI layouts are defined in YAML configuration files rather than code, keeping application logic cleanly separated from the interface description.

A Guitares GUI consists of a main window (with optional drop-down menu) that contains one or more UI elements.
The following elements are currently supported:

* Tab panels
* Frames (panels)
* Edit boxes
* Spin boxes
* Text labels
* Pop-up menus (dropdowns)
* List boxes
* Check boxes
* Radio button groups
* Sliders
* Push buttons
* Date/time edit boxes
* Table views
* File/directory chooser buttons
* Web views
* Map (MapLibre GL or Mapbox GL)

Check out the :doc:`getting_started` section for installation instructions and a quick-start guide.

.. note::

   This project is under active development.

Contents
--------

.. toctree::
   :maxdepth: 2

   getting_started
   simple_example
   configuration
   positioning
   elements
   variables
   callbacks
   dependencies
   tabpanels
   menu
   map
   popup_window
   dialogs
   edit_mode
   stylesheets
   guiobject
   examples
