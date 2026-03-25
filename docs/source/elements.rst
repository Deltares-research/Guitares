Elements
========

This page describes every available element ``style`` and its configuration keys.
Keys shown in **bold** are required. All others are optional.

Common keys shared by all (or most) elements are described in :doc:`configuration`.

.. contents:: Widgets
   :local:
   :depth: 1

----

Edit box
--------

``style: edit``

A single-line text input. The variable type (``str``, ``int``, or ``float``) is inferred from the
variable's initial value. Numeric inputs are right-aligned and highlighted red on invalid input.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement; see :doc:`positioning`
   * - **variable**
     - str
     -
     - Variable name
   * - variable_group
     - str
     - inherited
     - Variable group
   * - method
     - str
     -
     - Callback on editing finished
   * - text
     - str / dict
     - ``""``
     - Label
   * - text_position
     - str
     - ``"left"``
     - Label placement: ``left``, ``right``, ``above``, ``above-center``, ``above-left``
   * - tooltip
     - str / dict
     - ``""``
     - Tooltip text
   * - enable
     - bool
     - ``true``
     - Whether the field is editable

Example:

.. code-block:: yaml

   - style: edit
     position: {x: 120, y: 40, width: 100, height: 24}
     variable: grid_resolution
     variable_group: model
     method: update_grid
     text: Resolution (m)
     tooltip: Grid cell size in metres

----

Spin box
--------

``style: spinbox``

A numeric input with up/down arrow buttons. Automatically uses an integer spinbox or a floating-point
spinbox depending on the type of the linked variable.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Variable name (type determines int vs float spinbox)
   * - variable_group
     - str
     - inherited
     - Variable group
   * - method
     - str
     -
     - Callback fired when the user stops changing the value
   * - minimum
     - int / float
     - ``0``
     - Minimum allowed value
   * - maximum
     - int / float
     - ``100``
     - Maximum allowed value
   * - step
     - int / float
     - ``1`` (int) / ``0.1`` (float)
     - Step size per arrow click
   * - decimals
     - int
     - ``2``
     - Number of decimal places (float spinbox only)
   * - suffix
     - str
     - ``""``
     - Unit string appended to the displayed value, e.g. ``" m"``
   * - text
     - str / dict
     - ``""``
     - Label
   * - text_position
     - str
     - ``"left"``
     - Label placement
   * - tooltip
     - str / dict
     - ``""``
     - Tooltip text
   * - enable
     - bool
     - ``true``
     - Whether the spinbox is interactive

Example:

.. code-block:: yaml

   - style: spinbox
     position: {x: 120, y: 40, width: 120, height: 24}
     variable: grid_resolution
     variable_group: model
     minimum: 10
     maximum: 10000
     step: 10
     suffix: " m"
     text: Resolution
     method: update_grid

----

Text
----

``style: text``

A read-only label that displays the value of a variable as a string. Updated automatically when the
variable changes.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - variable
     - str
     -
     - Variable whose value is displayed
   * - variable_group
     - str
     - inherited
     - Variable group
   * - text
     - str / dict
     - ``""``
     - Static text (use ``variable`` for a dynamic value)

Example:

.. code-block:: yaml

   - style: text
     position: {x: 10, y: 10, width: 300, height: 20}
     variable: status_message

----

Push button
-----------

``style: pushbutton``

A clickable button that triggers a callback.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **text**
     - str / dict
     -
     - Button label
   * - method
     - str
     -
     - Callback on click
   * - icon
     - str
     -
     - Path to an image shown on the button
   * - tooltip
     - str / dict
     - ``""``
     - Tooltip text
   * - enable
     - bool
     - ``true``
     - Whether the button is clickable

Example:

.. code-block:: yaml

   - style: pushbutton
     position: {x: 10, y: 10, width: 120, height: 28}
     text: Run Model
     method: run_model
     tooltip: Start the simulation

----

Pop-up menu
-----------

``style: popupmenu``

A dropdown (combo box) from which the user selects one item.

Items can be defined as a static list in the YAML or as a variable that is updated at runtime.

The ``select`` key controls what value is stored in the variable:

