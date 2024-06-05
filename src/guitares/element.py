import importlib

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
        self.multiselection = False
        self.sortable = True
        self.selection_type = "single"
        self.ready = False
        # Mapbox
        self.map_style = "mapbox://styles/mapbox/streets-v11"
        self.map_center = [0, 0]
        self.map_zoom = 0
        self.map_projection = "mercator"

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
            if isinstance(dct["module"], str):
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
                try:
                    # Start with the base module
                    module = self.module
                    # If the method contains a dot, it means that it is a method of a class
                    method_path = self.method.split(".")
                    # Loop through the method path
                    for idx, method in enumerate(method_path):
                        # The last element is the method itself
                        if idx == len(method_path) - 1:
                            if hasattr(module, method):
                                self.callback = getattr(module, method)
                            else:
                                raise Exception("Error! Could not find method " + self.method + " in module " + self.module.__name__)
                        else:
                            if hasattr(module, method):
                                class_ = getattr(module, method)
                                # Initialize the class object
                                module = class_()
                            else:
                                raise Exception("Error! Could not find method " + self.method + " in module " + self.module.__name__)
                except Exception as e:
                    print(e)
        if self.variable_group in self.gui.variables:
            if self.variable in self.gui.variables[self.variable_group]:
                self.type = type(self.gui.variables[self.variable_group][self.variable]["value"])

        # "title" for backward compatibility
        if "title" in dct:
            self.text = dct["title"]
            self.title = dct["title"]

        if "text" in dct:
            if isinstance(dct["text"], dict):
                self.text = Text(self.variable_group)
                if "variable" in dct["text"]:
                    self.text.variable = dct["text"]["variable"]
                if "variable_group" in dct["text"]:
                    self.text.variable_group = dct["text"]["variable_group"]
            else:
                self.text = dct["text"]

        if "text_position" in dct:
            self.text_position = dct["text_position"]

        if "tooltip" in dct:    
            if isinstance(dct["tooltip"], dict):
                self.tooltip = Text(self.variable_group)
                if "variable" in dct["tooltip"]:
                    self.tooltip.variable = dct["tooltip"]["variable"]
                if "variable_group" in dct["tooltip"]:
                    self.tooltip.variable_group = dct["tooltip"]["variable_group"]
            else:
                self.tooltip = dct["tooltip"]

        # Special for popupmenus and listboxes
        if "select" in dct:
            # Either 'index' or 'item'
            self.select = dct["select"]

        if "option_value" in dct:    
            if isinstance(dct["option_value"], dict):
                if "variable" in dct["option_value"]:
                    self.option_value.variable = dct["option_value"]["variable"]
                if "variable_group" in dct["option_value"]:
                    self.option_value.variable_group = dct["option_value"]["variable_group"]
            else:
                # It's a list
                self.option_value.list = dct["option_value"]

        if "option_string" in dct:    
            if isinstance(dct["option_string"], dict):
                if "variable" in dct["option_string"]:
                    self.option_string.variable = dct["option_string"]["variable"]
                if "variable_group" in dct["option_string"]:
                    self.option_string.variable_group = dct["option_string"]["variable_group"]
            else:
                # It's a list
                self.option_string.list = dct["option_string"]

        if "filter" in dct:
            self.filter = dct["filter"]

        if "url" in dct:
            if isinstance(dct["url"], dict):
                self.url = Text(self.variable_group)
                if "variable" in dct["url"]:
                    self.url.variable = dct["url"]["variable"]
                if "variable_group" in dct["url"]:
                    self.url.variable_group = dct["url"]["variable_group"]
            else:
                self.url = dct["url"]

        if "collapse" in dct:
            self.collapse = dct["collapse"]

        if "collapsed" in dct:
            self.collapsed = dct["collapsed"]

        if "fraction_collapsed" in dct:
            self.fraction_collapsed = dct["fraction_collapsed"]

        if "fraction_expanded" in dct:
            self.fraction_expanded = dct["fraction_expanded"]

        if "multiselection" in dct:
            self.multiselection = dct["multiselection"]

        if "enable" in dct:
            self.enable = dct["enable"]

        if "selection_type" in dct:
            self.selection_type = dct["selection_type"]

        if "selection_direction" in dct:
            self.selection_direction = dct["selection_direction"]

        if "sortable" in dct:
            self.sortable = dct["sortable"]

        if "map_style" in dct:
            self.map_style = dct["map_style"]

        if "map_lat" in dct:
            self.map_center[1] = dct["map_lat"]

        if "map_lon" in dct:
            self.map_center[0] = dct["map_lon"]

        if "map_zoom" in dct:
            self.map_zoom = dct["map_zoom"]

        if "map_projection" in dct:
            self.map_projection = dct["map_projection"]    

        if "dependency" in dct:
            for dep in dct["dependency"]:
                dependency = Dependency()
                dependency.gui = parent.gui
                if "action" in dep:
                    dependency.action = dep["action"]
                if "checkfor" in dep:
                    dependency.checkfor = dep["checkfor"]
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
                
                if "string" in tab_dct: # Backward compatibility
                    tab.text = tab_dct["string"]
                if "text" in tab_dct:
                    tab.text = tab_dct["text"]
                if "variable_group" in tab_dct:
                    tab.variable_group = tab_dct["variable_group"]
                if "module" in tab_dct:
                    try:
                        if tab_dct["module"]:
                            tab.module = importlib.import_module(tab_dct["module"])
                    except Exception as e:
                        print("Error! Module " + tab_dct["module"] + " could not be imported!")
                        print(e)

                tab.dependencies = []
                if "dependency" in tab_dct:
                    for dep in tab_dct["dependency"]:
                        dependency = Dependency()
                        dependency.gui = self.gui
                        if "action" in dep:
                            dependency.action = dep["action"]
                        if "checkfor" in dep:
                            dependency.checkfor = dep["checkfor"]
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
                        tab.dependencies.append(dependency)

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

        elif self.style == "tableview":
            from .pyqt5.tableview import TableView
            self.widget = TableView(self)

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

        elif self.style == "pushselectdir":
            from .pyqt5.pushopendir import PushOpenDir

            self.widget = PushOpenDir(self)
            
        elif self.style == "pushsavefile":
            from .pyqt5.pushsavefile import PushSaveFile
            self.widget = PushSaveFile(self)

        elif self.style == "mapbox":
            # We don't want to add the mapbox widget if set to invisible, because it takes a long time to load.
            # This means that widgets that are originally set to invisible will not be added to the GUI!
            okay = True
            if self.dependencies:
                for dep in self.dependencies:
                    if dep.action == "visible":
                        if not dep.get():
                            okay = False
            if okay:                
                from .pyqt5.mapbox.mapbox import MapBox
                self.widget = MapBox(self)

        elif self.style == "mapbox_compare":
            # We don't want to add the mapbox widget if set to invisible, because it takes a long time to load.
            # This means that widgets that are originally set to invisible will not be added to the GUI!
            okay = True
            if self.dependencies:
                for dep in self.dependencies:
                    if dep.action == "visible":
                        if not dep.get():
                            okay = False
            if okay:                
                from .pyqt5.mapbox.mapbox_compare import MapBoxCompare
                self.widget = MapBoxCompare(self)

        elif self.style == "webpage":
            from .pyqt5.webpage import WebPage
            self.widget = WebPage(self)
        else:
            print("Element style " + self.style + " not recognized!")

        # And set the visibility
        if self.style != "radiobuttongroup": # Cannot set radiobutton group to visible
            if self.widget:
                self.widget.setVisible(True)
        else:
            self.widget.set_visible(True)        

    def set_geometry(self):
        try:
            self.widget.set_geometry()
        except:
            pass    

    def get_position(self):

        # Position as defined in the yml file 
        position = self.position
        resize_factor = self.gui.resize_factor
        parent = self.parent.widget

        # TO DO: relative positions!
        pwdt = parent.geometry().width()
        phgt = parent.geometry().height()

        # Multiply with resize factor for high-res screens
        x0 = position.x * resize_factor
        y0 = position.y * resize_factor
        wdt = position.width * resize_factor
        hgt = position.height * resize_factor

        if x0>0:
            # x0 is absolute
            if wdt>0:
                # wdt is absolute
                pass
            else:
                # wdt is relative
                wdt = pwdt - x0 + wdt
        else:
            # x0 is relative
            if wdt>0:
                # wdt is absolute
                x0 = pwdt - wdt + x0
            else:
                # wdt is relative
                x0 = pwdt + x0
                wdt = pwdt - x0 + wdt

        if y0>0:
            # y0 is absolute
            if hgt>0:
                # hgt is absolute
                y0 = phgt - (y0 + hgt)
            else:
                # hgt is relative
                y0 = - hgt
                hgt = phgt - position.y * resize_factor + hgt
        else:
            # y0 is relative
            if hgt>0:
                # hgt is absolute
                y0 = phgt - hgt
            else:
                # hgt is relative
                hgt = - y0 - hgt
                y0 = phgt - (y0 + hgt)

        # Round to integers
        x0 = int(x0)
        y0 = int(y0)
        wdt = int(wdt)
        hgt = int(hgt)

        return x0, y0, wdt, hgt

    def set_dependencies(self):
        # TODO: Would be cleaner to add enable and disable methods in the individual elements
        # Check if this element is a tabpanel
        if self.style == "tabpanel":
            for itab, tab in enumerate(self.tabs):
                # Check if this tab has dependencies
                if tab.dependencies:
                    for dependency in tab.dependencies:
                        true_or_false = dependency.get()
                        if dependency.action == "enable":
                            if true_or_false:
                                self.widget.setTabEnabled(itab, True)
                            else:
                                self.widget.setTabEnabled(itab, False)

                        elif dependency.action == "visible":
                            if true_or_false:
                                self.widget.setTabVisible(itab, True)
                            else:
                                self.widget.setTabVisible(itab, False)    

        else:            
            # "normal" element
            for dependency in self.dependencies:
                true_or_false = dependency.get()
                if dependency.action == "visible":
                    if self.style == "radiobuttongroup": # Cannot set radiobutton group directly
                        self.widget.set_visible(true_or_false)        
                    elif self.style == "mapbox" or self.style == "mapbox_compare":
                        if self.widget.ready:
                            self.widget.view.setVisible(true_or_false)        
                    else:    
                        if self.widget:
                            self.widget.setVisible(true_or_false)
                            if hasattr(self.widget, "text_widget"):
                                self.widget.text_widget.setVisible(true_or_false)
                elif dependency.action == "enable":
                    if self.style == "radiobuttongroup": # Cannot set radiobutton group directly
                        self.widget.set_enabled(true_or_false)        
                    else:    
                        if self.widget:
                            self.widget.setEnabled(true_or_false)
                            if hasattr(self.widget, "text_widget"):
                                self.widget.text_widget.setEnabled(true_or_false)
                elif dependency.action == "check":
                    self.widget.setChecked(true_or_false)
            if not self.enable:        
                if self.widget:
                    self.widget.setEnabled(False)
                    if hasattr(self.widget, "text_widget"):
                        self.widget.text_widget.setEnabled(False)



    def clear_tab(self, index):
        self.widget.clear_tab(index)

    def set_collapsed(self, true_or_false):
        self.collapsed = true_or_false
        self.gui.window.resize_elements(self.elements)