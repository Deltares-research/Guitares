Menu
====

An optional drop-down menu bar can be added to the main window by including a ``menu`` key
in the YAML configuration file.

Basic structure
---------------

.. code-block:: yaml

   window:
     title: My Application
     width: 800
     height: 600
     module: callbacks
     variable_group: myapp

   menu:
   - text: File
     menu:
     - text: Open
       method: open_file
     - text: Save
       method: save_file
       separator: true
     - text: Exit
       method: exit

   - text: Help
     menu:
     - text: About
       method: show_about

Menu keys
---------

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
     - Menu item label
   * - method
     - str
     -
     - Callback function called when the item is clicked
   * - module
     - str
     - inherited
     - Callback module override for this item (and its sub-items)
   * - menu
     - list
     -
     - Sub-menu items (creates a nested sub-menu)
   * - separator
     - bool
     - ``false``
     - Draw a separator line **above** this item
   * - checkable
     - bool
     - ``false``
     - Make the item a toggle (checkable menu item)

Nested sub-menus
----------------

Menu items can be nested to any depth by adding a ``menu`` key to a menu item:

.. code-block:: yaml

   menu:
   - text: View
     menu:
     - text: Layers
       menu:
       - text: Show grid
         checkable: true
         method: toggle_grid
       - text: Show boundaries
         checkable: true
         method: toggle_boundaries

Per-menu callback modules
--------------------------

The callback module can be set globally in the ``window`` block, or overridden for individual
top-level menus:

.. code-block:: yaml

   menu:
   - text: File
     module: file_menu_callbacks
     menu:
     - text: Open
       method: open_file
   - text: Edit
     module: edit_menu_callbacks
     menu:
     - text: Undo
       method: undo

Menu callbacks
--------------

Menu callbacks follow the same convention as element callbacks (see :doc:`callbacks`):

.. code-block:: python

   # file_menu_callbacks.py
   from app import app

   def open_file(*args):
       path = app.gui.getvar("myapp", "last_directory")
       # ... open file dialog ...

Checkable menu items
--------------------

A checkable menu item stores its checked state automatically.
The callback receives ``True`` or ``False`` as its first argument:

.. code-block:: python

   def toggle_grid(checked, widget):
       app.gui.setvar("myapp", "show_grid", checked)
       # ... update map layer visibility ...
