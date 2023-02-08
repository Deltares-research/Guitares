import importlib
from PyQt5.QtWidgets import QWidget, QTabWidget

from guitools.gui import set_elements, get_position_from_string

class TabPanel:

    def __init__(self, element, parent):

        # Add tab panel
        tab_panel = QTabWidget(parent)

        self.element = element
        self.element["widget"] = tab_panel
        self.element["select_tab"] = self.select_tab

        x0, y0, wdt, hgt = get_position_from_string(self.element["position"], parent, element["window"].resize_factor)
        tab_panel.setGeometry(x0, y0, wdt, hgt)

        for tab in self.element["tab"]:
            # Place tab in tab panel
            widget = QWidget()
            x0, y0, wdt, hgt = get_position_from_string(element["position"], parent, element["window"].resize_factor)
            widget.setGeometry(x0, y0, wdt, hgt)
#            widget.setGeometry(0, 0, wdt, int(hgt - 20.0 * self.main_window.resize_factor - 2.0))
            tab["widget"] = widget
            tab_panel.addTab(widget, tab["string"])

        tab_panel.currentChanged.connect(lambda indx, tabs=self.element["tab"]: self.tab_selected(tabs, indx))

    def tab_selected(self, tabs, indx):
        # First update all elements in this tab
        set_elements(tabs[indx]["element"])
        # Set the active tab
        self.element["window"].active_tab = tabs[indx]
        # Now call the select method
        if tabs[indx]["module"]:
            if hasattr(tabs[indx]["module"], "select"):
                tabs[indx]["module"].select()

    def select_tab(self, index):
        self.element["widget"].setCurrentIndex(index)
        self.tab_selected(self.element["tab"], index)
