import importlib
from PyQt5 import QtCore

from guitares.dependencies import Dependency, DependencyCheck

class Position:
    def __init__(self):
        self.x      = 0
        self.y      = 0
        self.width  = 10
        self.height = 10

class Text:
    def __init__(self, variable_group):
        self.variable       = ""
        self.variable_group = variable_group

class OptionValue:
    def __init__(self, variable_group):
        self.list           = []
        self.variable       = ""
        self.variable_group = variable_group

class OptionString:
    def __init__(self, variable_group):
        self.list           = []
        self.variable       = ""
        self.variable_group = variable_group


class Tab:
    def __init__(self, variable_group, module):
        self.text           = ""
        self.module         = ""
        self.variable_group = variable_group
        self.module         = module
        self.elements       = []
        self.gui            = None


class Element:
    def __init__(self, dct, parent, window):
        self.style = None
        self.widget = None
        self.parent = parent
        self.position = Position()
        self.tabs = []
        self.dependencies = []
        self.elements = []
        self.visible = True
        self.enable = True
        self.id = ""
        self.variable = None
        self.variable_group = parent.variable_group
        self.module = parent.module
        self.method = ""
        self.callback = None
        self.text = ""
        self.text_position = "left"
        self.tooltip = ""
        self.type = str
        self.gui    = window.gui
        self.getvar = window.gui.getvar
        self.setvar = window.gui.setvar
        self.window = window
        self.select = "item"
        self.option_value = OptionValue(self.variable_group)
        self.option_string = OptionString(self.variable_group)
        self.title = "Select File"
        self.filter = "All Files (*.*)"
        self.url = ""
        self.icon = ""
        self.collapse = False
        self.collapsed = False
        self.fraction_collapsed = 1.0
        self.fraction_expanded = 0.5

        # Now update element attributes based on dict

        self.style = dct["style"]

        if "position" in dct:
            self.position.x = dct["position"]["x"]
            self.position.y = dct["position"]["y"]
            if "width" in dct["position"]:
                self.position.width = dct["position"]["width"]
            if "height" in dct["position"]:
                self.position.height = dct["position"]["height"]

        if "variable" in dct:
            self.variable = dct["variable"]
        if "variable_group" in dct:
            self.variable_group = dct["variable_group"]
        if "id" in dct:
            self.id = dct["id"]
        if "module" in dct:
            if type(dct["module"]) == str:
                try:
                    self.module = importlib.import_module(dct["module"])
                except:
                    print("Error! Could not import module " + dct["module"])
        if "method" in dct:
            self.method = dct["method"]
        if hasattr(self.method, '__call__'):
             # Callback function is already defined as method
             self.callback = self.method
        else:
            if self.module and self.method:
                if hasattr(self.module, self.method):
                    self.callback = getattr(self.module, self.method)
                else:
                    print("Error! Could not find method " + self.method)
        if self.variable_group in self.gui.variables:
            if self.variable in self.gui.variables[self.variable_group]:
                self.type = type(self.gui.variables[self.variable_group][self.variable]["value"])

        # "title" for backward compatibility
        if "title" in dct:
            self.text = dct["title"]
        if "text" in dct:
            if type(dct["text"]) == dict:
                self.text = Text(self.variable_group)
                if "variable" in dct:
                    self.text.variable(dct["variable"])
                if "variable_group" in dct:
                    self.text.variable_group(dct["variable_group"])
            else:
                self.text = dct["text"]
        if "text_position" in dct:
            self.text_position = dct["text_position"]
        if "tooltip" in dct:
            if type(dct["tooltip"]) == dict:
                self.tooltip = Text(self.variable_group)
                if "variable" in dct:
                    self.tooltip.variable(dct["variable"])
                if "variable_group" in dct:
                    self.tooltip.variable_group(dct["variable_group"])
            else:
                self.tooltip = dct["tooltip"]

        # Special for popupmenus and listboxes
        if "select" in dct:
            # Either 'index' or 'item'
            self.select = dct["select"]
        if "option_value" in dct:
            if type(dct["option_value"]) == dict:
                if "variable" in dct["option_value"]:
                    self.option_value.variable = dct["option_value"]["variable"]
                if "variable_group" in dct["option_value"]:
                    self.option_value.variable_group = dct["option_value"]["variable_group"]
            else:
                # It's a list
                self.option_value.list = dct["option_value"]

        if "option_string" in dct:
            if type(dct["option_string"]) == dict:
                if "variable" in dct["option_string"]:
                    self.option_string.variable = dct["option_string"]["variable"]
                if "variable_group" in dct["option_string"]:
                    self.option_string.variable_group = dct["option_string"]["variable_group"]
            else:
                # It's a list
                self.option_string.list = dct["option_string"]

        if "title" in dct:
            self.title = dct["title"]
        if "filter" in dct:
            self.filter = dct["filter"]
        if "url" in dct:
            self.url = dct["url"]
        if "collapse" in dct:
            self.collapse = dct["collapse"]
        if "collapsed" in dct:
            self.collapsed = dct["collapsed"]
        if "fraction_collapsed" in dct:
            self.fraction_collapsed = dct["fraction_collapsed"]
        if "fraction_expanded" in dct:
            self.fraction_expanded = dct["fraction_expanded"]

        if "dependency" in dct:
            for dep in dct["dependency"]:
                dependency = Dependency()
                dependency.gui = parent.gui
                for check_dct in dep["check"]:
                    check = DependencyCheck(self.variable_group)
                    if "variable" in check_dct:
                        check.variable = check_dct["variable"]
                    if "variable_group" in check_dct:
                        check.variable_group = check_dct["variable_group"]
                    if "operator" in check_dct:
                        check.operator = check_dct["operator"]
                    if "value" in check_dct:
                        check.value = check_dct["value"]
                    dependency.checks.append(check)
                self.dependencies.append(dependency)

        if self.style == "tabpanel":
            self.tabs = []
            # Loop through tabs
            for itab, tab_dct in enumerate(dct["tab"]):
                tab = Tab(self.variable_group, self.module)
                tab.gui = self.gui
                # Backward compatibility
                if "string" in tab_dct:
                    tab.text = tab_dct["string"]
                if "text" in tab_dct:
                    tab.text = tab_dct["text"]
                if "variable_group" in tab_dct:
                    tab.variable_group = tab_dct["variable_group"]
                if "module" in tab_dct:
                    try:
                        tab.module = importlib.import_module(tab_dct["module"])
                    except:
                        print("Error! Module " + tab_dct["module"] + " could not be imported!")
                self.tabs.append(tab)

    def add(self):
        
        if self.style == "tabpanel":
            from .pyqt5.tabpanel import TabPanel
            self.widget = TabPanel(self)

        elif self.style == "panel":
            # Add frame
            from .pyqt5.frame import Frame
            self.widget = Frame(self)

        elif self.style == "dual_frame":
            # Add dual frame
            from .pyqt5.dual_frame import DualFrame
            self.widget = DualFrame(self)


        elif self.style == "pushbutton":
            from .pyqt5.pushbutton import PushButton
            self.widget = PushButton(self)

        elif self.style == "edit":
            from .pyqt5.edit import Edit
            self.widget = Edit(self)

        elif self.style == "datetimeedit":
            from .pyqt5.date_edit import DateEdit
            self.widget = DateEdit(self)

        elif self.style == "text":
            from .pyqt5.text import Text
            self.widget = Text(self)

        elif self.style == "popupmenu":
            from .pyqt5.popupmenu import PopupMenu
            self.widget = PopupMenu(self)

        elif self.style == "listbox":
            from .pyqt5.listbox import ListBox
            self.widget = ListBox(self)

        elif self.style == "checkbox":
            from .pyqt5.checkbox import CheckBox
            self.widget = CheckBox(self)

        elif self.style == "radiobuttongroup":
            from .pyqt5.radiobuttongroup import RadioButtonGroup
            self.widget = RadioButtonGroup(self)

        elif self.style == "slider":
            from .pyqt5.slider import Slider
            self.widget = Slider(self)

        elif self.style == "pushselectfile":
            from .pyqt5.pushopenfile import PushOpenFile
            self.widget = PushOpenFile(self)

        elif self.style == "pushsavefile":
            from .pyqt5.pushsavefile import PushSaveFile
            self.widget = PushSaveFile(self)

        elif self.style == "mapbox":
            from .pyqt5.mapbox.mapbox import MapBox
            self.widget = MapBox(self)
        elif self.style == "webpage":
            from .pyqt5.webpage import WebPage
            self.widget = WebPage(self)
        else:
            print("Element style " + self.style + " not recognized!")

        # And set the values
        if self.style != "radiobuttongroup": # Cannot set radiobutton group to visible
            if self.widget:
                self.widget.setVisible(True)

    def set_geometry(self):
        self.element.widget.set_geometry()

        # resize_factor = self.gui.resize_factor

        # x0, y0, wdt, hgt = self.get_position()

        # if self.style == "mapbox" or self.style == "webpage":
        #     self.widget.view.setGeometry(x0, y0, wdt, hgt)
        # elif self.style == "radiobuttongroup":
        #     nbuttons = len(self.option_value)
        #     yll = y0 + hgt - int(nbuttons * 20 * resize_factor)
        #     for i in range(nbuttons):
        #         self.widget.buttons()[i].setGeometry(x0,
        #                                                 int(yll + i * 20 * resize_factor),
        #                                                 wdt,
        #                                                 int(20 * resize_factor))
        # else:
        #     # All other elements
        #     self.widget.setGeometry(x0, y0, wdt, hgt)

        # if self.style == "tabpanel":
        #     for tab in self.tabs:
        #         # Resize tab widgets
        #         tab.widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))

        # # Also update text labels
        # if self.style == "panel":
        #     if hasattr(self.widget, "text_widget"):
        #         # Also change title widget
        #         self.widget.text_widget.setGeometry(x0 + 10, y0 - 9, self.text_width, 16)
        #         self.widget.text_widget.setAlignment(QtCore.Qt.AlignTop)

        # else:
        #     if hasattr(self.widget, "text_widget"):
        #         # Also change title widget
        #         label = self.widget.text_widget
        #         fm = label.fontMetrics()
        #         wlab = fm.size(0, self.text).width()
        #         if self.text_position == "above-center" or self.text_position == "above":
        #             label.setAlignment(QtCore.Qt.AlignCenter)
        #             label.setGeometry(x0, y0 - 20, wdt, 20)
        #         elif self.text_position == "above-left":
        #             label.setAlignment(QtCore.Qt.AlignLeft)
        #             label.setGeometry(x0, y0 - 20, wlab, 20)
        #         else:
        #             # Assuming left
        #             label.setAlignment(QtCore.Qt.AlignRight)
        #             label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, 20)

    def get_position(self):

        position = self.position
        resize_factor = self.gui.resize_factor
        parent = self.parent.widget

        # collapsable = False
        # if hasattr(self.parent, "style"):
        #     if self.parent.style == "panel" and self.parent.collapse:
        #         collapsable = True
        #
        # if collapsable:
        #     pwdt = self.parent.widget.geometry().width()
        #     phgt = self.parent.widget.geometry().height()
        #     if self == self.parent.elements[0]:
        #         # First panel
        #         x0 = 0
        #         y0 = 0
        #         if self.parent.collapsed:
        #             wdt = self.parent.fraction_collapsed * pwdt
        #         else:
        #             wdt = self.parent.fraction_expanded * pwdt
        #         hgt = phgt
        #     else:
        #         # Second panel
        #         if self.parent.collapsed:
        #             x0 = self.parent.fraction_collapsed * pwdt
        #         else:
        #             x0 = self.parent.fraction_expanded * pwdt
        #         y0 = 0
        #         wdt = pwdt - x0
        #         hgt = phgt
        #
        # else:

            # TO DO: relative positions!
        pwdt = parent.geometry().width()
        phgt = parent.geometry().height()

        x0 = position.x * resize_factor
        y0 = position.y * resize_factor
        wdt = position.width * resize_factor
        hgt = position.height * resize_factor

        if x0>0:
            if wdt>0:
                pass
            else:
                wdt = pwdt - x0 + wdt
        else:
            if wdt>0:
                x0 = pwdt - wdt + x0
            else:
                x0 = pwdt + x0
                wdt = pwdt - x0 + wdt

        if y0>0:
            if hgt>0:
                y0 = phgt - (y0 + hgt)
            else:
                y0 = - hgt
                hgt = phgt - position.y * resize_factor + hgt
        else:
            if hgt>0:
                y0 = phgt - hgt
            else:
                hgt = - y0 - hgt
                y0 = phgt - (y0 + hgt)

        x0 = int(x0)
        y0 = int(y0)
        wdt = int(wdt)
        hgt = int(hgt)

        return x0, y0, wdt, hgt

    def set_dependencies(self):
        for dependency in self.dependencies:
            okay = dependency.get()
            if dependency.action == "visible":
                if okay:
                    self.widget.setVisible(True)
                    if hasattr(self.widget, "text_widget"):
                        self.widget.text_widget.setVisible(True)
                else:
                    self.widget.setVisible(False)
                    if hasattr(self.widget, "text_widget"):
                        self.widget.text_widget.setVisible(False)
            elif dependency.action == "enable":
                if okay:
                    self.widget.setEnabled(True)
                    self.widget.setStyleSheet("")
                    if hasattr(self.widget, "text_widget"):
                        self.widget.text_widget.setVisible(True)
                else:
                    self.widget.setEnabled(False)
                    if hasattr(self.widget, "text_widget"):
                        self.widget.text_widget.setVisible(False)
            elif dependency.action == "check":
                if okay:
                    self.widget.setChecked(True)
                else:
                    self.widget.setChecked(False)

    def clear_tab(self, index):
        self.widget.clear_tab(index)

    def set_collapsed(self, true_or_false):
        self.collapsed = true_or_false
        self.gui.window.resize_elements(self.elements)