* ``"item"`` — stores the value from ``option_value`` corresponding to the selected index
* ``"index"`` — stores the zero-based index of the selected item

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Variable that stores the selected item or index
   * - variable_group
     - str
     - inherited
     - Variable group
   * - option_string
     - list / dict
     -
     - Display strings. Static list or ``{variable, variable_group}``
   * - option_value
     - list / dict
     -
     - Values associated with each string. Static list or ``{variable, variable_group}``
   * - select
     - str
     - ``"item"``
     - What to store: ``"item"`` or ``"index"``
   * - method
     - str
     -
     - Callback on selection change
   * - text
     - str / dict
     - ``""``
     - Label
   * - text_position
     - str
     - ``"left"``
     - Label placement
   * - tooltip
     - str / dict
     - ``""``
     - Tooltip
   * - enable
     - bool
     - ``true``
     -

Example (static list):

.. code-block:: yaml

   - style: popupmenu
     position: {x: 100, y: 40, width: 120, height: 24}
     variable: operator
     select: item
     option_string: ["+", "-", "*", "/"]
     option_value: ["add", "subtract", "multiply", "divide"]
     method: calculate

Example (dynamic list from variables):

.. code-block:: yaml

   - style: popupmenu
     position: {x: 100, y: 40, width: 120, height: 24}
     variable: scenario
     select: item
     option_string: {variable: scenario_names}
     option_value: {variable: scenario_ids}
     method: change_scenario

----

List box
--------

``style: listbox``

A scrollable list from which the user selects one or more items.
The ``select`` and ``multiselection`` keys work the same way as for the pop-up menu.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Selected item/index (or list of them when ``multiselection: true``)
   * - variable_group
     - str
     - inherited
     - Variable group
   * - option_string
     - list / dict
     -
     - Display strings
   * - option_value
     - list / dict
     -
     - Associated values
   * - select
     - str
     - ``"item"``
     - ``"item"`` or ``"index"``
   * - multiselection
     - bool
     - ``false``
     - Allow multiple selections
   * - method
     - str
     -
     - Callback on selection change
   * - text
     - str / dict
     - ``""``
     - Label
   * - text_position
     - str
     - ``"left"``
     - Label placement
   * - tooltip
     - str / dict
     - ``""``
     - Tooltip
   * - enable
     - bool
     - ``true``
     -

----

Check box
---------

``style: checkbox``

A toggle that stores ``True`` or ``False`` in the linked variable.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Boolean variable
   * - variable_group
     - str
     - inherited
     - Variable group
   * - text
     - str / dict
     - ``""``
     - Checkbox label (shown to the right of the checkbox)
   * - method
     - str
     -
     - Callback on toggle
   * - tooltip
     - str / dict
     - ``""``
     - Tooltip
   * - enable
     - bool
     - ``true``
     -

Example:

.. code-block:: yaml

   - style: checkbox
     position: {x: 10, y: 40, width: 150, height: 20}
     variable: show_grid
     text: Show grid
     method: toggle_grid

----

Radio button group
------------------

``style: radiobuttongroup``

A group of mutually exclusive radio buttons.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Variable storing the selected value
   * - variable_group
     - str
     - inherited
     - Variable group
   * - **option_string**
     - list
     -
     - Label for each radio button
   * - **option_value**
     - list
     -
     - Value stored when each button is selected
   * - method
     - str
     -
     - Callback on selection change
   * - enable
     - bool
     - ``true``
     -

Example:

.. code-block:: yaml

   - style: radiobuttongroup
     position: {x: 10, y: 10, width: 200, height: 60}
     variable: interpolation_method
     option_string: [Nearest, Linear, Cubic]
     option_value: [nearest, linear, cubic]
     method: change_interpolation

----

Slider
------

``style: slider``

A horizontal slider for selecting a value in a numeric range.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Variable storing the current value (integer)
   * - variable_group
     - str
     - inherited
     - Variable group
   * - minimum
     - int
     - ``0``
     - Minimum value
   * - maximum
     - int
     - ``100``
     - Maximum value
   * - method
     - str
     -
     - Callback fired when the user releases the slider
   * - slide_method
     - str
     -
     - Callback fired continuously while dragging
   * - text
     - str / dict
     - ``""``
     - Label
   * - enable
     - bool
     - ``true``
     -

Example:

.. code-block:: yaml

   - style: slider
     position: {x: 200, y: 40, width: 300, height: 24}
     variable: year
     minimum: 2000
     maximum: 2100
     slide_method: update_year_label
     method: reload_data

----

Date/time edit
--------------

``style: datetimeedit``

