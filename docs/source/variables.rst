Variables
=========

All required GUI variables should be defined before the GUI is built.
This should therefore be done somewhere in the __init__() method of the *Application* class (in the **app module**).
The standard way to set and get variables is with *gui* objects *setvar* and *getvar* methods.

GUI variables are stored as a ``dict`` in groups (keys) with unique names.
For simple applications, using just one group is often sufficient.
For more complex situations, it is advisable to classify them in more groups.
This becomes particularly important when you have variables with different roles that share the same name.
You may for example use the name *x* for the x-coordinate of one map feature, and the same name *x* for coordinate of another map feature.
You will now want to define two groups (e.g. *feature1* and *feature2*):

.. code-block:: python

      app.gui.getvar("feature1", "x", 1.0)
      app.gui.getvar("feature2", "x", 2.0)

Alternatively, you can use:

.. code-block:: python

      app.gui.variables["feature1"]["x"]["value"] = 1.0
      app.gui.variables["feature2"]["x"]["value"] = 2.0

When GUI variables are set like this within a callback method, their new values will automatically appear in the GUI.

Accessing variables
-------------------

You will often want to access the value of a GUI variable in one the callback methods.
Let's assume that a GUI variable *varname* that sits in the group *vargroup* was changed within an **Edit** box that has the callback method *edit_varname*.
The standard way to access the value of *varname*  in the callback method is:

.. code-block:: python

   def edit_varname(*args):
      value = app.gui.getvar("vargroup", "varname")

Alternatively, you can also use:

.. code-block:: python

   def edit_varname(*args):
      value = app.gui.variables["vargroup"]["varname"]["value"]

The first input argument for a callback method is always the value of the variable of the UI element that executed the callback method.
Within a callback method, you may therefore also use:

.. code-block:: python

   def edit_varname(*args):
      value = args[0]
