Positioning elements
====================

Every element requires a ``position`` key that controls its placement within its parent container
(either the main window or a frame/panel).

Coordinate system
-----------------

Guitares uses a **bottom-left origin** coordinate system: ``x`` increases to the right and ``y``
increases upward from the bottom of the parent container.

.. code-block:: yaml

   position:
     x: 100      # pixels from left edge of parent
     y: 40       # pixels from bottom edge of parent
     width: 200  # element width in pixels
     height: 24  # element height in pixels

Absolute vs. relative coordinates
----------------------------------

Both position and size values can be either **absolute** (positive) or **relative to the opposite
edge** (negative or zero). This allows elements to stretch with the window without hard-coding
pixel positions.

.. list-table::
   :widths: 20 80
   :header-rows: 1

   * - Value
     - Meaning
   * - Positive ``x``
     - Distance in pixels from the **left** edge of the parent
   * - Negative ``x``
     - Distance in pixels from the **right** edge of the parent
   * - Positive ``y``
     - Distance in pixels from the **bottom** edge of the parent
   * - Negative ``y``
     - Distance in pixels from the **top** edge of the parent
   * - Positive ``width``
     - Fixed width in pixels
   * - Negative ``width``
     - Width = parent width − ``x`` + ``width`` (i.e., stretch to right edge with a margin)
   * - Positive ``height``
     - Fixed height in pixels
   * - Negative ``height``
     - Height = parent height − ``y`` + ``height`` (i.e., stretch to top edge with a margin)

Examples
--------

**Fixed position and size** — element starts 10 px from the left and 10 px from the bottom,
with a fixed size of 200 × 24 px:

.. code-block:: yaml

   position: {x: 10, y: 10, width: 200, height: 24}

**Stretch to fill width** — element starts 10 px from the left and fills to 10 px from the right:

.. code-block:: yaml

   position: {x: 10, y: 10, width: -10, height: 24}

**Fill the parent entirely** (with 5 px margins on all sides):

.. code-block:: yaml

   position: {x: 5, y: 5, width: -5, height: -5}

**Anchor to the top-right corner** — a 100 × 24 element placed 10 px from the right and 10 px
from the top:

.. code-block:: yaml

   position: {x: -110, y: -34, width: 100, height: 24}

High-DPI screens
----------------

Guitares applies a ``resize_factor`` (set when creating the ``GUI`` object) to all pixel values
at runtime. This means that the values in the YAML file are always specified in **logical pixels**
at a 1× scale, regardless of the actual screen resolution.
