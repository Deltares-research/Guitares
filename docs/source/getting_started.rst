Getting started
===============

Prerequisites
-------------

Guitares requires Python 3.10 or higher. The following packages are installed automatically as dependencies:

* **PySide6** — Qt6 bindings for Python
* **PySide6-WebEngine** — web engine for the map widget and webpage element
* **PyYAML** — YAML configuration file parsing
* **geopandas**, **numpy**, **pandas**, **pyproj**, **shapely** — geospatial and numerical support

Installation
------------

Install the latest release from PyPI:

.. code-block:: bash

    pip install guitares

For an editable installation from source (useful during development):

.. code-block:: bash

    git clone https://github.com/deltares-research/guitares.git
    cd guitares
    pip install -e .

Verifying the installation
--------------------------

After installation, run the included ``hello`` example to verify everything works:

.. code-block:: bash

    cd examples/hello
    python hello.py

You should see a small window with an edit box that greets you by name.

Project structure
-----------------

A Guitares application consists of four files:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - File
     - Purpose
   * - ``myapp.yml``
     - YAML configuration file describing the window and all UI elements
   * - ``app.py``
     - Creates the ``Application`` class, initializes variables, and builds the GUI
   * - ``callbacks.py``
     - Contains callback functions that run when the user interacts with the GUI
   * - ``myapp.py``
     - Entry point that imports ``app`` and calls ``app.gui.build()``

See :doc:`simple_example` for a complete walkthrough.

Map engine
----------

Guitares supports two map engines for the interactive map widget.
The engine is selected when creating the ``GUI`` object:

.. code-block:: python

    from guitares.gui import GUI
    gui = GUI(app, config_file="myapp.yml", map_engine="maplibre")

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Engine
     - Notes
   * - ``"maplibre"``
     - Open-source, no API token required, works offline. **Recommended default.**
   * - ``"mapbox"``
     - Requires a Mapbox API token stored in a file called ``mapbox_token.txt`` next to your config file.

See :doc:`map` for full documentation of the map widget.
