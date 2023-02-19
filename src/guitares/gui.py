import os
import yaml
import importlib
import time
import sched
import sys
import copy
import shutil

import http.server
import socketserver
from urllib.request import urlopen
from urllib.error import *
import threading
from PyQt5.QtWidgets import QApplication, QDialog, QWidget, QVBoxLayout
from PyQt5 import QtCore

class GUI:
    def __init__(self, module,
                 framework="pyqt5",
                 splash_file=None,
                 stylesheet=None,
                 config_path=None,
                 config_file=None,
                 icon=None,
                 server_path=None,
                 server_port=3000,
                 js_messages=True,
                 copy_mapbox_server_folder=False,
                 mapbox_token_file="mapbox_token.txt"):

        self.module      = module
        self.framework   = framework
        self.splash_file = splash_file
        self.stylesheet  = stylesheet
        self.config_file = config_file
        self.config_path = config_path
        self.splash      = None
        self.config      = {}
        self.variables   = {}
        self.server_thread = None
        self.server_path = server_path
        self.server_port = server_port
        self.js_messages = js_messages

        # For some reason, the splash crashes on QPixmap(splash_file) ...
        # self.show_splash()

        if not self.config_path:
            self.config_path = os.getcwd()

        self.popup_data = None
        self.resize_factor = 1.0

        if server_path:
            # Need to run http server (e.g. for MapBox)
            # Check if something's already running on port 3000
            try:
                html = urlopen("http://localhost:" + str(server_port) + "/")
                print("Found server running at port 3000 ...")
            except:
                print("Starting http server ...")
                # Run http server in separate thread
                # Use daemon=True to make sure the server stops after the application is finished
                if copy_mapbox_server_folder:
                    mpboxpth = os.path.join(os.path.dirname(os.path.abspath(__file__)), "pyqt5", "mapbox", "server")
                    # Delete current server folder
                    if os.path.exists(server_path):
                        shutil.rmtree(server_path)
                    # Now copy over folder from mapbox
                    shutil.copytree(mpboxpth, server_path)

                thr = threading.Thread(target=run_server, args=(server_path, server_port), daemon=True)
                thr.start()

            # Read mapbox token and store in js file in server path
            if os.path.exists(os.path.join(module.main_path, mapbox_token_file)):
                fid = open(os.path.join(module.main_path, mapbox_token_file), "r")
                mapbox_token = fid.readlines()
                fid.close()
                fid = open(os.path.join(server_path, "mapbox_token.js"), "w")
                fid.write("mapbox_token = '" + mapbox_token[0].strip() + "';")
                fid.close()


    def show_splash(self):
        if self.framework == "pyqt5" and self.splash_file:
            from .pyqt5.splash import Splash
#            self.splash = Splash(os.path.join(self.config_path, self.splash_file), seconds=2.0).splash
            self.splash = Splash(self.splash_file, seconds=2.0).splash

    def close_splash(self):
        if self.splash:
            self.splash.close()

    def build(self,
              window={},
              menu={},
              toolbar={},
              element=[]):

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        app = QApplication(sys.argv)

        if self.stylesheet:
            app.setStyleSheet(open(os.path.join(self.config_path, self.stylesheet), "r").read())

        if self.config_file:
            self.config = read_gui_config(self.config_path, self.config_file)

        set_missing_config_values(self.config, self)

        # Add main window
        if self.framework=="pyqt5":        
            from .pyqt5.main_window import MainWindow

        self.window = MainWindow(self)

        # Add menu
        if self.config["menu"]:
            from .pyqt5.menu import Menu
            self.menu = Menu(self.config["menu"], self.window)

        # Add toolbar
        # TODO

        # Status bar
