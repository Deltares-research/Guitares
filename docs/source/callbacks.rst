Callbacks
=========

A **callback** is a Python function that is called automatically when the user interacts with a
GUI element (e.g. edits a value, clicks a button, selects a list item).

Defining callbacks
------------------

Callbacks are defined as plain functions in a Python **callback module**.
The module is specified in the YAML config at the window or element level:

.. code-block:: yaml

   window:
     module: callbacks        # default callback module for all elements
     variable_group: myapp

   element:
   - style: edit
     variable: dx
     method: update_resolution   # calls callbacks.update_resolution

   - style: pushbutton
     text: Run
     method: run_model
     module: run_callbacks       # override: calls run_callbacks.run_model

Callback signature
------------------

Every callback function receives two arguments:

.. code-block:: python

   def my_callback(value, widget):
       ...

* **value** — the current value of the variable linked to the element that triggered the callback.
  For an edit box this is the entered number or string; for a listbox it is the selected item or index;
  for a checkbox it is ``True`` or ``False``.
* **widget** — the underlying PySide6 widget object. This is rarely needed but can be used for
  advanced widget manipulation.

Both arguments can be ignored using ``*args``:

.. code-block:: python

   def my_callback(*args):
       ...

Reading and writing variables inside a callback
-----------------------------------------------

Inside a callback, use ``app.gui.getvar`` and ``app.gui.setvar`` to read and update variables.
After the callback returns, Guitares automatically refreshes all GUI elements to reflect any
variable changes:

.. code-block:: python

   from app import app

   def update_resolution(*args):
       dx = app.gui.getvar("model", "dx")
       dy = app.gui.getvar("model", "dy")
       # ... do something with dx, dy ...
       app.gui.setvar("model", "cell_count", int(domain_area / (dx * dy)))

Callback modules
----------------

A callback module is a plain Python file. It is imported once when the GUI is built.
The ``app`` object should be imported at the top of the module so that variables and GUI
methods are accessible:

.. code-block:: python

   # callbacks.py
   from app import app

   def enter_name(value, widget):
       name = app.gui.getvar("hello", "name")
       app.gui.setvar("hello", "response", f"Hello, {name}!")

Dot-notation for class methods
-------------------------------

If callbacks are methods on a class, use dot notation in the ``method`` field:

.. code-block:: yaml

   method: MyProcessor.process

Guitares will instantiate ``MyProcessor()`` and call ``process()`` on it.

Slider callbacks
----------------

The slider supports two callbacks:

.. list-table::
   :widths: 25 75
   :header-rows: 1

   * - YAML key
     - When called
   * - ``slide_method``
     - Called continuously while the user is dragging the slider
   * - ``method``
     - Called once when the user releases the slider

This is useful when the dragging callback should do a lightweight update (e.g. update a year label)
while the release callback triggers a heavier operation (e.g. reload map data).
