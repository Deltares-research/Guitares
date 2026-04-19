"""GUI edit mode for dragging and repositioning widgets.

Activated with Ctrl+E (toggle) and saved with Ctrl+S when in edit mode.
Only available when running under a debugger (sys.gettrace() is not None).

Widgets can be dragged to new positions (snapped to a 5px grid).
Modified positions are written back to the source YAML files.
"""

import logging
import sys
from typing import Any, Dict, List, Optional, Tuple

import yaml
from PySide6 import QtCore, QtGui
from PySide6.QtCore import QPoint, QRect, Qt
from PySide6.QtWidgets import QApplication, QWidget

SNAP = 5  # Grid snap in pixels
logger = logging.getLogger(__name__)


def is_debug() -> bool:
    """Check if a debugger is attached (works with VS Code debugpy, PyCharm, pdb)."""
    # Check for debugpy (VS Code)
    if "debugpy" in sys.modules:
        return True
    # Check for pydevd (PyCharm / VS Code internal)
    if "pydevd" in sys.modules:
        return True
    # Fallback: trace function set
    if sys.gettrace() is not None:
        return True
    return False


HANDLE = 6  # Resize handle size in pixels


class DragOverlay(QWidget):
    """Transparent overlay that shows a draggable handle over a widget.

    Draws a blue border around the widget and allows dragging to reposition.
    Corners can be dragged to resize.
    """

    def __init__(self, element: Any, parent: QWidget) -> None:
        super().__init__(parent)
        self.element = element
        self.widget = element.widget
        self.resize_factor = element.gui.resize_factor
        self._dragging = False
        self._resizing = False
        self._resize_corner = None  # 'tl', 'tr', 'bl', 'br'
        self._drag_offset = QPoint()
        self._original_pos = QPoint()
        self._modified = False
        self._original_text = element.text if isinstance(element.text, str) else None

        # Match the widget's geometry
        self.sync_geometry()

        self.setMouseTracking(True)
        self.setCursor(Qt.SizeAllCursor)
        self.show()
        self.raise_()

    def sync_geometry(self) -> None:
        """Match overlay geometry to the target widget."""
        if self.widget:
            self.setGeometry(self.widget.geometry())

    def _corner_rects(self) -> Dict[str, QRect]:
        """Return rectangles for the four resize handles."""
        h = HANDLE
        w, ht = self.width(), self.height()
        return {
            "tl": QRect(0, 0, h, h),
            "tr": QRect(w - h, 0, h, h),
            "bl": QRect(0, ht - h, h, h),
            "br": QRect(w - h, ht - h, h, h),
        }

    def _hit_corner(self, pos: QPoint) -> Optional[str]:
        """Return which corner handle is hit, or None."""
        for name, rect in self._corner_rects().items():
            if rect.contains(pos):
                return name
        return None

    def paintEvent(self, event: Any) -> None:
        """Draw a blue dashed border with resize handles."""
        painter = QtGui.QPainter(self)
        pen = QtGui.QPen(QtGui.QColor(30, 115, 232), 2, Qt.DashLine)
        painter.setPen(pen)
        painter.drawRect(1, 1, self.width() - 2, self.height() - 2)

        # Draw resize handles
        painter.setBrush(QtGui.QColor(30, 115, 232))
        painter.setPen(Qt.NoPen)
        for rect in self._corner_rects().values():
            painter.drawRect(rect)

        # Draw position + size label (top-right, inside overlay)
        ep = self.element.position
        label = f"({ep.x},{ep.y}) {ep.width}x{ep.height}"
        font = QtGui.QFont("Arial", 6)
        painter.setFont(font)
        fm = QtGui.QFontMetrics(font)
        tw = fm.horizontalAdvance(label) + 4
        th = fm.height() + 2
        lx = max(self.width() - tw - 2, 2)
        painter.setBrush(QtGui.QColor(0, 0, 0, 180))
        painter.setPen(Qt.NoPen)
        painter.drawRect(lx, 2, tw, th)
        painter.setPen(QtGui.QColor(255, 255, 255))
        painter.drawText(lx + 2, th, label)
        painter.end()

    def mousePressEvent(self, event: Any) -> None:
        """Start drag or resize."""
        if event.button() == Qt.LeftButton:
            corner = self._hit_corner(event.pos())
            if corner:
                self._resizing = True
                self._resize_corner = corner
                self._drag_offset = event.pos()
                self._original_pos = self.pos()
                self._original_size = self.size()
            else:
                self._dragging = True
                self._drag_offset = event.pos()
                self._original_pos = self.pos()

    def mouseMoveEvent(self, event: Any) -> None:
        """Move or resize widget (snapped to grid)."""
        if self._dragging:
            new_pos = self.mapToParent(event.pos()) - self._drag_offset
            rf = self.resize_factor
            snap_pixels = SNAP * rf
            new_x = round(new_pos.x() / snap_pixels) * snap_pixels
            new_y = round(new_pos.y() / snap_pixels) * snap_pixels
            self.move(int(new_x), int(new_y))
            parent_h = self.parent().height() if self.parent() else 0
            self.element.position.x = round(new_x / rf / SNAP) * SNAP
            self.element.position.y = (
                round((parent_h - new_y - self.height()) / rf / SNAP) * SNAP
            )
            self.element.set_geometry()

        elif self._resizing:
            rf = self.resize_factor
            snap_pixels = SNAP * rf
            dx = event.pos().x() - self._drag_offset.x()
            dy = event.pos().y() - self._drag_offset.y()
            geo = QRect(self._original_pos, self._original_size)
            c = self._resize_corner

            if "r" in c:
                geo.setRight(int(round((geo.right() + dx) / snap_pixels) * snap_pixels))
            if "l" in c:
                new_left = int(round((geo.left() + dx) / snap_pixels) * snap_pixels)
                geo.setLeft(new_left)
            if "b" in c:
                geo.setBottom(
                    int(round((geo.bottom() + dy) / snap_pixels) * snap_pixels)
                )
            if "t" in c:
                new_top = int(round((geo.top() + dy) / snap_pixels) * snap_pixels)
                geo.setTop(new_top)

            # Minimum size
            if geo.width() < int(SNAP * rf * 2):
                return
            if geo.height() < int(SNAP * rf * 2):
                return

            self.setGeometry(geo)

            parent_h = self.parent().height() if self.parent() else 0
            self.element.position.x = round(geo.x() / rf / SNAP) * SNAP
            self.element.position.y = (
                round((parent_h - geo.y() - geo.height()) / rf / SNAP) * SNAP
            )
            self.element.position.width = round(geo.width() / rf / SNAP) * SNAP
            self.element.position.height = round(geo.height() / rf / SNAP) * SNAP
            self.element.set_geometry()

        else:
            # Update cursor based on hover over corners
            corner = self._hit_corner(event.pos())
            if corner in ("tl", "br"):
                self.setCursor(Qt.SizeFDiagCursor)
            elif corner in ("tr", "bl"):
                self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.SizeAllCursor)

    def mouseReleaseEvent(self, event: Any) -> None:
        """End drag or resize."""
        if event.button() == Qt.LeftButton:
            if self._dragging and self.pos() != self._original_pos:
                self._modified = True
            if self._resizing:
                self._modified = True
            self._dragging = False
            self._resizing = False
            self._resize_corner = None
            self.update()

    def mouseDoubleClickEvent(self, event: Any) -> None:
        """Open property editor popup on double-click."""
        if event.button() == Qt.LeftButton:
            _open_property_editor(self)


