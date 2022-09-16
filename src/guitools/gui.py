import os
import yaml
import importlib

import http.server
import socketserver
from urllib.request import urlopen
from urllib.error import *
import threading


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
        self.server_path = server_path
        self.server_port = server_port

        if not self.config_path:
            self.config_path = os.getcwd()

        if server_path:

            # Check if something's already running on port 3000.
            try:
                html = urlopen("http://localhost:" + str(server_port) + "/")
                print("Found server running at port 3000 ...")
            except:
                print("Starting http server ...")
#                threading.Thread(target=run_server(server_path, server_port)).start()
                threading.Thread(target=run_server).start()



    def show_splash(self):
        if self.framework == "pyqt5" and self.splash_file:
            from .pyqt5.splash import Splash
            self.splash = Splash(os.path.join(self.config_path, self.splash_file), seconds=2.0).splash

    def close_splash(self):
        if self.splash:
            self.splash.close()

    def build(self, app,
              window={},
              menu={},
              toolbar={},
              element=[]):


        if self.stylesheet:
            app.setStyleSheet(open(os.path.join(self.config_path, self.stylesheet), "r").read())

        self.config["window"]  = window
        self.config["menu"]    = menu
        self.config["toolbar"] = toolbar
        self.config["element"] = element

        self.map_widget = {}
        
        if self.config_file:
            # Read element file
            self.read_gui_config(self.config_path, self.config_file)

        self.set_missing_config_values()

        # Add main window
        if self.framework=="pyqt5":        
            from .pyqt5.main_window import MainWindow


        self.main_window = MainWindow(self.config)
#        self.main_window.resize_factor = 1.0

        # Add menu
        
        # Add toolbar
        
        # Add elements
        self.add_elements(self.config["element"], self.main_window)
                    
#            self.main_window.resize_function = lambda: gui.resize()
#            self.main_window.statusBar().showMessage('Message in statusbar.')
        self.main_window.show()

#        if self.framework=="pyqt5":        
#            app.exec_()


    def add_elements(self, element_list, parent):
        
        for element in element_list:

            if "window" not in element:
                element["window"] = self.main_window

            if element["style"] == "tabpanel":

                from .pyqt5.tabpanel import TabPanel
                TabPanel(parent, self, element)

                for tab in element["tab"]:
                    # And now add the elements in this tab
                    if tab["element"]:
                        self.add_elements(tab["element"],
                                          tab["widget"])

            elif element["style"] == "panel":

                # Add frame
                from .pyqt5.frame import Frame
                Frame(element, parent)

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

                elif element["style"] == "olmap":
                    from .pyqt5.olmap import OlMap
                    element["widget_group"] = OlMap(element, parent)
                    self.map_widget[element["id"]] = element["widget_group"]

                elif element["style"] == "mapbox":
                    from .pyqt5.mapbox import MapBox
#                    self.olmap[element["id"]] = MapBox(element, parent)
                    element["widget_group"] = MapBox(element,
                                                     parent,
                                                     self.server_path,
                                                     self.server_port)
                    self.map_widget[element["id"]] = element["widget_group"]

                elif element["style"] == "webpage":
                    from .pyqt5.webpage import WebPage
                    WebPage(element, parent)

                if element["style"] == "slider":
                    from .pyqt5.slider import Slider
                    element["widget_group"] = Slider(element, parent)

                # And set the values    
                if "widget_group" in element:
                    element["widget_group"].set()
        
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
                for tab in element["tab"]:
                    if type(tab["element"]) == str:
                        # Must be a file
                        tab["element"] = self.read_gui_elements(path, tab["element"])
                        
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
        self.set_missing_element_values(self.config["element"],
                                        self.config["window"]["variable_group"],
                                        callback_module,
                                        main_module)

    def set_missing_element_values(self, element, parent_group, parent_module, main_module):
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
                for tab in element["tab"]:
                    if "variable_group" not in tab:
                        tab["variable_group"] = el["variable_group"]
                    if "module" not in tab:
                        tab["module"] = el["module"]
                    else:
                        if type(tab["module"]) == str:
                            tab["module"] = importlib.import_module(tab["module"])
                    self.set_missing_element_values(tab["element"],
                                                    tab["variable_group"],
                                                    el["module"],
                                                    main_module)
            elif el["style"] == "panel":
                self.set_missing_element_values(el["element"],
                                                el["variable_group"],
                                                el["module"],
                                                main_module)

            else:

                # Setvar and getvar methods
                el["setvar"] = self.setvar
                el["getvar"] = self.getvar
                
                # Variable type                
                if "variable" in el:
                    group = el["variable_group"]
                    name  = el["variable"]
                    el["type"] = type(self.variables[group][name]["value"])
                
                # Special for popupmenus and listboxes
                if el["style"] == "popupmenu":
                    if type(el["option_value"]) == dict:
                        if "variable_group" not in el["option_value"]:
                            el["option_value"]["variable_group"] = el["variable_group"]
                    if type(el["option_string"]) == dict:
                        if "variable_group" not in el["option_string"]:
                            el["option_string"]["variable_group"] = el["variable_group"]

                # Icon paths
                if "icon" in el:
                    el["icon"] = os.path.join(self.config_path, el["icon"])

                # Other missing default values
                default = {}
                default["text"]       = ""
                default["dependency"] = []
                default["enable"]     = True
                for key, val in default.items():
                    if key not in el:
                        el[key] = val



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
                for el in element_list:
                    if "widget_group" in el:
                        el["widget_group"].set()
        
    def setvar(self, group, name, value):
        if group not in self.variables:
            self.variables[group] = {}
        if name not in self.variables[group]:
            self.variables[group][name] = {}
        self.variables[group][name]["value"] = value


    def getvar(self, group, name):
        if group not in self.variables:
            print("Error! GUI variable group '" + group + "' not defined !")
        elif name not in self.variables[group]:
            print("Error! GUI variable '" + name + "' not defined in group '" + group + "'!")
        return self.variables[group][name]["value"]

            
def yaml2dict(file_name):
    file = open(file_name,"r")
    dct = yaml.load(file, Loader=yaml.FullLoader)
    return dct

#def run_server(server_path, server_port):
def run_server():

    # server_path = "d:\\checkouts\\github\\GUITools\\examples\\visualdelta\\server"
    server_path = r'C:\Users\winter_ga\PycharmProjects\ddb\GUITools\examples\visualdelta\server'
    server_port = 3000

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
