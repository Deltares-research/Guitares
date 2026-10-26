"""PySide6 toolbar for Guitares main windows.

The toolbar is described in the configuration under ``toolbar`` as a list of
items (or a dict with an ``item`` list). Every item takes ``id``, ``icon``
(path to an image), ``tooltip``, ``method`` (callable or method name in the
window module), ``checkable`` and ``enable``. ``separator: true`` adds a
separator after the item.
"""

import importlib
import traceback
from typing import Any, Dict, List

from PySide6 import QtCore, QtGui
from PySide6.QtWidgets import QToolBar


class ToolBar:
    """Toolbar with actions that call the configured methods.

    Parameters
    ----------
    window : Any
        The Guitares window object.
    items : list of dict
        Toolbar item definitions.
    """

    def __init__(self, window: Any, items: List[dict]) -> None:
        self.window = window
        self.widget = QToolBar(window.window_widget)
        self.widget.setMovable(False)
        self.widget.setIconSize(QtCore.QSize(16, 16))
        window.window_widget.addToolBar(self.widget)
        self.actions: Dict[str, QtGui.QAction] = {}
        for item in items:
            icon = QtGui.QIcon(item["icon"]) if item.get("icon") else QtGui.QIcon()
            text = item.get("text", item.get("tooltip", item.get("id", "")))
            action = QtGui.QAction(icon, text, window.window_widget)
            if item.get("tooltip"):
                action.setToolTip(item["tooltip"])
            action.setCheckable(bool(item.get("checkable", False)))
            action.setEnabled(bool(item.get("enable", True)))
            method = item.get("method")
            module = window.module
            if isinstance(item.get("module"), str):
                try:
                    module = importlib.import_module(item["module"])
                except Exception:
                    traceback.print_exc()
            callback = None
            if callable(method):
                callback = method
            elif (
                isinstance(method, str)
                and module is not None
                and hasattr(module, method)
            ):
                callback = getattr(module, method)
            if callback is not None:
                action.triggered.connect(
                    lambda checked=False, cb=callback, a=action: self._fire(
                        cb, a, checked
                    )
                )
            self.widget.addAction(action)
            if item.get("separator"):
                self.widget.addSeparator()
            if item.get("id"):
                self.actions[item["id"]] = action

    def _fire(self, callback: Any, action: QtGui.QAction, checked: bool) -> None:
        try:
            if action.isCheckable():
                callback(checked, action)
            else:
                callback(action)
            self.window.update()
        except Exception:
            traceback.print_exc()

    def set_enabled(self, item_id: str, enabled: bool) -> None:
        """Enable or disable toolbar item ``item_id``."""
        if item_id in self.actions:
            self.actions[item_id].setEnabled(enabled)

    def set_checked(self, item_id: str, checked: bool) -> None:
        """Set the checked state of a checkable toolbar item."""
        if item_id in self.actions:
            self.actions[item_id].setChecked(checked)
