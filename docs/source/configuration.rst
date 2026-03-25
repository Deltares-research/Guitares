Configuration
=============

A Guitares GUI is described in a **YAML configuration file**.
The file has two top-level keys: ``window`` and ``element``.

Window properties
-----------------

The ``window`` key defines global properties of the main window.

.. list-table::
   :widths: 25 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **title**
     - str
     -
     - Window title bar text
   * - **width**
     - int
     -
     - Window width in pixels
   * - **height**
     - int
     -
     - Window height in pixels
   * - module
     - str
     -
     - Default callback module (Python module name, without ``.py``)
   * - variable_group
     - str
     -
     - Default variable group inherited by all elements
   * - icon
     - str
     -
     - Path to a window icon image file

Example:

.. code-block:: yaml

   window:
     title: My Application
     width: 1000
     height: 700
     module: callbacks
     variable_group: myapp

Elements list
-------------

The ``element`` key holds a list of UI elements to place in the window.
Each item in the list is a dict with at minimum a ``style`` and ``position``.

.. code-block:: yaml

   element:
   - style: edit
     position: {x: 100, y: 40, width: 200, height: 24}
     variable: my_variable
     method: my_callback

   - style: pushbutton
     position: {x: 100, y: 10, width: 100, height: 24}
     text: Run
     method: run_model

See :doc:`elements` for the full list of available styles and their options.

Menu
----

An optional ``menu`` key adds a drop-down menu bar. See :doc:`menu` for details.

Splitting config across files
-----------------------------

For large applications it is common to split the element list across multiple YAML files.
Tab panels support an ``element`` key that references an external file:

.. code-block:: yaml

   element:
   - style: tabpanel
     position: {x: 10, y: 10, width: -10, height: 160}
     tab:
     - text: Settings
       module: settings_callbacks
       element: settings.yml     # loaded from the same directory
     - text: Results
       module: results_callbacks
       element: results.yml

See :doc:`tabpanels` for more information.

Common element keys
-------------------

The following keys are shared by most element types:

.. list-table::
   :widths: 25 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **style**
     - str
     -
     - Widget type (``edit``, ``pushbutton``, ``popupmenu``, etc.)
   * - **position**
     - dict
     -
     - Placement; see :doc:`positioning`
   * - variable
     - str
     -
     - Name of the GUI variable this element reads/writes
   * - variable_group
     - str
     - inherited
     - Variable group; overrides the window default
   * - module
     - str
     - inherited
     - Callback module; overrides the window default
   * - method
     - str
     -
     - Callback function called on user interaction
   * - text
     - str or dict
     - ``""``
     - Label string, or ``{variable, variable_group}`` for a dynamic label
   * - text_position
     - str
     - ``"left"``
     - Label placement: ``left``, ``right``, ``above``, ``above-center``, ``above-left``
   * - tooltip
     - str or dict
     - ``""``
     - Tooltip text, or ``{variable, variable_group}`` for a dynamic tooltip
   * - enable
     - bool
     - ``true``
     - Whether the element is interactive
   * - dependency
     - list
     -
     - Conditional enable/visible rules; see :doc:`dependencies`