#        self.window.statusBar().showMessage('Message in statusbar.')

        # Central widget
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)
        self.window.setCentralWidget(widget)
        self.central_widget = widget

        # Check if gui variables exist. If not, give a warning.

        # Add elements
        add_elements(self.config["element"], self.central_widget, self)

        # Set elements
        self.update()

        self.window.show()

        if hasattr(self.module, "on_build"):
            self.module.on_build()

        app.exec_()

    def update(self):
        # Update all elements
        set_elements(self.config["element"])

    def update_tab(self):
        # Update all elements in tab
        set_elements(self.config["element"])
        print("Another call to update_tab ...")

    def setvar(self, group, name, value):
        if group not in self.variables:
            self.variables[group] = {}
        if name not in self.variables[group]:
            self.variables[group][name] = {}
        self.variables[group][name]["value"] = value

    def getvar(self, group, name):
        if group not in self.variables:
            print("Error! GUI variable group '" + group + "' not defined !")
            return None
        elif name not in self.variables[group]:
            print("Error! GUI variable '" + name + "' not defined in group '" + group + "'!")
            return None
        return self.variables[group][name]["value"]

    def popup(self, config, data, modal=True):
        from .pyqt5.popup_window import PopupWindow
        self.popup_data = copy.copy(data)
        p = PopupWindow(config, self, modal=modal)
        if p.result() == 1:
            data = self.popup_data
        return data

    def get_position(self, position, parent):
        # Use the method outside of the class
        x0, y0, wdt, hgt = get_position(position, parent, self.resize_factor)
        return x0, y0, wdt, hgt

def read_gui_config(path, file_name):
    d = yaml2dict(os.path.join(path, file_name))
    config = {}
    config["window"]  = {}
    config["menu"]    = {}
    config["toolbar"] = {}
    config["element"] = []
    if "window" in d:
        config["window"]  = d["window"]
    if "menu" in d:
        config["menu"]    = d["menu"]
    if "toolbar" in d:
        config["toolbar"] = d["toolbar"]
    if "element" in d:
        # Recursively read elements
        config["element"] = read_gui_elements(path, file_name)
    return config

def read_gui_elements(path, file_name):
    # Return just the elements
    d = yaml2dict(os.path.join(path, file_name))
    element = d["element"]
    for el in d["element"]:
        if el["style"] == "tabpanel":
            # Loop through tabs
            for tab in el["tab"]:
                #
                # # Backward compatibility
                # if "string" in tab:
                #     tab["text"] = tab["string"]

                if "element" in tab:
                    if type(tab["element"]) == str:
                        # Must be a file
                        tab["element"] = read_gui_elements(path, tab["element"])
                else:
                    tab["element"] = []
        # else:
        #
        #     # Backward compatibility
        #     if "title" in el:
        #         el["text"] = el["title"]

    return element

def set_missing_config_values(config, gui):
    if "window" not in config:
        config["window"] = {}
    # Window
    if "width" not in config["window"]:
        config["window"]["width"] = 800
    if "height" not in config["window"]:
        config["window"]["height"] = 800
    if "title" not in config["window"]:
        config["window"]["title"] = ""
    if "module" not in config["window"]:
        config["window"]["module"] = None
    if "variable_group" not in config["window"]:
        config["window"]["variable_group"] = "_main"
    if "icon" not in config["window"]:
        config["window"]["icon"] = None
    # Menu
    # Toolbar
    # Elements
    if config["window"]["module"]:
        callback_module = importlib.import_module(config["window"]["module"])
    else:
        callback_module = None
    set_missing_element_values(config["element"],
                               config["window"]["variable_group"],
                               callback_module,
                               gui)
    set_missing_menu_values(config["menu"], callback_module)

#def set_missing_element_values(element, parent_group, parent_module, variables, getvar, setvar):
def set_missing_element_values(element, parent_group, parent_module, gui):

    for el in element:

        el["visible"] = True

        if "id" not in el:
            el["id"] = ""
        if "variable_group" not in el:
            el["variable_group"] = parent_group
        if "module" not in el:
            el["module"] = parent_module
        else:
            if type(el["module"]) == str:
                el["module"] = importlib.import_module(el["module"])
        if el["style"] == "tabpanel":
            # Loop through tabs
            for tab in el["tab"]:

                # Backward compatibility
                if "string" in tab:
                    tab["text"] = tab["string"]

                if "variable_group" not in tab:
                    tab["variable_group"] = el["variable_group"]
                if "module" not in tab:
                    tab["module"] = el["module"]
                else:
                    if type(tab["module"]) == str:
                        try:
                            tab["module"] = importlib.import_module(tab["module"])
                        except:
                            print("Error! Could not import module " + tab["module"] + " ...")
                if "element" in tab:
                    set_missing_element_values(tab["element"],
                                               tab["variable_group"],
                                               tab["module"],
                                               gui)
        elif el["style"] == "panel":

            # Backward compatibility
            if "title" in el:
                el["text"] = el["title"]

            if "text" not in el:
                el["text"] = ""

            if "element" in el:
                set_missing_element_values(el["element"],
                                           el["variable_group"],
                                           el["module"],
                                           gui)
        else:
            # Variable type
            if "variable" in el:
                group = el["variable_group"]
                name = el["variable"]
                el["type"] = str
                if group in gui.variables:
                    if name in gui.variables[group]:
                        el["type"] = type(gui.variables[group][name]["value"])

            # Special for popupmenus and listboxes
            if el["style"] == "popupmenu" or el["style"] == "listbox":

                if "select" not in el:
                    # Either 'index' or 'item'
                    el["select"] = "item"
                #                        raise Exception("Error! select not specified in element with style " + el["style"])
                if el["select"] == "item":
                    # Item
                    # Bith option_value and option_string must always be present
                    if "option_string" not in el:
                        raise Exception("Error! option_string not specified in element with style " + el["style"])
                    if "option_value" not in el:
                        el["option_value"] = el["option_string"]
