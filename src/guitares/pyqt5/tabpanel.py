from PyQt5.QtWidgets import QWidget, QTabWidget

from guitares.gui import set_elements, get_position
from .widget import Widget

class TabPanel(QTabWidget):
    def __init__(self, element, parent, gui):
        super().__init__(parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)

        # Add tab panel
#        tab_panel = QTabWidget(parent)
        self.setVisible(True)
        self.setGeometry(x0, y0, wdt, hgt)

#        self.widgets.append(tab_panel)

        # Used to programmatically select a tab
#        element["select_tab"] = self.select_tab

        for tab in element["tab"]:
            # Place tab in tab panel
            widget = QWidget()
            tab["widget"] = widget
            self.addTab(widget, tab["text"])
            widget.setGeometry(0, 0, wdt, int(hgt - 20.0 * gui.resize_factor))

        # Add the callback
        self.currentChanged.connect(lambda indx, tabs=element["tab"]: self.tab_selected(tabs, indx))

    def tab_selected(self, tabs, indx):
        # Now call the select method
        if tabs[indx]["module"]:
            if hasattr(tabs[indx]["module"], "select"):
                tabs[indx]["module"].select()
        # Update GUI
        self.gui.update()

    def select_tab(self, index):
        # Selected programmatically
        self.element["widget"].setCurrentIndex(index)
        self.tab_selected(self.element["tab"], index)
