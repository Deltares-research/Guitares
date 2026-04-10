"""PySide6 tab panel widget wrapper for Guitares tabbed interfaces."""

import traceback
from typing import Any, List

from PySide6.QtWidgets import QTabWidget, QWidget


class TabPanel(QTabWidget):
    """Tab panel that manages multiple tabs with select/deselect lifecycle.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this tab panel.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)

        self.element = element

        self.setVisible(True)

        for tab in element.tabs:
            # Place tab in tab panel
            widget = QWidget()
            tab.widget = widget
            self.addTab(widget, tab.text)

        # Add the callback
        self.currentChanged.connect(
            lambda indx, tabs=element.tabs: self.tab_selected(tabs, indx)
        )

        self.previous_tab_index: int = 0

        self.set_geometry()

    def tab_selected(self, tabs: List[Any], indx: int) -> None:
        """Handle tab selection, calling deselect on the previous tab and select on the new.

        Parameters
        ----------
        tabs : List[Any]
            The list of tab descriptors.
        indx : int
            The index of the newly selected tab.
        """
        # If the previous tab has a module, call the deselect method
        previous_tab = tabs[self.previous_tab_index]

        if previous_tab.module:
            if hasattr(previous_tab.module, "deselect"):
                try:
                    previous_tab.module.deselect()
                except Exception:
                    traceback.print_exc()
        # Also check if there are any tab panels in the previous tab. If so, execute deselect for active tab.
        for element in previous_tab.elements:
            # Check if child is a TabPanel
            if element.style == "tabpanel":
                iii = element.widget.currentIndex()
                if hasattr(element.tabs[iii].module, "deselect"):
                    try:
                        element.tabs[iii].module.deselect()
                    except Exception:
                        traceback.print_exc()

        self.previous_tab_index = indx

        # Now call the select method
        if tabs[indx].module:
            if hasattr(tabs[indx].module, "select"):
                try:
                    tabs[indx].module.select()
                except Exception:
                    traceback.print_exc()

        # Also check if there are tab panels in this tab. If so, execute select for active tab.
        if tabs[indx].elements:
            for element in tabs[indx].elements:
                if element.style == "tabpanel":
                    j = element.widget.currentIndex()
                    try:
                        element.widget.select_tab(j)
                    except Exception:
                        traceback.print_exc()
        # Update GUI
        self.element.window.update()

    def select_tab(self, index: int) -> None:
        """Programmatically select a tab by index.

        Parameters
        ----------
        index : int
            The tab index to select.
        """
        self.setCurrentIndex(index)
        self.tab_selected(self.element.tabs, index)

    def clear_tab(self, index: int) -> None:
        """Remove all child widgets from a tab.

        Parameters
        ----------
        index : int
            The tab index to clear.
        """
        tab = self.element.tabs[index].widget
        for child in tab.children():
            child.setParent(None)

    def set_geometry(self) -> None:
        """Position and size the tab panel and its tab content areas."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        for tab in self.element.tabs:
            # Resize tab widgets
            tab.widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))