#                        raise Exception("Error! option_value not specified in element with style " + el["style"])

                else:
                    # Index
                    # Only option_string must always be present
                    # option_value is ignored
                    if "option_string" not in el:
                        raise Exception("Error! option_string not specified in element with style " + el["style"])

                if "option_value" in el:
                    if type(el["option_value"]) == dict:
                        if "variable_group" not in el["option_value"]:
                            el["option_value"]["variable_group"] = el["variable_group"]
                if type(el["option_string"]) == dict:
                    if "variable_group" not in el["option_string"]:
                        el["option_string"]["variable_group"] = el["variable_group"]

            if el["style"] == "pushselectfile" or el["style"] == "pushloadfile":
                if "title" not in el:
                    el["title"] = "Open file"
                if "filter" not in el:
                    el["filter"] = "All files (*.*)"

            if el["style"] == "pushsavefile":
                if "title" not in el:
                    el["title"] = "Save file"
                if "filter" not in el:
                    el["filter"] = "All files (*.*)"

            if "dependency" in el:
                for dep in el["dependency"]:
                    for check in dep["check"]:
                        if "variable_group" not in check:
                            check["variable_group"] = parent_group

            # TODO
            # Icon paths
#            if "icon" in el:
#                el["icon"] = os.path.join(self.config_path, el["icon"])

            # Other missing default values
            default = {}
            default["text"] = ""
            default["dependency"] = []
            default["enable"] = True
            default["text_position"] = "left"
            for key, val in default.items():
                if key not in el:
                    el[key] = val

def set_missing_menu_values(menu_list, parent_module):
#    if isinstance(menu_list, list):
    for menu in menu_list:
        # Set missing values
        # First module
        if "module" not in menu:
            menu["module"] = parent_module
        else:
            if type(menu["module"]) == str:
                try:
                    menu["module"] = importlib.import_module(menu["module"])
                except:
                    print("Error in menu! Module " + menu["module"] + " not found!")
        # And now others
        default = {}
        default["checkable"] = False
        default["separator"] = False
        default["id"] = ""
        default["option"] = ""
        for key, val in default.items():
            if key not in menu:
                menu[key] = val

        if "menu" in menu:
            set_missing_menu_values(menu["menu"], menu["module"])


