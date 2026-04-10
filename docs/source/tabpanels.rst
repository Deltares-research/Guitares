Using tab panels
================

A tab panel (``style: tabpanel``) is a container element that organizes child elements into
named tabs. Only one tab is visible at a time; the user switches between tabs by clicking the
tab headers.

Basic structure
---------------

.. code-block:: yaml

   - style: tabpanel
     position: {x: 10, y: 10, width: -10, height: 160}
     tab:
     - text: Settings
       module: settings_callbacks
       element:
       - style: edit
         position: {x: 10, y: 10, width: 200, height: 24}
         variable: dx
         text: Resolution

     - text: Results
       module: results_callbacks
       element:
       - style: text
         position: {x: 10, y: 10, width: 300, height: 20}
         variable: status

Tab keys
--------

.. list-table::
   :widths: 25 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **text**
     - str
     -
     - Tab header label (``string`` also accepted for backward compatibility)
   * - module
     - str
     - inherited
     - Callback module for all elements in this tab
   * - variable_group
     - str
     - inherited
     - Variable group for all elements in this tab
   * - element
     - list / str
     -
     - Child elements — either inline list or a path to an external YAML file
   * - dependency
     - list
     -
     - Conditional enable/visible rules for the tab itself

Loading elements from external files
-------------------------------------

For large applications it is convenient to split each tab's elements into a separate YAML file.
Set the ``element`` key to a filename (relative to the main config file):

.. code-block:: yaml

   - style: tabpanel
     position: {x: 10, y: 10, width: -10, height: 160}
     tab:
     - text: Grid
       module: grid_callbacks
       element: grid.yml

     - text: Boundaries
       module: boundary_callbacks
       element: boundaries.yml

     - text: Output
       module: output_callbacks
       element: output.yml

The referenced file contains only an ``element`` list (no ``window`` key):

.. code-block:: yaml

   # grid.yml
   element:
   - style: spinbox
     position: {x: 10, y: 10, width: 120, height: 24}
     variable: dx
     text: Resolution (m)
     method: update_grid

Tab dependencies
----------------

Individual tabs can be shown/hidden or enabled/disabled using ``dependency`` rules.
This is useful for hiding tabs that are not relevant for the current application state:

.. code-block:: yaml

   tab:
   - text: Advanced
     module: advanced_callbacks
     element: advanced.yml
     dependency:
     - action: visible
       checkfor: all
       check:
       - variable: expert_mode
         operator: eq
         value: true

See :doc:`dependencies` for the full dependency syntax.

Nested tab panels
-----------------

Tab panels can be nested — a tab can contain another ``tabpanel`` element in its element list.
This is useful for building hierarchical interfaces.
