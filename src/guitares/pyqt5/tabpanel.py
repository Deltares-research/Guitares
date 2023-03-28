from PyQt5.QtWidgets import QWidget, QTabWidget
import traceback

class TabPanel(QTabWidget):
    def __init__(self, element):
        super().__init__(element.parent.widget)

        self.element = element

        self.setVisible(True)

        # Used to programmatically select a tab
#        element["select_tab"] = self.select_tab

        for tab in element.tabs:
            # Place tab in tab panel
            widget = QWidget()
            tab.widget = widget
            self.addTab(widget, tab.text)

        # Add the callback
        self.currentChanged.connect(lambda indx, tabs=element.tabs: self.tab_selected(tabs, indx))

        self.set_geometry()

    def tab_selected(self, tabs, indx):
        # Now call the select method
        if tabs[indx].module:
            if hasattr(tabs[indx].module, "select"):
                try:
                    tabs[indx].module.select()
                except:
                    traceback.print_exc()

        # Also check if there are tab panels in this tab. If so, execute select for active tab.
        if tabs[indx].elements:
            for element in tabs[indx].elements:
                if element.style == "tabpanel":
                    j = element.widget.currentIndex()
                    try:
                        element.widget.select_tab(j)
                    except:
                        traceback.print_exc()
        # Update GUI
        self.element.window.update()

    def select_tab(self, index):
        # Selected programmatically
        self.setCurrentIndex(index)
        self.tab_selected(self.element.tabs, index)

    def clear_tab(self, index):
        tab = self.element.tabs[index].widget
        for child in tab.children():
            child.setParent(None)

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        for tab in self.element.tabs:
            # Resize tab widgets
            tab.widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))