class EditMode:
    """Manages the GUI edit mode for repositioning widgets.

    Parameters
    ----------
    gui : Any
        The guitares GUI object.
    """

    def __init__(self, gui: Any) -> None:
        self.gui = gui
        self.active = False
        self.overlays: List[DragOverlay] = []
        self._saved_positions: Dict[int, Tuple[int, int]] = {}  # id(element) → (x, y)
        self._shortcut_toggle: Optional[QtGui.QShortcut] = None
        self._shortcut_save: Optional[QtGui.QShortcut] = None
        self._shortcut_undo: Optional[QtGui.QShortcut] = None
        self._shortcut_add: Optional[QtGui.QShortcut] = None
        self._main_window: Optional[QWidget] = None
        self._placement_filter: Optional[Any] = None

    def install(self, main_window: QWidget) -> None:
        """Install keyboard shortcuts on the main window.

        Parameters
        ----------
        main_window : QWidget
            The application's main window widget.
        """
        self._shortcut_toggle = QtGui.QShortcut(
            QtGui.QKeySequence("Ctrl+E"), main_window
        )
        self._shortcut_toggle.activated.connect(self.toggle)

        self._shortcut_save = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+S"), main_window)
        self._shortcut_save.activated.connect(self.save)

        self._shortcut_undo = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+Z"), main_window)
        self._shortcut_undo.activated.connect(self.undo)

        self._shortcut_add = QtGui.QShortcut(QtGui.QKeySequence("Ctrl+A"), main_window)
        self._shortcut_add.activated.connect(self.add_element)
        self._main_window = main_window

    def toggle(self) -> None:
        """Toggle edit mode on/off."""
        if self.active:
            self.deactivate()
        else:
            self.activate()

    def activate(self) -> None:
        """Enter edit mode — create drag overlays on all widgets."""
        if self.active:
            return
        self.active = True
        logger.info(
            "=== EDIT MODE ON (Ctrl+E exit, Ctrl+S save, Ctrl+Z undo, Ctrl+A add) ==="
        )
        self.gui.window.dialog_fade_label(
            "Edit Mode  |  Ctrl+E toggle  |  Ctrl+A add  |  Ctrl+Z undo  |  Ctrl+S save",
            timeout=5000,
        )

        # Walk all elements and create overlays
        self._create_overlays(self.gui.window.elements)

        # Snapshot positions for undo
        self._snapshot_positions()

    def undo(self) -> None:
        """Revert all positions and sizes to the last snapshot."""
        if not self.active:
            return
        restored = 0
        for overlay in self.overlays:
            eid = id(overlay.element)
            if eid in self._saved_positions:
                old_x, old_y, old_w, old_h = self._saved_positions[eid]
                overlay.element.position.x = old_x
                overlay.element.position.y = old_y
                overlay.element.position.width = old_w
                overlay.element.position.height = old_h
                overlay.element.set_geometry()
                overlay.sync_geometry()
                overlay._modified = False
                overlay.update()
                restored += 1
        logger.info(f"Undo: restored {restored} widget(s)")

    def _snapshot_positions(self) -> None:
        """Store current positions and sizes of all overlaid elements."""
        self._saved_positions.clear()
        for overlay in self.overlays:
            el = overlay.element
            self._saved_positions[id(el)] = (
                el.position.x,
                el.position.y,
                el.position.width,
                el.position.height,
            )
        logger.info(f"  Snapshot: {len(self._saved_positions)} widget positions saved")

    def deactivate(self) -> None:
        """Exit edit mode — remove all overlays."""
        if not self.active:
            return
        self.active = False
        logger.info("=== EDIT MODE OFF ===")

        # Check for unsaved changes
        modified = [o for o in self.overlays if o._modified]
        if modified:
            logger.info(f"  {len(modified)} widget(s) were moved. Ctrl+S to save.")

        for overlay in self.overlays:
            overlay.hide()
            overlay.deleteLater()
        self.overlays.clear()

    def save(self) -> None:
        """Save modified widget positions back to YAML files."""
        if not self.active:
            return

        modified = [o for o in self.overlays if o._modified]
        if not modified:
            logger.info("No changes to save.")
            return

        # Group modifications by source YAML file
        by_file: Dict[str, List[DragOverlay]] = {}
        for overlay in modified:
            source = getattr(overlay.element, "_source_yml", None)
            if source:
                by_file.setdefault(source, []).append(overlay)
            else:
                logger.info(
                    f"  Warning: no source YAML for {overlay.element.style} — skipping"
                )

        for yml_path, overlays in by_file.items():
            try:
                _update_yaml_positions(yml_path, overlays)
                logger.info(f"  Saved {len(overlays)} change(s) to {yml_path}")
                for o in overlays:
                    o._modified = False
                    # Update original text so next save matches the new text
                    if isinstance(o.element.text, str):
                        o._original_text = o.element.text
            except Exception as e:
                logger.info(f"  Error saving {yml_path}: {e}")

        # Re-snapshot so undo reverts to the last saved state
        self._snapshot_positions()

    def _create_overlays(self, elements: List[Any]) -> None:
        """Recursively create drag overlays for all elements."""
        for element in elements:
            # Skip elements without a widget
            if not hasattr(element, "widget") or element.widget is None:
                continue

            # Skip certain widget types that are hard to drag
            skip_styles = {
                "tabpanel",
                "panel",
                "map",
                "mapbox",
                "mapbox_compare",
                "maplibre",
                "maplibre_compare",
                "webpage",
                "radiobuttongroup",
            }
            if element.style in skip_styles:
                pass  # Don't create overlay for containers, but recurse into children
            else:
                try:
                    # Check the widget has a geometry method (skip custom compound widgets)
                    if not hasattr(element.widget, "geometry"):
                        continue
                    parent = element.widget.parent()
                    if parent:
                        overlay = DragOverlay(element, parent)
                        self.overlays.append(overlay)
                except Exception:
                    pass  # Skip widgets that can't be overlaid

            # Recurse into tab panels
            if element.style == "tabpanel" and hasattr(element, "tabs"):
                for tab in element.tabs:
                    if hasattr(tab, "elements"):
                        self._create_overlays(tab.elements)
            # Recurse into panels
            if hasattr(element, "elements") and element.elements:
                self._create_overlays(element.elements)

    def add_element(self) -> None:
        """Prompt for element properties, then let user click to place it."""
        if not self.active:
            logger.info("Enter edit mode first (Ctrl+E).")
            return

        gui = self.gui
        group = "_edit_mode_add"

        # Available styles for new elements
        style_options = [
            "edit",
            "text",
            "pushbutton",
            "checkbox",
            "popupmenu",
            "slider",
            "spinbox",
        ]
        text_pos_options = ["left", "above", "above-left", "above-center", "right"]

        gui.setvar(group, "style", "edit")
        gui.setvar(group, "style_options", style_options)
        gui.setvar(group, "text", "Label")
        gui.setvar(group, "text_position", "left")
        gui.setvar(group, "text_pos_options", text_pos_options)
        gui.setvar(group, "tooltip", "")
        gui.setvar(group, "variable", "dummy")
        gui.setvar(group, "width", 60)
        gui.setvar(group, "height", 20)

        win_width = 350
        win_height = 380
        fw = win_width - 30

        config = {
            "window": {
                "title": "Add Element",
                "width": win_width,
                "height": win_height,
                "variable_group": group,
            },
            "menu": [],
            "element": [
                {
                    "style": "popupmenu",
                    "variable": "style",
                    "text": "Style",
                    "text_position": "above-left",
                    "select": "item",
                    "option_string": style_options,
                    "option_value": style_options,
                    "position": {
                        "x": 15,
                        "y": win_height - 55,
                        "width": 140,
                        "height": 20,
                    },
                },
                {
                    "style": "edit",
                    "variable": "text",
                    "text": "Text",
                    "text_position": "above-left",
                    "position": {
                        "x": 15,
                        "y": win_height - 110,
                        "width": fw,
                        "height": 20,
                    },
                },
                {
                    "style": "popupmenu",
                    "variable": "text_position",
                    "text": "Text Position",
                    "text_position": "above-left",
                    "select": "item",
                    "option_string": text_pos_options,
                    "option_value": text_pos_options,
                    "position": {
                        "x": 15,
                        "y": win_height - 165,
                        "width": 140,
                        "height": 20,
                    },
                },
                {
                    "style": "edit",
                    "variable": "tooltip",
                    "text": "Tooltip",
                    "text_position": "above-left",
                    "position": {
                        "x": 15,
                        "y": win_height - 220,
                        "width": fw,
                        "height": 20,
                    },
                },
                {
                    "style": "edit",
                    "variable": "variable",
                    "text": "Variable",
                    "text_position": "above-left",
                    "position": {
                        "x": 15,
                        "y": win_height - 275,
                        "width": 200,
                        "height": 20,
                    },
                },
                {
                    "style": "edit",
                    "variable": "width",
                    "text": "Width",
                    "type": "int",
                    "text_position": "above-center",
                    "position": {
                        "x": 230,
                        "y": win_height - 275,
                        "width": 50,
                        "height": 20,
                    },
                },
                {
                    "style": "edit",
                    "variable": "height",
                    "text": "Height",
                    "type": "int",
                    "text_position": "above-center",
                    "position": {
                        "x": 285,
                        "y": win_height - 275,
                        "width": 50,
                        "height": 20,
                    },
                },
            ],
        }

        okay, _ = gui.popup(config, id="edit_mode_add_element")
        if not okay:
            return

        # Collect values
        new_cfg = {
            "style": gui.getvar(group, "style"),
            "text": gui.getvar(group, "text"),
            "text_position": gui.getvar(group, "text_position"),
            "tooltip": gui.getvar(group, "tooltip"),
            "variable": gui.getvar(group, "variable"),
            "width": int(gui.getvar(group, "width")),
            "height": int(gui.getvar(group, "height")),
        }

        # Enter placement mode
        logger.info("Click in the GUI to place the element (Esc to cancel)...")
        QApplication.setOverrideCursor(Qt.CrossCursor)

        # Make overlays transparent to mouse events during placement
        for o in self.overlays:
            o.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, True)

        self._placement_filter = _ClickPlacementFilter(self, new_cfg)
        self._main_window.installEventFilter(self._placement_filter)