def add_elements(element_list, parent, gui):

    for element in element_list:

        if element["style"] == "tabpanel":

            from .pyqt5.tabpanel import TabPanel
            element["widget"] = TabPanel(element, parent, gui)

            for tab in element["tab"]:
                # And now add the elements in this tab
                if tab["element"]:
                    add_elements(tab["element"],
                                 tab["widget"],
                                 gui)

        elif element["style"] == "panel":

            # Add frame
            from .pyqt5.frame import Frame
            element["widget"] = Frame(element, parent, gui)

            # And now add the elements in this frame
            if "element" in element:
                add_elements(element["element"],
                             element["widget"],
                             gui)

        else:

            # Add push-buttons etc.
            if element["style"] == "pushbutton":
                from .pyqt5.pushbutton import PushButton
                element["widget"] = PushButton(element, parent, gui)

            elif element["style"] == "edit":
                from .pyqt5.edit import Edit
                element["widget"] = Edit(element, parent, gui)

            elif element["style"] == "datetimeedit":
                from .pyqt5.date_edit import DateEdit
                element["widget"] = DateEdit(element, parent, gui)

            elif element["style"] == "text":
                from .pyqt5.text import Text
                element["widget"] = Text(element, parent, gui)

            elif element["style"] == "popupmenu":
                from .pyqt5.popupmenu import PopupMenu
                element["widget"] = PopupMenu(element, parent, gui)

            elif element["style"] == "listbox":
                from .pyqt5.listbox import ListBox
                element["widget"] = ListBox(element, parent, gui)

            elif element["style"] == "checkbox":
                from .pyqt5.checkbox import CheckBox
                element["widget"] = CheckBox(element, parent, gui)

            elif element["style"] == "radiobuttongroup":
                from .pyqt5.radiobuttongroup import RadioButtonGroup
                element["widget"] = RadioButtonGroup(element, parent, gui)

            elif element["style"] == "slider":
                from .pyqt5.slider import Slider
                element["widget"] = Slider(element, parent, gui)

            elif element["style"] == "pushselectfile":
                from .pyqt5.pushopenfile import PushOpenFile
                element["widget"] = PushOpenFile(element, parent, gui)

            elif element["style"] == "pushsavefile":
                from .pyqt5.pushsavefile import PushSaveFile
                element["widget"] = PushSaveFile(element, parent, gui)

            elif element["style"] == "mapbox":
                from .pyqt5.mapbox.mapbox import MapBox
                element["widget"] = MapBox(element, parent, gui)
            elif element["style"] == "webpage":
                from .pyqt5.webpage import WebPage
                element["widget"] = WebPage(element, parent, gui)

            else:
                print("Element style " + element["style"] + " not recognized!")

            # And set the values
            if element["style"] != "radiobuttongroup": # Cannot set radiobutton group to visible
                if "widget" in element:
                    element["widget"].setVisible(True)

def set_elements(element_list):
    for element in element_list:
        try:
            if element["visible"]:
                if element["style"] == "tabpanel":
                    index = element["widget"].currentIndex()
                    for j, tab in enumerate(element["tab"]):
                        # And now add the elements in this tab
                        if tab["element"] and j==index:
                            set_elements(tab["element"])
                elif element["style"] == "panel":
                    # And now set the elements in this frame
                    if "element" in element:
                        set_elements(element["element"])
                else:
                    # And set the values
                    if "widget" in element:
                        # Set the values
                        element["widget"].set()
                        # Set the dependencies
                        set_dependencies(element)
        except Exception as err:
            print(err)



def find_element_by_id(element, element_id):
    element_found = None
    for el in element:
        if el["style"] == "tabpanel":
            for tab in el["tab"]:
                # Look for elements in this tab
                if tab["element"]:
                    element_found = find_element_by_id(tab["element"], element_id)
                    if element_found:
                        return element_found
        elif el["style"] == "panel":
            # Look for elements in this frame this frame
            if "element" in el:
                element_found = find_element_by_id(el["element"], element_id)
                if element_found:
                    return element_found
        else:
            if "id" in el:
                if el["id"] == element_id:
                    return el
    return None

def find_menu_item_by_id(menu, menu_id):
    for menu_item in menu:
        if "id" in menu_item:
            if menu_item["id"] == menu_id:
                return menu_item
        if "menu" in menu_item:
            item = find_menu_item_by_id(menu_item["menu"], menu_id)
            if item:
                return item
    return None

def set_menu_items(menu):
    for menu_item in menu:
        if "id" in menu_item:
            if menu_item["id"] == menu_id:
                return menu_item
        if "menu" in menu_item:
            item = find_menu_item_by_id(menu_item["menu"], menu_id)
            if item:
                return item
    return None

def resize_elements(element_list, parent, resize_factor):
    for element in element_list:
        if element["style"] == "tabpanel":
            x0, y0, wdt, hgt = get_position(element["position"], parent, resize_factor)
