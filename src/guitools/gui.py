import os
import yaml
import importlib
import time
import sys

import http.server
import socketserver
from urllib.request import urlopen
from urllib.error import *
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore


class GUI:
    def __init__(self, module,
                 framework="pyqt5",
                 splash_file=None,
                 stylesheet=None,
                 config_path=None,
                 config_file=None,
                 server_path=None,
                 server_port=3000):

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

        if not self.config_path:
            self.config_path = os.getcwd()

        if server_path:
            # Need to run http server (e.g. for MapBox)
            # Check if something's already running on port 3000.
            try:
                html = urlopen("http://localhost:" + str(server_port) + "/")
                print("Found server running at port 3000 ...")
            except:
                print("Starting http server ...")
                # Run http server in separate thread
                # Use daemon=True to make sure the server stops after the application is finished
                thr = threading.Thread(target=run_server, args=(server_path, server_port), daemon=True)
                thr.start()

    def show_splash(self):
        if self.framework == "pyqt5" and self.splash_file:
            from .pyqt5.splash import Splash
            self.splash = Splash(os.path.join(self.config_path, self.splash_file), seconds=2.0).splash

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

        self.map_widget = {}
        
        if self.config_file:
            self.config["window"] = window
            self.config["menu"] = menu
            self.config["toolbar"] = toolbar
            self.config["element"] = element
            # Read element file
            self.read_gui_config(self.config_path, self.config_file)

        self.set_missing_config_values()

        # Add main window
        if self.framework=="pyqt5":        
            from .pyqt5.main_window import MainWindow


        self.main_window = MainWindow(self.config)
#        self.main_window.resize_factor = 1.0

        # Add menu
        if self.config["menu"]:
            from .pyqt5.menu import Menu
            Menu(self.config["menu"], self.main_window)

        # Add toolbar
        
        # Add elements
        self.add_elements(self.config["element"], self.main_window)

        self.update()
                    
#            self.main_window.resize_function = lambda: gui.resize()
#            self.main_window.statusBar().showMessage('Message in statusbar.')
        self.main_window.show()

        self.module.on_build()

        app.exec_()

#        if self.framework=="pyqt5":        
#            app.exec_()

    def add_elements(self, element_list, parent):
        
        for element in element_list:

            if "text" in element:
                if element["text"]=="Number of breakpoints":
                    shite=1
            if "window" not in element:
                element["window"] = self.main_window

            if element["style"] == "tabpanel":

                from .pyqt5.tabpanel import TabPanel
                TabPanel(element, parent)

                for tab in element["tab"]:
                    # And now add the elements in this tab
                    if tab["element"]:
                        self.add_elements(tab["element"],
                                          tab["widget"])

            elif element["style"] == "panel":

                # Add frame
                from .pyqt5.frame import Frame
                Frame(element, parent)
                element["widget"].setVisible(True)

                # And now add the elements in this frame
                if "element" in element:
                    self.add_elements(element["element"],
                                      element["widget"])

            else:

                # Add push-buttons etc.
                if element["style"] == "pushbutton":
                    from .pyqt5.pushbutton import PushButton
                    element["widget_group"] = PushButton(element, parent)

                elif element["style"] == "edit":
                    from .pyqt5.edit import Edit
                    element["widget_group"] = Edit(element, parent)

                elif element["style"] == "datetimeedit":
                    from .pyqt5.date_edit import DateEdit
                    element["widget_group"] = DateEdit(element, parent)

                elif element["style"] == "popupmenu":
                    from .pyqt5.popupmenu import PopupMenu
                    element["widget_group"] = PopupMenu(element, parent)

                elif element["style"] == "listbox":
                    from .pyqt5.listbox import ListBox
                    element["widget_group"] = ListBox(element, parent)

                elif element["style"] == "olmap":
                    from .pyqt5.olmap import OlMap
                    element["widget_group"] = OlMap(element, parent)
                    self.map_widget[element["id"]] = element["widget_group"]

                elif element["style"] == "mapbox":
                    from .pyqt5.mapbox.mapbox import MapBox