class _ClickPlacementFilter(QtCore.QObject):
    """Event filter that captures a single click for element placement."""

    def __init__(self, edit_mode: EditMode, element_config: dict) -> None:
        super().__init__()
        self.edit_mode = edit_mode
        self.element_config = element_config

    def eventFilter(self, obj: Any, event: Any) -> bool:
        if event.type() == QtCore.QEvent.Type.MouseButtonPress:
            if event.button() == Qt.LeftButton:
                global_pos = event.globalPosition().toPoint()
                self._finish(global_pos)
                return True
            elif event.button() == Qt.RightButton:
                self._cancel()
                return True
        elif event.type() == QtCore.QEvent.Type.KeyPress:
            if event.key() == Qt.Key_Escape:
                self._cancel()
                return True
        return False

    def _restore_overlays(self) -> None:
        """Restore overlay mouse interaction after placement mode."""
        for o in self.edit_mode.overlays:
            o.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)

    def _cancel(self) -> None:
        """Cancel placement mode."""
        self.edit_mode._main_window.removeEventFilter(self)
        QApplication.restoreOverrideCursor()
        # Restore overlay mouse interaction
        for o in self.edit_mode.overlays:
            o.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        logger.info("Add element cancelled.")

    def _finish(self, global_pos: QPoint) -> None:
        """Place the element at the clicked position."""
        self.edit_mode._main_window.removeEventFilter(self)
        QApplication.restoreOverrideCursor()

        gui = self.edit_mode.gui
        window = gui.window
        rf = gui.resize_factor

        # Find the guitares parent (Tab, panel Element, or Window)
        parent, parent_elements = _find_guitares_parent(window, global_pos)

        if parent is None:
            logger.info("Could not determine parent container.")
            self._restore_overlays()
            return

        # Convert global click position to parent-local coordinates
        local_pos = parent.widget.mapFromGlobal(global_pos)
        parent_h = parent.widget.geometry().height()

        # Convert Qt top-down y to YAML bottom-up y
        cfg = self.element_config
        snap = SNAP
        yaml_x = round((local_pos.x() / rf) / snap) * snap
        yaml_y = (
            round(((parent_h - local_pos.y() - cfg["height"] * rf) / rf) / snap) * snap
        )

        # Build the element dict
        el_dct = {
            "style": cfg["style"],
            "position": {
                "x": yaml_x,
                "y": yaml_y,
                "width": cfg["width"],
                "height": cfg["height"],
            },
            "variable": cfg["variable"],
            "text": cfg["text"],
            "text_position": cfg["text_position"],
        }
        if cfg["tooltip"]:
            el_dct["tooltip"] = cfg["tooltip"]

        # Ensure the variable exists in gui.variables
        var_group = parent.variable_group
        var_name = cfg["variable"]
        if gui.getvar(var_group, var_name) is None:
            # Create a default value based on style
            defaults = {
                "edit": "",
                "text": "",
                "pushbutton": "",
                "checkbox": False,
                "popupmenu": 0,
                "slider": 0,
                "spinbox": 0,
            }
            gui.setvar(var_group, var_name, defaults.get(cfg["style"], ""))

        # Determine _source_yml from siblings or parent chain
        source_yml = _find_source_yml(parent, parent_elements)

        # Create the Element object
        from guitares.element import Element

        element = Element(el_dct, parent, window)
        element._source_yml = source_yml
        element._is_new = True

        # Instantiate the widget
        element.add()
        element.widget.show()

        # Add to parent's element list
        parent_elements.append(element)

        # Restore overlay mouse interaction
        self._restore_overlays()

        # Create overlay for the new element
        qt_parent = element.widget.parent()
        if qt_parent:
            overlay = DragOverlay(element, qt_parent)
            overlay._modified = True  # Mark as needing save
            self.edit_mode.overlays.append(overlay)
            # Snapshot its position for undo
            self.edit_mode._saved_positions[id(element)] = (
                element.position.x,
                element.position.y,
                element.position.width,
                element.position.height,
            )

        style = cfg["style"]
        logger.info(f"Added {style} at ({yaml_x}, {yaml_y}) in {var_group}")