#            hgt = hgt + int(20 * resize_factor)
            tab_panel = element["widget"]
            tab_panel.setGeometry(x0, y0, wdt, hgt)
            for tab in element["tab"]:
                widget = tab["widget"]
                widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))
                # And resize elements in this tab
                if tab["element"]:
                    resize_elements(tab["element"], widget, resize_factor)
        elif element["style"] == "panel":
            x0, y0, wdt, hgt = get_position(element["position"], parent, resize_factor)
            element["widget"].setGeometry(x0, y0, wdt, hgt)
            if hasattr(element["widget"], "text_widget"):
                # Also change title widget
                element["widget"].text_widget.setGeometry(x0 + 10, y0 - 9, element["text_width"], 16)
                element["widget"].text_widget.setAlignment(QtCore.Qt.AlignTop)
            if "element" in element:
                if element["position"]["height"] < 0:
                    resize_elements(element["element"], element["widget"], resize_factor)
        elif element["style"] == "mapbox":
            x0, y0, wdt, hgt = get_position(element["position"], parent, resize_factor)
            element["widget"].view.setGeometry(x0, y0, wdt, hgt)
        elif element["style"] == "webpage":
            x0, y0, wdt, hgt = get_position(element["position"], parent, resize_factor)
            element["widget"].view.setGeometry(x0, y0, wdt, hgt)
        elif element["style"] == "radiobuttongroup":
            nbuttons = len(element["option_value"])
            x0, y0, wdt, hgt = get_position(element["position"], parent, resize_factor)
            yll = y0 + hgt - int(nbuttons * 20 * resize_factor)
            for i in range(nbuttons):
                element["widget"].buttons()[i].setGeometry(x0,
                                                           int(yll + i * 20 * resize_factor),
                                                           wdt,
                                                           int(20 * resize_factor))
        else:
            if "widget" not in element:
                continue
            x0, y0, wdt, hgt = get_position(element["position"], parent, resize_factor)
            element["widget"].setGeometry(x0, y0, wdt, hgt)
            if hasattr(element["widget"], "text_widget"):
                # Also change title widget
                label = element["widget"].text_widget
                fm = label.fontMetrics()
                wlab = fm.size(0, element["text"]).width()
                if element["text_position"] == "above-center" or element["text_position"] == "above":
                    label.setAlignment(QtCore.Qt.AlignCenter)
                    label.setGeometry(x0, y0 - 20, wdt, 20)
                elif element["text_position"] == "above-left":
                    label.setAlignment(QtCore.Qt.AlignLeft)
                    label.setGeometry(x0, y0 - 20, wlab, 20)
                else:
                    # Assuming left
                    label.setAlignment(QtCore.Qt.AlignRight)
                    label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, 20)

def get_position(position, parent, resize_factor):

    # TO DO: relative positions!

    x0 = position["x"] * resize_factor
    y0 = position["y"] * resize_factor
    wdt = 10
    hgt = 10
    if "width" in position:
        wdt = position["width"] * resize_factor
    if "height" in position:
        hgt = position["height"] * resize_factor

    if x0>0:
        if wdt>0:
            pass
        else:
            wdt = parent.geometry().width() - x0 + wdt
    else:
        if wdt>0:
            x0 = parent.geometry().width() - wdt + x0
        else:
            x0 = parent.geometry().width() + x0
            wdt = parent.geometry().width() - x0 + wdt

    if y0>0:
        if hgt>0:
            y0 = parent.geometry().height() - (y0 + hgt)
        else:
            y0 = - hgt
            hgt = parent.geometry().height() - position["y"] * resize_factor + hgt
    else:
        if hgt>0:
            y0 = parent.geometry().width() - hgt
        else:
            hgt = - y0 - hgt
            y0 = parent.geometry().width() - (y0 + hgt)

    x0 = int(x0)
    y0 = int(y0)
    wdt = int(wdt)
    hgt = int(hgt)

    return x0, y0, wdt, hgt


