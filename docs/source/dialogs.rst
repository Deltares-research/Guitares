Dialogs
=======

Guitares provides a set of built-in dialog methods on the ``Window`` object. These are
convenience wrappers around Qt dialog classes that handle styling and return values
consistently.

All dialog methods are called on the window object, for example:

.. code-block:: python

   app.gui.window.dialog_warning("Something went wrong!")

Message dialogs
---------------

dialog_ok_cancel
^^^^^^^^^^^^^^^^

Show a question dialog with OK and Cancel buttons.

.. code-block:: python

   result = app.gui.window.dialog_ok_cancel("Are you sure?", title="Confirm")

Returns the dialog result (truthy if OK was clicked).

dialog_yes_no
^^^^^^^^^^^^^

Show a question dialog with Yes and No buttons.

.. code-block:: python

   result = app.gui.window.dialog_yes_no("Do you want to continue?")

Returns the dialog result (truthy if Yes was clicked).

dialog_custom
^^^^^^^^^^^^^

Show a dialog with custom button labels.

.. code-block:: python

   result = app.gui.window.dialog_custom(
       "Choose an action",
       title="Action",
       button_text=["Save", "Discard", "Cancel"],
   )

Returns the dialog result corresponding to the clicked button.

dialog_warning
^^^^^^^^^^^^^^

Show a warning message box.

.. code-block:: python

   app.gui.window.dialog_warning("File not found!", title="Warning")

dialog_info
^^^^^^^^^^^

Show an informational message box.

.. code-block:: python

   app.gui.window.dialog_info("Operation completed successfully.")

dialog_critical
^^^^^^^^^^^^^^^

Show a critical error message box.

.. code-block:: python

   app.gui.window.dialog_critical("Fatal error: cannot open database.", title="Error")

Timed dialogs
-------------

dialog_auto_close
^^^^^^^^^^^^^^^^^

Show a dialog that closes automatically after a timeout.

.. code-block:: python

   app.gui.window.dialog_auto_close("Saving...", timeout=2000)

Parameters:

* ``text`` — message to display
* ``timeout`` — auto-close delay in milliseconds (default: 1500)

dialog_fade_label
^^^^^^^^^^^^^^^^^

Show a non-blocking overlay label that fades in, pauses, then fades out and
self-destructs. Unlike other dialogs, this does **not** block the event loop.

.. code-block:: python

   app.gui.window.dialog_fade_label("Settings saved!", timeout=3000)

Parameters:

* ``text`` — message to display
* ``timeout`` — display duration in milliseconds before the fade-out starts (default: 1500)

Progress dialogs
----------------

dialog_progress
^^^^^^^^^^^^^^^

Show a progress dialog with a progress bar.

.. code-block:: python

   dlg = app.gui.window.dialog_progress("Processing...", nmax=100, title="Progress")

   for i in range(100):
       # ... do work ...
       dlg.setValue(i + 1)

   dlg.close()

Parameters:

* ``text`` — progress message
* ``nmax`` — maximum progress value
* ``title`` — dialog title

Returns the progress dialog object.

dialog_wait
^^^^^^^^^^^

Show a busy/wait dialog (no progress bar, just a message).

.. code-block:: python

   dlg = app.gui.window.dialog_wait("Please wait...")
   # ... do work ...
   dlg.close()

Returns the wait dialog object.

Input dialogs
-------------

dialog_string
^^^^^^^^^^^^^

Show a text-input dialog that returns the entered string.

.. code-block:: python

   result = app.gui.window.dialog_string("Enter your name:", title="Name")
   if result is not None:
       print(f"Hello, {result}!")

Returns the entered string, or ``None`` on cancel.

dialog_popupmenu
^^^^^^^^^^^^^^^^

Show a popup-menu selection dialog.

.. code-block:: python

   result = app.gui.window.dialog_popupmenu(
       "Choose a color:",
       title="Color",
       options=["Red", "Green", "Blue"],
   )

Returns the selected option.

File and directory dialogs
--------------------------

dialog_open_file
^^^^^^^^^^^^^^^^

Show a file-open dialog.

.. code-block:: python

   full_name, path, name, ext, fltr = app.gui.window.dialog_open_file(
       "Select a file",
       filter="Text Files (*.txt);;All Files (*.*)",
       path="/home/user/documents",
   )

   if full_name:
       print(f"Selected: {full_name}")

Parameters:

* ``text`` — dialog prompt
* ``filter`` — file filter string (e.g. ``"CSV (*.csv);;All (*.*)"``)
* ``path`` — initial directory (defaults to current working directory)
* ``file_name`` — pre-filled file name
* ``selected_filter`` — pre-selected filter
* ``allow_directory_change`` — if ``False``, reject files from other directories
* ``multiple`` — allow selecting multiple files

Returns ``(full_name, path, name, extension, filter)`` or all empty strings on cancel.

dialog_save_file
^^^^^^^^^^^^^^^^

Show a file-save dialog. Same parameters and return value as ``dialog_open_file``
(except no ``multiple`` parameter).

.. code-block:: python

   full_name, path, name, ext, fltr = app.gui.window.dialog_save_file(
       "Save as",
       filter="JSON (*.json);;All (*.*)",
   )

dialog_select_path
^^^^^^^^^^^^^^^^^^

Show a directory selection dialog.

.. code-block:: python

   selected_dir = app.gui.window.dialog_select_path(
       "Choose output directory",
       path="/home/user",
   )

   if selected_dir:
       print(f"Directory: {selected_dir}")

Returns the selected directory path, or ``None`` on cancel.
