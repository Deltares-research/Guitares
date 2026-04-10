Element dependencies
====================

The **dependency** system allows elements to be automatically shown/hidden or enabled/disabled
based on the current values of GUI variables — without writing any Python code.

Any element can carry a ``dependency`` list in its YAML configuration.
After every user interaction, Guitares re-evaluates all dependency rules and updates the GUI
accordingly.

Basic structure
---------------

.. code-block:: yaml

   - style: pushbutton
     text: Delete
     method: delete_item
     dependency:
     - action: enable
       checkfor: all
       check:
       - variable: selected_index
         operator: ge
         value: 0

This button is only enabled when ``selected_index >= 0``.

Dependency keys
---------------

.. list-table::
   :widths: 25 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **action**
     - str
     -
     - What to control: ``"enable"``, ``"visible"``, or ``"check"``
   * - **checkfor**
     - str
     -
     - How to combine checks: ``"all"``, ``"any"``, or ``"none"``
   * - **check**
     - list
     -
     - List of individual variable checks (see below)

Check keys
----------

Each entry in the ``check`` list compares a variable against a value:

.. list-table::
   :widths: 25 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description
   * - **variable**
     - str
     -
     - Variable name to check
   * - variable_group
     - str
     - inherited
     - Variable group
   * - **operator**
     - str
     -
     - Comparison operator (see table below)
   * - **value**
     - any
     -
     - Value to compare against

Supported operators:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Operator
     - Meaning
   * - ``eq``
     - Equal to
   * - ``ne``
     - Not equal to
   * - ``gt``
     - Greater than
   * - ``ge``
     - Greater than or equal to
   * - ``lt``
     - Less than
   * - ``le``
     - Less than or equal to

Actions
-------

* **enable** — the element is enabled when the condition is true; disabled otherwise.
* **visible** — the element (and its label) is shown when the condition is true; hidden otherwise.
* **check** — sets the checked state of a checkbox to the condition result.

checkfor logic
--------------

* **all** — all checks must be true
* **any** — at least one check must be true
* **none** — no checks must be true (i.e. all checks must be false)

Examples
--------

Enable a button only when at least one item exists in a list:

.. code-block:: yaml

   dependency:
   - action: enable
     checkfor: all
     check:
     - variable: nr_items
       operator: gt
       value: 0

Show an extra panel only when a specific scenario is selected:

.. code-block:: yaml

   dependency:
   - action: visible
     checkfor: all
     check:
     - variable: scenario
       variable_group: model
       operator: eq
       value: "advanced"

Multiple conditions — enable only when both a file is loaded and a feature is selected:

.. code-block:: yaml

   dependency:
   - action: enable
     checkfor: all
     check:
     - variable: file_loaded
       operator: eq
       value: true
     - variable: selected_index
       operator: ge
       value: 0

Enable when *either* of two conditions holds:

.. code-block:: yaml

   dependency:
   - action: enable
     checkfor: any
     check:
     - variable: mode
       operator: eq
       value: "edit"
     - variable: mode
       operator: eq
       value: "draw"

Multiple dependency rules
-------------------------

An element can have multiple ``dependency`` entries.
All rules are evaluated independently — each controls its own ``action``:

.. code-block:: yaml

   dependency:
   - action: enable
     checkfor: all
     check:
     - variable: model_loaded
       operator: eq
       value: true
   - action: visible
     checkfor: all
     check:
     - variable: show_advanced
       operator: eq
       value: true