A date and time picker widget.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Variable storing the datetime value
   * - variable_group
     - str
     - inherited
     - Variable group
   * - method
     - str
     -
     - Callback on value change
   * - text
     - str / dict
     - ``""``
     - Label
   * - text_position
     - str
     - ``"left"``
     - Label placement

----

Table view
----------

``style: tableview``

A read-only (or sortable) table populated from a ``pandas.DataFrame`` stored in a variable.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - variable
     - str
     -
     - Variable storing the selected row index or indices
   * - variable_group
     - str
     - inherited
     - Variable group
   * - option_value
     - dict
     -
     - ``{variable, variable_group}`` pointing to the DataFrame variable
   * - selection_type
     - str
     - ``"single"``
     - ``"none"``, ``"single"``, ``"multiple"``, ``"extended"``
   * - selection_direction
     - str
     - ``"row"``
     - ``"row"`` or ``"column"``
   * - sortable
     - bool
     - ``true``
     - Whether clicking a column header sorts the table
   * - method
     - str
     -
     - Callback on row/column selection
   * - text
     - str / dict
     - ``""``
     - Label
   * - text_position
     - str
     - ``"above"``
     - Label placement

Example:

.. code-block:: yaml

   - style: tableview
     position: {x: 10, y: 10, width: -10, height: 200}
     text: Available scenarios
     text_position: above
     variable: selected_row
     option_value: {variable: scenarios_df}
     selection_type: single
     method: select_scenario

----

File/directory chooser buttons
-------------------------------

Three button styles open system file/directory dialogs and store the chosen path in a variable.

**Open file:** ``style: pushselectfile``

**Open directory:** ``style: pushselectdir``

**Save file:** ``style: pushsavefile``

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - **variable**
     - str
     -
     - Variable that receives the chosen path
   * - variable_group
     - str
     - inherited
     - Variable group
   * - text
     - str / dict
     -
     - Button label
   * - title
     - str
     - ``"Select File"``
     - Dialog window title
   * - filter
     - str
     - ``"All Files (*.*)"``
     - File type filter, e.g. ``"NetCDF (*.nc)"``
   * - full_path
     - bool
     - ``false``
     - Store the full path; if ``false`` stores only the filename
   * - method
     - str
     -
     - Callback after a path is selected

Example:

.. code-block:: yaml

   - style: pushselectfile
     position: {x: 10, y: 40, width: 160, height: 24}
     variable: bathymetry_file
     text: Select bathymetry file
     title: Open bathymetry file
     filter: NetCDF (*.nc);;All Files (*.*)
     method: load_bathymetry

----

Web view
--------

``style: webpage``

Embeds a web browser (PySide6 WebEngine) that displays a URL.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Element placement
   * - url
     - str / dict
     - ``""``
     - URL to load (static or from variable)

Example:

.. code-block:: yaml

   - style: webpage
     url: https://guitares.readthedocs.io/
     position: {x: 10, y: 10, width: -10, height: -10}

----

Frame (panel)
-------------

``style: panel``

A container that groups child elements. Frames can optionally show a border with a title and can
be made collapsible.

.. list-table::
   :widths: 30 10 15 45
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **position**
     - dict
     -
     - Placement of the frame within its parent
   * - title
     - str
     -
     - Border title (no border shown if omitted)
   * - element
     - list
     -
     - Child elements (same syntax as the top-level ``element`` list)
   * - collapse
     - bool
     - ``false``
     - Make the frame collapsible
   * - collapsed
     - bool
     - ``false``
     - Initial collapsed state
   * - fraction_expanded
     - float
     - ``0.5``
     - Fraction of parent taken when expanded (used with ``collapse: true``)
   * - fraction_collapsed
     - float
     - ``1.0``
     - Fraction of parent taken when collapsed
   * - id
     - str
     -
     - Unique identifier (required for collapsible frames)

Example:

.. code-block:: yaml

   - style: panel
     title: Model settings
     position: {x: 10, y: 10, width: 300, height: -10}
     element:
     - style: spinbox
       position: {x: 10, y: 10, width: 120, height: 24}
       variable: dx
       text: dx
       suffix: " m"

----

Tab panel
---------

``style: tabpanel``

A container with multiple named tabs, each holding its own set of child elements.
See :doc:`tabpanels` for full documentation.

Map
---

``style: map`` (or ``style: maplibre`` / ``style: mapbox``)

An interactive map widget. See :doc:`map` for full documentation.
