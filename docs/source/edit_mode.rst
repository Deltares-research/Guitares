Edit Mode
=========

Guitares includes an interactive **edit mode** for repositioning, resizing, and adding
widgets at runtime. Edit mode is only available when running under a debugger
(e.g. VS Code with debugpy, PyCharm, or ``pdb``).

When active, every widget gets a blue dashed overlay that can be dragged to
reposition and resized from the corners. Changes can be saved back to the
source YAML files.

Activating edit mode
--------------------

Edit mode is automatically installed when Guitares detects a debugger. A console
message is printed at startup::

    Edit Mode  |  Ctrl+E toggle  |  Ctrl+A add  |  Ctrl+Z undo  |  Ctrl+S save

Press **Ctrl+E** to toggle edit mode on and off. When activated, a fading overlay
message is shown with the available shortcuts.

Keyboard shortcuts
------------------

All shortcuts are only active while edit mode is enabled (after pressing Ctrl+E):

.. list-table::
   :header-rows: 1
   :widths: 20 80

   * - Shortcut
     - Action
   * - **Ctrl+E**
     - Toggle edit mode on/off
   * - **Ctrl+A**
     - Add a new element (opens property dialog, then click to place)
   * - **Ctrl+Z**
     - Undo all position/size changes since the last save
   * - **Ctrl+S**
     - Save modified positions back to source YAML files

Moving and resizing widgets
---------------------------

When edit mode is active:

* **Drag** anywhere on a widget overlay to move it. Positions snap to a 5-pixel grid.
* **Drag a corner handle** to resize the widget. A minimum size of 10×10 pixels is enforced.
* A small label in the top-right corner of each overlay shows the current YAML position
  and size as ``(x, y) width×height``.

Editing widget properties
-------------------------

**Double-click** on a widget overlay to open the property editor popup. This allows you
to edit:

* **Position** — X, Y (from bottom of parent), Width, Height
* **Text** — the label text shown next to or on the widget
* **Text Position** — where the label appears relative to the widget
  (only for styles that have separate labels: edit, popupmenu, listbox, slider, spinbox,
  tableview, table)
* **Tooltip** — the hover tooltip text

The popup also displays read-only information:

* **Style** — the widget type (e.g. ``edit``, ``pushbutton``)
* **Source** — the full path to the YAML file that defines this widget
* **Variable** — the bound variable group and name

After clicking OK, only the properties that actually changed are applied.
Clicking Cancel discards all changes.

Adding new elements
-------------------

Press **Ctrl+A** to add a new widget:

1. A dialog opens where you configure the new element:

   * **Style** — choose from: edit, text, pushbutton, checkbox, popupmenu, slider, spinbox
   * **Text** — the label text
   * **Text Position** — label placement (left, above, above-left, above-center, right)
   * **Tooltip** — hover text
   * **Variable** — the variable name (defaults to ``dummy``)
   * **Width** and **Height** — initial size in logical pixels

2. After clicking OK, the cursor changes to a crosshair. Click anywhere in the GUI
   to place the element at that position.

   * **Left-click** places the element
   * **Right-click** or **Escape** cancels placement

3. The new element is created with the parent determined automatically from where you
   clicked (the deepest tab panel tab, panel, or the main window).

4. A dummy GUI variable is created if the specified variable does not exist yet.

5. The new element gets a drag overlay immediately, so you can reposition and resize it
   right away.

Saving changes
--------------

Press **Ctrl+S** to write all modifications back to the source YAML files.

* Existing elements are matched by style + variable name (or text for pushbuttons).
* New elements are appended to the correct location in the YAML structure
  (inside the appropriate tab or at the top level).
* After saving, the undo snapshot is updated so that Ctrl+Z reverts to the last
  saved state.

.. note::

   Only position, size, text, tooltip, and text_position changes are saved. Other
   properties (module, method, dependencies, etc.) must be edited in the YAML
   file directly.

Coordinate system
-----------------

Guitares uses a **bottom-up Y coordinate** system in YAML:

* ``x`` is the distance from the **left** edge of the parent
* ``y`` is the distance from the **bottom** edge of the parent

This is converted to Qt's top-down coordinates internally by ``get_position()``.
Negative values for position or size are interpreted as offsets from the right/bottom
edge of the parent.

Limitations
-----------

* Edit mode is only available with the **PySide6** framework, not PyQt5.
* Container widgets (tabpanel, panel, map, webpage, radiobuttongroup) cannot be
  dragged or resized — only their child widgets can.
* The debugger check uses ``sys.gettrace()`` and the ``debugpy``/``pydevd`` module
  names. If your debugger is not detected, edit mode will not be available.
