Using Style Sheets
==================

Guitares supports Qt Style Sheets (QSS) for customizing the appearance of the application.
QSS is a CSS-like language that controls colors, fonts, borders, padding, and other visual
properties of Qt widgets.

Applying a stylesheet
---------------------

Place a ``.qss`` file in your application directory and reference it from ``app.py``:

.. code-block:: python

   class Application:
       def __init__(self):
           self.gui = GUI(self, config_file="myapp.yml",
                          stylesheet="Combinear.qss")

The path is relative to the config file location.

Example stylesheet
------------------

The ``Combinear.qss`` file included with several Guitares examples gives the application
a modern dark-panel look.
Here is a simplified version showing the most common customizations:

.. code-block:: css

   /* Main window and panels */
   QMainWindow, QFrame, QDialog {
       background-color: #2b2b2b;
       color: #cccccc;
   }

   /* Push buttons */
   QPushButton {
       background-color: #3c3c3c;
       color: #ffffff;
       border: 1px solid #555555;
       border-radius: 3px;
       padding: 4px 10px;
   }
   QPushButton:hover {
       background-color: #4a4a4a;
   }
   QPushButton:pressed {
       background-color: #2a5a8a;
   }
   QPushButton:disabled {
       color: #666666;
   }

   /* Edit boxes */
   QLineEdit {
       background-color: #1e1e1e;
       color: #cccccc;
       border: 1px solid #555555;
       border-radius: 2px;
       padding: 2px;
   }

   /* Dropdowns */
   QComboBox {
       background-color: #3c3c3c;
       color: #cccccc;
       border: 1px solid #555555;
   }

   /* Tab panels */
   QTabWidget::pane {
       border: 1px solid #555555;
   }
   QTabBar::tab {
       background-color: #3c3c3c;
       color: #aaaaaa;
       padding: 4px 12px;
   }
   QTabBar::tab:selected {
       background-color: #2a5a8a;
       color: #ffffff;
   }

Widget selectors
----------------

QSS uses the Qt widget class name as the selector. The most commonly styled widgets in
Guitares applications are:

.. list-table::
   :widths: 30 70
   :header-rows: 1

   * - QSS selector
     - Guitares element
   * - ``QPushButton``
     - Push button, file chooser buttons
   * - ``QLineEdit``
     - Edit box
   * - ``QSpinBox``, ``QDoubleSpinBox``
     - Spin box
   * - ``QComboBox``
     - Pop-up menu
   * - ``QListWidget``
     - List box
   * - ``QCheckBox``
     - Check box
   * - ``QSlider``
     - Slider
   * - ``QTabWidget``, ``QTabBar``
     - Tab panel
   * - ``QFrame``
     - Panel / frame
   * - ``QLabel``
     - Text and element labels
   * - ``QTableView``
     - Table view
   * - ``QDateTimeEdit``
     - Date/time edit

Using ID and class selectors
-----------------------------

You can target specific widgets by their Qt object name if you set the ``id`` key in the YAML:

.. code-block:: yaml

   - style: pushbutton
     id: run_button
     text: Run

.. code-block:: css

   QPushButton#run_button {
       background-color: #2a6a2a;
       font-weight: bold;
   }

Further reading
---------------

For a complete reference on Qt Style Sheets syntax and properties, see the
`Qt documentation on stylesheets <https://doc.qt.io/qt-6/stylesheet.html>`_.
