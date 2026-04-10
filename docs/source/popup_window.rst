Popup windows
=============

Guitares supports **modal popup windows** — secondary dialogs that collect data from the user
before returning control to the main application.

A popup has the same YAML structure as the main window and can contain any standard element.
Guitares automatically adds **OK** and **Cancel** buttons at the bottom.

Creating a popup config
-----------------------

A popup config file looks like any other Guitares config, but the ``window`` section uses
``okay_method`` to define a callback that runs when OK is clicked:

.. code-block:: yaml

   # popup_settings.yml
   window:
     title: Edit Settings
     width: 300
     height: 120
     module: popup_callbacks
     variable_group: popup
     okay_method: on_okay

   element:
   - style: edit
     position: {x: 100, y: 70, width: 150, height: 24}
     variable: name
     text: Name
     method: edit_name

   - style: spinbox
     position: {x: 100, y: 40, width: 150, height: 24}
     variable: value
     minimum: 0
     maximum: 1000
     suffix: " m"
     text: Value

Opening a popup from a callback
--------------------------------

Call ``app.gui.popup()`` from any callback to open the dialog:

.. code-block:: python

   # main_callbacks.py
   from app import app

   def open_settings(*args):
       # Pack current values into a data dict
       data = {
           "name": app.gui.getvar("myapp", "name"),
           "value": app.gui.getvar("myapp", "value"),
       }

       okay, result = app.gui.popup("popup_settings.yml", "settings", data)

       if okay:
           app.gui.setvar("myapp", "name", result["name"])
           app.gui.setvar("myapp", "value", result["value"])

The ``popup()`` call blocks until the user clicks OK or Cancel.

* If OK is clicked, it returns ``(True, data)`` where ``data`` contains the updated values.
* If Cancel is clicked, it returns ``(False, data)`` with the original values unchanged.

The popup callback module
--------------------------

Callbacks inside the popup work the same way as in the main window.
The ``okay_method`` is called when the user clicks OK — it can perform validation and
return ``False`` to keep the popup open:

.. code-block:: python

   # popup_callbacks.py
   from app import app

   def edit_name(*args):
       pass  # variable is updated automatically

   def on_okay(*args):
       name = app.gui.getvar("popup", "name")
       if not name:
           # Keep the popup open if the name is empty
           return False
       return True

Popup data flow
---------------

Data is passed into and out of a popup through the ``data`` dict argument.
Guitares maps the dict keys to variable names in the popup's ``variable_group``:

1. Before the popup opens, values from ``data`` are written to popup variables.
2. The user edits values through the popup elements.
3. When OK is clicked, popup variable values are written back to ``data``.
4. ``app.gui.popup()`` returns the updated ``data`` dict.

This means the keys of your ``data`` dict should match the variable names used in
the popup's YAML config.