def _find_guitares_parent(window: Any, global_pos: QPoint) -> Tuple[Any, list]:
    """Find the deepest guitares container (Tab, panel, or Window) at a position.

    Returns (parent_object, parent_object.elements) or (None, []).
    """
    best_parent = None
    best_elements: list = []
    best_depth = -1

    def _walk(elements: list, depth: int) -> None:
        nonlocal best_parent, best_elements, best_depth
        for el in elements:
            if el.style == "tabpanel" and hasattr(el, "tabs"):
                # Check the active tab
                index = el.widget.currentIndex()
                if 0 <= index < len(el.tabs):
                    tab = el.tabs[index]
                    tab_widget = el.widget.widget(index)
                    if tab_widget and _widget_contains_global(tab_widget, global_pos):
                        if depth > best_depth:
                            best_parent = tab
                            best_elements = tab.elements
                            best_depth = depth
                        # Recurse into tab's elements
                        _walk(tab.elements, depth + 1)

            elif el.style == "panel":
                if el.widget and _widget_contains_global(el.widget, global_pos):
                    if depth > best_depth:
                        best_parent = el
                        best_elements = el.elements if el.elements else []
                        best_depth = depth
                    if el.elements:
                        _walk(el.elements, depth + 1)

    # Start: window itself is the fallback
    if _widget_contains_global(window.widget, global_pos):
        best_parent = window
        best_elements = window.elements
        best_depth = 0

    _walk(window.elements, 1)
    return best_parent, best_elements