#                    self.olmap[element["id"]] = MapBox(element, parent)
                    element["widget_group"] = MapBox(element,
                                                     parent,
                                                     self.server_path,
                                                     self.server_port)
                    self.map_widget[element["id"]] = element["widget_group"]

                elif element["style"] == "webpage":
                    from .pyqt5.webpage import WebPage
                    WebPage(element, parent)

                elif element["style"] == "slider":
                    from .pyqt5.slider import Slider
                    element["widget_group"] = Slider(element, parent)

                else:
                    print("Element style " + element["style"] + " not recognized!")

                # And set the values    
                if "widget_group" in element:
                    if hasattr(element["widget_group"], "widgets"):
                        for wdgt in element["widget_group"].widgets:
                            wdgt.setVisible(True)
#                    element["widget_group"].set()


    def read_gui_config(self, path, file_name):
        
        d = yaml2dict(os.path.join(path, file_name))
        
        if "window" in d:           
            self.config["window"]  = d["window"]
        if "menu" in d:           
            self.config["menu"]    = d["menu"]
        if "toolbar" in d:           
            self.config["toolbar"] = d["toolbar"]
        if "element" in d:
            # Recursively read elements 
            self.config["element"] = self.read_gui_elements(path, file_name)
    
    def read_gui_elements(self, path, file_name):
        # Return just the elements    
        d = yaml2dict(os.path.join(path, file_name))
        element = d["element"]
        for el in d["element"]:
            if el["style"] == "tabpanel":
                # Loop through tabs
                for tab in el["tab"]:
                    if "element" in tab:
                        if type(tab["element"]) == str:
                            # Must be a file
                            tab["element"] = self.read_gui_elements(path, tab["element"])
                    else:
                        tab["element"] = []
                        
        return element
    
    def set_missing_config_values(self):
    
        # Window
        if "width" not in self.config["window"]:
            self.config["window"]["width"] = 800
        if "height" not in self.config["window"]:
            self.config["window"]["height"] = 800
        if "title" not in self.config["window"]:
            self.config["window"]["title"] = ""
        if "module" not in self.config["window"]:
            self.config["window"]["module"] = None
        if "variable_group" not in self.config["window"]:
            self.config["window"]["variable_group"] = "_main"

        # Menu
            
        # Toolbar    
    
        # Elements
        if self.config["window"]["module"]:
            callback_module = importlib.import_module(self.config["window"]["module"])
        else:
            callback_module = None
        main_module = self.module

        set_missing_element_values(self.config["element"],
                                   self.config["window"]["variable_group"],
                                   callback_module,
                                   self.variables,
                                   self.getvar,
                                   self.setvar,
                                   main_module)

        set_missing_menu_values(self.config["menu"],
                                callback_module)


    def update(self):
        # Update all elements
        self.set_elements(self.config["element"], self.main_window)

    def update_tab(self, tab):
        # Update all elements in tab
        self.set_elements(self.config["element"], tab)
        
    def set_elements(self, element_list, parent):
        
        for element in element_list:

            if element["style"] == "tabpanel":
                for tab in element["tab"]:
                    # And now add the elements in this tab
                    if tab["element"]:
                        self.set_elements(tab["element"], tab["widget"])
            elif element["style"] == "panel":
                # And now add the elements in this frame
                if "element" in element:
                    self.set_elements(element["element"], element["widget"])
            else:
                # And set the values    
                # for el in element_list:
                #     if "widget_group" in el:
                #         el["widget_group"].set()
                if "widget_group" in element:
                    element["widget_group"].set()

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