def set_dependencies(element):
    if element["dependency"]:
        for dep in element["dependency"]:
            try:
                getvar = element["widget"].gui.getvar
                if dep["checkfor"] == "all":
                    okay = True
                    for check in dep["check"]:
                        name  = check["variable"]
                        group = check["variable_group"]
                        value = getvar(group, name)
                        if type(check["value"]) == dict:
                            check_value = getvar(check["value"]["variable_group"], check["value"]["variable"])
                        else:
                            check_value = check["value"]
                            if type(value) == int:
                                check_value = int(check_value)
                            elif type(value) == float:
                                check_value = float(check_value)
                        # if self.check_variables(name=name, group=group):
                        if check["operator"] == "eq":
                            if value != check_value:
                                okay = False
                                break
                        elif check["operator"] == "ne":
                            if value == check_value:
                                okay = False
                                break
                        elif check["operator"] == "gt":
                            if value <= check_value:
                                okay = False
                                break
                        elif check["operator"] == "ge":
                            if value < check_value:
                                okay = False
                                break
                        elif check["operator"] == "lt":
                            if value >= check_value:
                                okay = False
                                break
                        elif check["operator"] == "le":
                            if value > check_value:
                                okay = False
                                break
                elif dep["checkfor"] == "any":
                    okay = False
                    for check in dep["check"]:
                        name  = check["variable"]
                        group = check["variable_group"]
                        value = getvar(group, name)
                        if type(check["value"]) == dict:
                            check_value = getvar(check["value"]["variable_group"], check["value"]["variable"])
                        else:
                            check_value = check["value"]
                            if type(value) == int:
                                check_value = int(check_value)
                            elif type(value) == float:
                                check_value = float(check_value)
                        # if self.check_variables(name=name, group=group):
                        if check["operator"] == "eq":
                            if value == check_value:
                                okay = True
                                break
                        elif check["operator"] == "ne":
                            if value != check_value:
                                okay = True
                                break
                        elif check["operator"] == "gt":
                            if value > check_value:
                                okay = True
                                break
                        elif check["operator"] == "ge":
                            if value >= check_value:
                                okay = True
                                break
                        elif check["operator"] == "lt":
                            if value < check_value:
                                okay = True
                                break
                        elif check["operator"] == "le":
                            if value <= check_value:
                                okay = True
                                break
                elif dep["checkfor"] == "none":
                    okay = True
                    for check in dep["check"]:
                        name  = check["variable"]
                        group = check["variable_group"]
                        value = getvar(group, name)
                        if type(check["value"]) == dict:
                            check_value = getvar(check["value"]["variable_group"], check["value"]["variable"])
                        else:
                            check_value = check["value"]
                            if type(value) == int:
                                check_value = int(check_value)
                            elif type(value) == float:
                                check_value = float(check_value)
                        if check["operator"] == "eq":
                            if value == check_value:
                                okay = False
                                break
                        elif check["operator"] == "ne":
                            if value != check_value:
                                okay = False
                                break
                        elif check["operator"] == "gt":
                            if value > check_value:
                                okay = False
                                break
                        elif check["operator"] == "ge":
                            if value >= check_value:
                                okay = False
                                break
                        elif check["operator"] == "lt":
                            if value < check_value:
                                okay = False
                                break
                        elif check["operator"] == "le":
                            if value <= check_value:
                                okay = False
                                break
                if dep["action"] == "visible":
                    if okay:
                        element["widget"].setVisible(True)
                        if hasattr(element["widget"], "text_widget"):
                            element["widget"].text_widget.setVisible(True)
                    else:
                        element["widget"].setVisible(False)
                        if hasattr(element["widget"], "text_widget"):
                            element["widget"].text_widget.setVisible(False)
                elif dep["action"] == "enable":
                    if okay:
                        element["widget"].setEnabled(True)
                        element["widget"].setStyleSheet("")
                        if hasattr(element["widget"], "text_widget"):
                            element["widget"].text_widget.setVisible(True)
                    else:
                        element["widget"].setEnabled(False)
                        if hasattr(element["widget"], "text_widget"):
                            element["widget"].text_widget.setVisible(False)
            except:
                print("Error setting dependency !!!")

def check_variable(element):
    # Check whether variables exist
    if not "variable_group" in element:
        print("Error : no group specified for element !")
        return False
    group = element["variable_group"]
    if not name:
        name = element["variable"]
    if not group:
        group = element["variable_group"]
    if not name:
        print("Error : no variable name specified for element !")
        return False
    if not group:
        print("Error : no group specified for element !")
        return False
    # if not group in variables:
    #     print("Error : GUI variables do not include group '" + group + "' !")
    #     return False
    # if not name in variables[group]:
    #     print("Error : GUI variable group '" + group +
    #           "' does not include variable '" + name + "' !")
    #     return False

    return True

def yaml2dict(file_name):
    file = open(file_name,"r")
    dct = yaml.load(file, Loader=yaml.FullLoader)
    return dct

def run_server(server_path, server_port):
    os.chdir(server_path)
    PORT = server_port
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map['.js']     = 'text/javascript'
    Handler.extensions_map['.mjs']    = 'text/javascript'
    Handler.extensions_map['.css']    = 'text/css'
    Handler.extensions_map['.html']   = 'text/html'
    Handler.extensions_map['.json']   = 'application/json'
    print("Server path : " + server_path)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()
