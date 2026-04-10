Variables
=========

All required GUI variables should be defined before the GUI is built.
This is typically done in the ``__init__()`` method of the *Application* class (in **app.py**).
The standard way to set and get variables is through the ``gui`` object's ``setvar`` and ``getvar`` methods.

Variable groups
---------------

GUI variables are stored in a ``dict`` organized into named **groups**.
For simple applications, a single group is often sufficient.
For more complex applications it is useful to organize variables into multiple groups,
especially when the same variable name is needed for different purposes.

For example, if you use the name ``x`` for the x-coordinate of two different map features,
define separate groups:

.. code-block:: python

   app.gui.setvar("feature1", "x", 1.0)
   app.gui.setvar("feature2", "x", 2.0)

Setting variables
-----------------

Use ``setvar`` to store a value:

.. code-block:: python

   app.gui.setvar("mygroup", "varname", value)

Alternatively, access the underlying dict directly:

.. code-block:: python

   app.gui.variables["mygroup"]["varname"]["value"] = value

When a variable is updated inside a callback, the GUI automatically refreshes to display the new value.

Getting variables
-----------------

Use ``getvar`` to retrieve a value:

.. code-block:: python

   value = app.gui.getvar("mygroup", "varname")

Or access the dict directly:

.. code-block:: python

   value = app.gui.variables["mygroup"]["varname"]["value"]

Variable types
--------------

The type of a variable is inferred automatically from the value passed to ``setvar``.
The type determines how the widget displays and validates input:

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Python type
     - Widget behavior
   * - ``str``
     - Edit box shows text; no numeric validation
   * - ``int``
     - Edit box and spinbox enforce integer input and right-align numbers
   * - ``float``
     - Edit box and spinbox enforce float input and right-align numbers
   * - ``bool``
     - Used by checkboxes and dependencies

Linking variables to elements
------------------------------

In the YAML configuration, each interactive element is linked to a variable via the ``variable``
and ``variable_group`` keys:

.. code-block:: yaml

   - style: edit
     variable: grid_resolution
     variable_group: model
     method: update_grid

When the user edits the value, the new value is written to ``gui.variables["model"]["grid_resolution"]["value"]``
and the callback ``update_grid`` is called.

The ``variable_group`` defaults to the value set in the ``window`` section of the config file,
so it only needs to be specified when it differs from the window default.

Dynamic labels and tooltips
---------------------------

Labels (``text``) and tooltips can be either static strings or dynamic — reading from a variable:

.. code-block:: yaml

   text:
     variable: status_message
     variable_group: mygroup

When the variable changes, the label updates automatically on the next GUI refresh.