def set_missing_element_values(element, parent_group, parent_module, variables, getvar, setvar, main_module):
    for el in element:
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
                if "variable_group" not in tab:
                    tab["variable_group"] = el["variable_group"]
                if "module" not in tab:
                    tab["module"] = el["module"]
                else:
                    if type(tab["module"]) == str:
                        tab["module"] = importlib.import_module(tab["module"])
                if "element" in tab:
                    set_missing_element_values(tab["element"],
                                           tab["variable_group"],
                                           tab["module"],
                                           variables,
                                           getvar,
                                           setvar,
                                           main_module)
        elif el["style"] == "panel":
            if "title" not in el:
                el["title"] = ""
            if "element" in el:
                set_missing_element_values(el["element"],
                                           el["variable_group"],
                                           el["module"],
                                           variables,
                                           getvar,
                                           setvar,
                                           main_module)

        else:

            # Setvar and getvar methods
            el["setvar"] = setvar
            el["getvar"] = getvar

            # Variable type
            if "variable" in el:
                group = el["variable_group"]
                name = el["variable"]
                el["type"] = str
                if group in variables:
                    if name in variables[group]:
                        el["type"] = type(variables[group][name]["value"])

            # Special for popupmenus and listboxes
            if el["style"] == "popupmenu" or el["style"] == "listbox":

                if "select" not in el:
                    # Either 'index' or 'item'
                    el["select"] = "item"
                #                        raise Exception("Error! select not specified in element with style " + el["style"])
                if el["select"] == "item":
                    # item
                    # option_value and option_string must always be present
                    if "option_string" not in el:
                        raise Exception("Error! option_string not specified in element with style " + el["style"])
                    if "option_value" not in el:
                        raise Exception("Error! option_value not specified in element with style " + el["style"])

                else:
                    # index
                    # option_string must always be present
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

            if "dependency" in el:
                for dep in el["dependency"]:
                    for check in dep["check"]:
                        if "variable_group" not in check:
                            check["variable_group"] = parent_group

            # Icon paths
#            if "icon" in el:
#                el["icon"] = os.path.join(self.config_path, el["icon"])

            # Other missing default values
            default = {}
            default["text"] = ""
            default["dependency"] = []
            default["enable"] = True
            for key, val in default.items():
                if key not in el:
                    el[key] = val


def set_missing_menu_values(menu_list, parent_module):
    if isinstance(menu_list, dict):
        # End node
        if "module" not in menu_list:
            menu_list["module"] = parent_module
        else:
            if type(menu_list["module"]) == str:
                try:
                    menu_list["module"] = importlib.import_module(menu_list["module"])
                except:
                    print("Error in menu! Module " + menu_list["module"] + " not found!")
        default = {}
        default["checkable"] = False
        default["separator"] = False
        default["id"] = ""
        default["option"] = ""
        for key, val in default.items():
            if key not in menu_list:
                menu_list[key] = val
    else:
        for menu in menu_list:
            if "module" not in menu:
                menu["module"] = parent_module
            else:
                if type(menu["module"]) == str:
                    try:
                        menu["module"] = importlib.import_module(menu["module"])
                    except:
                        print("Error in menu! Module " + menu["module"] + " not found!")
            if "menu" in menu:
                # Loop through tabs
                for sub_menu in menu["menu"]:
                    set_missing_menu_values(sub_menu,
                                            menu["module"])


def yaml2dict(file_name):
    file = open(file_name,"r")
    dct = yaml.load(file, Loader=yaml.FullLoader)
    return dct

def run_server(server_path, server_port):
#    global httpd
    os.chdir(server_path)
    PORT = server_port
    Handler = http.server.SimpleHTTPRequestHandler
    Handler.extensions_map['.js']     = 'text/javascript'
    Handler.extensions_map['.mjs']    = 'text/javascript'
    Handler.extensions_map['.css']    = 'text/css'
    Handler.extensions_map['.html']   = 'text/html'
    Handler.extensions_map['main.js'] = 'module'
    print("Server path : " + server_path)
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print("Serving at port", PORT)
        httpd.serve_forever()