def _widget_contains_global(widget: QWidget, global_pos: QPoint) -> bool:
    """Check if a widget's rect contains a global position."""
    local = widget.mapFromGlobal(global_pos)
    return widget.rect().contains(local)


def _find_source_yml(parent: Any, parent_elements: list) -> Optional[str]:
    """Find the source YAML file by checking siblings, then walking up the parent chain."""
    # First check siblings
    for sibling in parent_elements:
        src = getattr(sibling, "_source_yml", None)
        if src:
            return src
    # Walk up the parent chain
    node = parent
    while node is not None:
        src = getattr(node, "_source_yml", None)
        if src:
            return src
        # Check elements at this level
        elements = getattr(node, "elements", [])
        for el in elements:
            src = getattr(el, "_source_yml", None)
            if src:
                return src
        node = getattr(node, "parent", None)
    return None


def _open_property_editor(overlay: DragOverlay) -> None:
    """Open a popup to edit widget properties."""
    el = overlay.element
    gui = el.gui
    group = "_edit_mode_props"

    # Set current values as GUI variables
    gui.setvar(group, "pos_x", el.position.x)
    gui.setvar(group, "pos_y", el.position.y)
    gui.setvar(group, "width", el.position.width)
    gui.setvar(group, "height", el.position.height)
    gui.setvar(group, "text", el.text if isinstance(el.text, str) else "")
    gui.setvar(group, "tooltip", el.tooltip if isinstance(el.tooltip, str) else "")
    gui.setvar(group, "variable", el.variable or "")
    gui.setvar(group, "variable_group", el.variable_group or "")
    gui.setvar(group, "style", el.style)
    gui.setvar(group, "source_yml", getattr(el, "_source_yml", "") or "")

    # Text position options
    text_pos_options = ["above", "left", "right", "below"]
    text_pos = getattr(el, "text_position", "left")
    gui.setvar(group, "text_position", text_pos)
    gui.setvar(group, "text_position_options", text_pos_options)

    # Check if text_position dropdown is needed
    styles_with_text_position = {
        "edit",
        "popupmenu",
        "listbox",
        "slider",
        "spinbox",
        "tableview",
        "table",
    }
    show_text_pos = el.style in styles_with_text_position

    # Build popup config dict
    source_yml = getattr(el, "_source_yml", "") or "N/A"
    var_label = f"Variable: {el.variable_group}.{el.variable or ''}"
    win_width = 450
    win_height = 420 if show_text_pos else 380
    field_width = win_width - 30  # 15px margin each side

    elements = [
        # Header info
        {
            "style": "text",
            "text": f"Style: {el.style}",
            "position": {
                "x": 15,
                "y": win_height - 30,
                "width": field_width,
                "height": 20,
            },
        },
        {
            "style": "text",
            "text": f"Source: {source_yml}",
            "position": {
                "x": 15,
                "y": win_height - 50,
                "width": field_width,
                "height": 20,
            },
        },
        # Position row
        {
            "style": "edit",
            "variable": "pos_x",
            "text": "X",
            "type": "int",
            "text_position": "above-center",
            "position": {"x": 15, "y": win_height - 100, "width": 65, "height": 20},
        },
        {
            "style": "edit",
            "variable": "pos_y",
            "text": "Y",
            "type": "int",
            "text_position": "above-center",
            "position": {"x": 95, "y": win_height - 100, "width": 65, "height": 20},
        },
        {
            "style": "edit",
            "variable": "width",
            "text": "Width",
            "type": "int",
            "text_position": "above-center",
            "position": {"x": 175, "y": win_height - 100, "width": 65, "height": 20},
        },
        {
            "style": "edit",
            "variable": "height",
            "text": "Height",
            "type": "int",
            "text_position": "above-center",
            "position": {"x": 255, "y": win_height - 100, "width": 65, "height": 20},
        },
        # Text
        {
            "style": "edit",
            "variable": "text",
            "text": "Text",
            "text_position": "above-left",
            "position": {
                "x": 15,
                "y": win_height - 155,
                "width": field_width,
                "height": 20,
            },
        },
    ]

    # Text position dropdown (conditional)
    if show_text_pos:
        elements.append(
            {
                "style": "popupmenu",
                "variable": "text_position",
                "text": "Text Position",
                "text_position": "above-left",
                "select": "item",
                "option_string": text_pos_options,
                "option_value": text_pos_options,
                "position": {
                    "x": 15,
                    "y": win_height - 210,
                    "width": 140,
                    "height": 20,
                },
            },
        )
        tooltip_y = win_height - 265
    else:
        tooltip_y = win_height - 210

    elements.extend(
        [
            # Tooltip
            {
                "style": "edit",
                "variable": "tooltip",
                "text": "Tooltip",
                "text_position": "above-left",
                "position": {
                    "x": 15,
                    "y": tooltip_y,
                    "width": field_width,
                    "height": 20,
                },
            },
            # Variable info (read-only)
            {
                "style": "text",
                "text": var_label,
                "position": {"x": 15, "y": 55, "width": field_width, "height": 20},
            },
        ]
    )

    config = {
        "window": {
            "title": f"Edit: {el.style}",
            "width": win_width,
            "height": win_height,
            "variable_group": group,
        },
        "menu": [],
        "element": elements,
    }

    okay, data = gui.popup(config, id="edit_mode_property_editor")

    if okay:
        changed = False

        # Check position changes
        new_x = int(gui.getvar(group, "pos_x"))
        new_y = int(gui.getvar(group, "pos_y"))
        new_w = int(gui.getvar(group, "width"))
        new_h = int(gui.getvar(group, "height"))

        if (
            new_x != el.position.x
            or new_y != el.position.y
            or new_w != el.position.width
            or new_h != el.position.height
        ):
            el.position.x = new_x
            el.position.y = new_y
            el.position.width = new_w
            el.position.height = new_h
            el.set_geometry()
            changed = True

        new_text = gui.getvar(group, "text")
        if isinstance(el.text, str) and new_text != el.text:
            el.text = new_text
            # Update the label widget (text_widget), not the input widget itself
            if hasattr(el.widget, "text_widget"):
                el.widget.text_widget.setText(new_text)
            elif hasattr(el.widget, "setText"):
                # For pushbuttons and text labels, setText is correct
                el.widget.setText(new_text)
            # Recalculate geometry so the label resizes to fit the new text
            el.set_geometry()
            changed = True

        new_tooltip = gui.getvar(group, "tooltip")
        if isinstance(el.tooltip, str) and new_tooltip != el.tooltip:
            el.tooltip = new_tooltip
            if hasattr(el.widget, "setToolTip"):
                el.widget.setToolTip(new_tooltip)
            changed = True

        new_text_pos = gui.getvar(group, "text_position")
        if new_text_pos != text_pos:
            el.text_position = new_text_pos
            el.set_geometry()
            changed = True

        if changed:
            overlay._modified = True

        # Re-sync ALL overlays
        for o in overlay.element.gui.edit_mode.overlays:
            o.sync_geometry()
            o.update()


