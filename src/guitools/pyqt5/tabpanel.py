from PyQt5.QtWidgets import QWidget, QTabWidget

from guitools.gui import set_elements, get_position_from_string
from .widget import Widget

class TabPanel(Widget):
    def __init__(self, element, parent, gui):
        super().__init__(element, parent, gui)

        x0, y0, wdt, hgt = get_position_from_string(self.element["position"], parent, self.gui.resize_factor)

        # Add tab panel
        tab_panel = QTabWidget(parent)
        tab_panel.setVisible(True)
        tab_panel.setGeometry(x0, y0, wdt, hgt)

        if element["id"] == "modelmaker_hurrywave":
            print("okay")

        self.widgets.append(tab_panel)

        # Used to programmatically select a tab
        self.element["select_tab"] = self.select_tab


        for tab in self.element["tab"]:
            # Place tab in tab panel
            widget = QWidget()
            tab["widget"] = widget
            tab_panel.addTab(widget, tab["string"])
            widget.setGeometry(0, 0, wdt, int(hgt - 20.0 * self.gui.resize_factor))
            pass

        tab_panel.currentChanged.connect(lambda indx, tabs=self.element["tab"]: self.tab_selected(tabs, indx))

        pass

    def tab_selected(self, tabs, indx):
        # Now call the select method
        if tabs[indx]["module"]:
            if hasattr(tabs[indx]["module"], "select"):
                tabs[indx]["module"].select()
        # Update GUI
        self.gui.update()

    def select_tab(self, index):
        # Selected programmatically
        self.element["widget"].widgets[0].setCurrentIndex(index)
        self.tab_selected(self.element["tab"], index)
