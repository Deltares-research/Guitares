Elements
========

Edit box
--------

.. list-table:: style: edit
   :widths: 50 10 15 50
   :header-rows: 1

   * - Key
     - Type
     - Default
     - Description

   * - **position["x"]**
     - int
     - 
     - x-position of lower-left corner (in pixels)

   * - **position["y"]**
     - int
     - 
     - y-position of lower-left corner (in pixels)

   * - **position["width"]**
     - int
     - 
     - width (in pixels)

   * - **position["height"]**
     - int
     - 
     - height (in pixels)

   * - **variable**
     - int, str or float
     - 
     - variable name

   * - variable_group
     - str
     - inherited
     - variable group name

   * - module
     - str
     - inherited
     - callback module

   * - method
     - str
     - 
     - callback method

   * - text
     - str or dict
     - 
     - text label

   * - text["variable"]
     - str
     - 
     - text label from variable

   * - text["variable_group"]
     - str
     - inherited
     - text label variable group

   * - text_position
     - str
     - left
     - text label position

.. code-block:: python

   element = {style: "edit",
              position: {x: 10, y: 20, width: 80, height: 20},
              variable: "x0",
              variable_group: "main",
              module: "callbacks":
              method: "edit_x0",
              text: "x0",
              text_position: "left"}

     
Text
----

Push button
-----------

Pop-up menu
-----------

List box
----------

Slider
------

Tab panel
---------

Frame
-----