def _update_yaml_positions(yml_path: str, overlays: List[DragOverlay]) -> None:
    """Update widget positions in a YAML file.

    Reads the YAML, finds matching elements by style+variable,
    updates their positions, and writes back.  New elements are appended.
    """
    with open(yml_path, "r") as f:
        content = f.read()

    data = yaml.safe_load(content)
    if not data:
        data = {}
    if "element" not in data:
        data["element"] = []

    for overlay in overlays:
        el = overlay.element
        if getattr(el, "_is_new", False):
            # New element — build dict and append
            el_dct: Dict[str, Any] = {
                "style": el.style,
                "position": {
                    "x": el.position.x,
                    "y": el.position.y,
                    "width": el.position.width,
                    "height": el.position.height,
                },
            }
            if el.variable:
                el_dct["variable"] = el.variable
            if isinstance(el.text, str) and el.text:
                el_dct["text"] = el.text
            if el.text_position != "left":
                el_dct["text_position"] = el.text_position
            if isinstance(el.tooltip, str) and el.tooltip:
                el_dct["tooltip"] = el.tooltip
            # Find the right place to append (tab or top-level)
            _append_element_to_data(data, el, el_dct)
            el._is_new = False  # No longer new after save
        else:
            _update_element_in_data(data["element"], el, overlay._original_text)

    with open(yml_path, "w") as f:
        yaml.dump(
            data, f, default_flow_style=False, sort_keys=False, allow_unicode=True
        )


