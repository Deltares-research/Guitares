"""PyQt5 tab panel widget with tab selection callbacks."""

import traceback
from typing import Any

from PyQt5.QtWidgets import QTabWidget, QWidget


class TabPanel(QTabWidget):
    """Tab panel that manages multiple tabs with select/deselect callbacks.

    Parameters
    ----------
    element : Any
        The GUI element descriptor containing tab definitions and callback modules.
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

        self.previous_tab_index = 0

        self.set_geometry()

    def tab_selected(self, tabs: list[Any], indx: int) -> None:
        """Handle tab selection by calling deselect/select on the tab modules.

        Parameters
        ----------
        tabs : list[Any]
            The list of tab descriptors.
        indx : int
            The index of the newly selected tab.
        """
        # If the previous tab has a module, call the deselect method
        if tabs[self.previous_tab_index].module:
            if hasattr(tabs[self.previous_tab_index].module, "deselect"):
                try:
                    tabs[self.previous_tab_index].module.deselect()
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
        """Set widget position and size, including resizing tab content areas."""
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        for tab in self.element.tabs:
            # Resize tab widgets
            tab.widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))
