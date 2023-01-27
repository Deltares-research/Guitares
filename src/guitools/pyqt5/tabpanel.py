import importlib
from PyQt5.QtWidgets import QWidget, QTabWidget


class TabPanel:

    def __init__(self, element, parent):

        # Add tab panel
        tab_panel = QTabWidget(parent)

        self.element = element
        self.element["widget"] = tab_panel

        x0, y0, wdt, hgt = element["window"].get_position_from_string(self.element["position"], parent)
        tab_panel.setGeometry(x0, y0, wdt, hgt)

        tab_panel.currentChanged.connect(lambda indx, tabs=self.element["tab"]: self.tab_selected(tabs, indx))

        for tab in self.element["tab"]:

            tab["module"] = None

            if "callback" in tab:
                if tab["callback"]:
                    try:
                        tab["module"] = importlib.import_module("models.sfincs." + tab["callback"])
                    except:
                        print("Could not import " + tab["callback"])

            # Place tab in GUI
            widget = QWidget()
            x0, y0, wdt, hgt = element["window"].get_position_from_string(element["position"], parent)
            widget.setGeometry(x0, y0, wdt, hgt)
#            widget.setGeometry(0, 0, wdt, int(hgt - 20.0 * self.main_window.resize_factor - 2.0))
            tab["widget"] = widget
            tab_panel.addTab(widget, tab["string"])

    def tab_selected(self, tabs, indx):
#        self.main_window.active_tab = tabs[indx]
#        self.main_window.update_active_tab()
        if tabs[indx]["module"]:
            try:
                tabs[indx]["module"].select()
            except:
                print(tabs[indx]["callback"] + ".py does not exist !")