def _update_element_in_data(
    elements: list, target_element: Any, original_text: Optional[str] = None
) -> bool:
    """Find and update an element's position in the YAML data structure."""
    for el_dict in elements:
        if not isinstance(el_dict, dict):
            continue

        # Match by style + variable (best we can do without IDs)
        style_match = el_dict.get("style") == target_element.style
        var_match = True
        if hasattr(target_element, "variable") and target_element.variable:
            var_match = el_dict.get("variable") == target_element.variable
        elif "text" in el_dict:
            # Use original text for matching (text may have been changed)
            match_text = (
                original_text
                if original_text is not None
                else (
                    target_element.text
                    if isinstance(target_element.text, str)
                    else None
                )
            )
            if match_text is not None:
                var_match = el_dict.get("text") == match_text

        if style_match and var_match and "position" in el_dict:
            el_dict["position"]["x"] = target_element.position.x
            el_dict["position"]["y"] = target_element.position.y
            el_dict["position"]["width"] = target_element.position.width
            el_dict["position"]["height"] = target_element.position.height
            # Update text if changed
            if isinstance(target_element.text, str) and "text" in el_dict:
                el_dict["text"] = target_element.text
            if isinstance(target_element.tooltip, str) and "tooltip" in el_dict:
                el_dict["tooltip"] = target_element.tooltip
            if hasattr(target_element, "text_position"):
                el_dict["text_position"] = target_element.text_position
            return True

        # Recurse into tab panels
        if el_dict.get("style") == "tabpanel" and "tab" in el_dict:
            for tab in el_dict["tab"]:
                if "element" in tab and isinstance(tab["element"], list):
                    if _update_element_in_data(
                        tab["element"], target_element, original_text
                    ):
                        return True

        # Recurse into panels (and any other container with nested ``element``)
        nested = el_dict.get("element")
        if isinstance(nested, list):
            if _update_element_in_data(nested, target_element, original_text):
                return True

    return False


def _append_element_to_data(data: dict, element: Any, el_dct: dict) -> None:
    """Append a new element dict to the correct location in the YAML data.

    Walks the YAML structure to find the matching parent (tab or panel)
    and appends the new element there.
    """
    from guitares.element import Element, Tab

    parent = element.parent

    if isinstance(parent, Tab):
        # Parent is a tab — find it by text
        if _append_to_tab(data.get("element", []), parent.text, el_dct):
            return
    elif isinstance(parent, Element) and parent.style == "panel":
        # Parent is a panel — find it by style + text
        if _append_to_panel(data.get("element", []), parent.text, el_dct):
            return

    # Fallback: append to top-level
    data["element"].append(el_dct)


def _append_to_tab(elements: list, tab_text: str, el_dct: dict) -> bool:
    """Find a tab by text in the YAML and append el_dct to its element list."""
    for top_el in elements:
        if not isinstance(top_el, dict):
            continue
        if top_el.get("style") == "tabpanel" and "tab" in top_el:
            for tab_dct in top_el["tab"]:
                if tab_dct.get("text") == tab_text:
                    if "element" not in tab_dct:
                        tab_dct["element"] = []
                    if isinstance(tab_dct["element"], list):
                        tab_dct["element"].append(el_dct)
                    return True
            # Recurse into tabs' elements
            for tab_dct in top_el["tab"]:
                if "element" in tab_dct and isinstance(tab_dct["element"], list):
                    if _append_to_tab(tab_dct["element"], tab_text, el_dct):
                        return True
        elif top_el.get("style") == "panel" and "element" in top_el:
            if isinstance(top_el["element"], list):
                if _append_to_tab(top_el["element"], tab_text, el_dct):
                    return True
    return False


def _append_to_panel(elements: list, panel_text: str, el_dct: dict) -> bool:
    """Find a panel by text in the YAML and append el_dct to its element list."""
    for top_el in elements:
        if not isinstance(top_el, dict):
            continue
        if top_el.get("style") == "panel" and top_el.get("text") == panel_text:
            if "element" not in top_el:
                top_el["element"] = []
            if isinstance(top_el["element"], list):
                top_el["element"].append(el_dct)
            return True
        # Recurse into tabpanels
        if top_el.get("style") == "tabpanel" and "tab" in top_el:
            for tab_dct in top_el["tab"]:
                if "element" in tab_dct and isinstance(tab_dct["element"], list):
                    if _append_to_panel(tab_dct["element"], panel_text, el_dct):
                        return True
        # Recurse into panels
        if top_el.get("style") == "panel" and "element" in top_el:
            if isinstance(top_el["element"], list):
                if _append_to_panel(top_el["element"], panel_text, el_dct):
                    return True
    return False
