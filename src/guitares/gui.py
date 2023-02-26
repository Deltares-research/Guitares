import os
import yaml
import importlib
import time
import sched
import sys
import copy
import shutil

from pathlib import Path
import toml
import http.server
import socketserver
from urllib.request import urlopen
from urllib.error import *
import threading
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui

from guitares.window import Window

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
        self.icon        = icon
        self.config      = {}
        self.variables   = {}
        self.server_thread = None
        self.server_path = server_path
        self.server_port = server_port
        self.js_messages = js_messages
        self.popup_data = None
        self.resize_factor = 1.0

        if not self.config_path:
            self.config_path = os.getcwd()

        if server_path:
            # Need to run http server (e.g. for MapBox)
            # Check if something's already running on port 3000
            try:
                html = urlopen("http://localhost:" + str(server_port) + "/")
                print("Found server running at port {} ...".format(server_port))
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

    def build(self):

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        app = QApplication(sys.argv)

        # Show splash screen
        self.show_splash()

        # Set the icon
        app.setWindowIcon(QtGui.QIcon(self.icon))

        if self.stylesheet:
            app.setStyleSheet(open(os.path.join(self.config_path, self.stylesheet), "r").read())

        if self.config_file:
            self.config = self.read_gui_config(self.config_path, self.config_file)

        # Make window object
        self.window = Window(self.config, self)

        window_widget = self.window.build()

        # Call on_build method after building window
        if hasattr(self.module, "on_build"):
            self.module.on_build()
            
        # Close splash screen before GUI is initiated
        self.close_splash()
        app.exec_()

    # def update(self):
    #     # Update all elements
    #     self.set_elements(self.window.elements)
    #     self.set_menus(self.window.menus)

    def update_tab(self):
        # Update all elements in tab
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

    def popup(self, config, data):
        if type(config) == str:
            path = os.path.dirname(config)
            file_name = os.path.basename(config)
            config = self.read_gui_config(path, file_name)
        self.popup_data = copy.copy(data)
        self.popup_window = Window(config, self, type="popup")
        p = self.popup_window.build()
        if p.result() == 1:
            data = self.popup_data
        return data

    def read_gui_config(self, path, file_name):
        suffix = Path(path).joinpath(file_name).suffix
        if suffix == '.yml':
            d = yaml2dict(os.path.join(path, file_name))
        elif suffix == '.toml':
            d = toml.load(os.path.join(path, file_name))
        config = {}
        config["window"] = {}
        config["toolbar"] = {}
        config["menu"] = []
        config["element"] = []
        if "window" in d:
            config["window"] = d["window"]
        if "toolbar" in d:
            config["toolbar"] = d["toolbar"]
        if "menu" in d:
            # Recursively read menu
            config["menu"] = d["menu"]
        if "element" in d:
            # Recursively read elements
            config["element"] = self.read_gui_elements(path, file_name)
        return config

    def read_gui_elements(self, path, file_name):
        # Return just the elements
        suffix = Path(path).joinpath(file_name).suffix
        if suffix == '.yml':
            d = yaml2dict(os.path.join(path, file_name))
        elif suffix == '.toml':
            d = toml.load(os.path.join(path, file_name))
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

    # def add_elements(self, elements):
    #     # Loop through elements list
    #     for element in elements:
    #         if element.style == "tabpanel":
    #             # Add tab panel
    #             element.add()
    #             # Loop through tabs in tab panel
    #             for tab in element.tabs:
    #                 # And now add the elements in this tab
    #                 if tab.elements:
    #                     self.add_elements(tab.elements)
    #         elif element.style == "panel":
    #             # Add panel
    #             element.add()
    #             # And now add the elements in this frame
    #             if element.elements:
    #                 self.add_elements(element.elements)
    #         else:
    #             element.add()
    #
    # def set_elements(self, elements):
    #     # Loop through elements list
    #     for element in elements:
    #         try:
    #             if element.visible:
    #                 if element.style == "tabpanel":
    #                     # Only update the elements in the active tab
    #                     index = element.widget.currentIndex()
    #                     # Loop through elements in tab
    #                     for j, tab in enumerate(element.tabs):
    #                         # Check if tab has elements
    #                         if tab.elements and j==index:
    #                             # And now add the elements in this tab
    #                             self.set_elements(tab.elements)
    #                 elif element.style == "panel":
    #                     # Check if this frame has elements
    #                     if element.elements:
    #                         # Set elements in this frame
    #                         self.set_elements(element.elements)
    #                 else:
    #                     # Set the element values
    #                     element.widget.set()
    #                     # Set the dependencies
    #                     element.set_dependencies()
    #         except Exception as err:
    #             print(err)

    # def find_element_by_id(self, elements, element_id):
    #     element_found = None
    #     for element in elements:
    #         if element.id == element_id:
    #             return element
    #         if element.style == "tabpanel":
    #             # Loop through tabs
    #             for tab in element.tabs:
    #                 # Look for elements in this tab
    #                 if tab.elements:
    #                     element_found = self.find_element_by_id(tab.elements, element_id)
    #                     if element_found:
    #                         return element_found
    #         elif element.style == "panel":
    #             # Look for elements in this frame
    #             if element.elements:
    #                 element_found = self.find_element_by_id(element.elements, element_id)
    #                 if element_found:
    #                     return element_found
    #     return None
    #
    # def resize_elements(self, elements, resize_factor):
    #     # Loop through elements
    #     for element in elements:
    #         # Set geometry of this element
    #         element.set_geometry()
    #         if element.style == "tabpanel":
    #             # Loop through tabs
    #             for tab in element.tabs:
    #                 # # Resize tab widgets
    #                 # tab.widget.setGeometry(0, 0, wdt, int(hgt - 20 * resize_factor))
    #                 # And resize elements in this tab
    #                 if tab.elements:
    #                     self.resize_elements(tab.elements, resize_factor)
    #         elif element.style == "panel":
    #             # If this panel is resizable, also update element positions of children
    #             if element.position.height < 0:
    #                 self.resize_elements(element.elements, resize_factor)

    # def add_menus(self, menus, parent, gui):
    #     # Loop through elements list
    #     for menu in menus:
    #         menu.parent = parent
    #         menu.gui = gui
    #         menu.add()
    #         if menu.menus:
    #             self.add_menus(menu.menus, menu, gui)
    #
    # def set_menus(self, menus):
    #     for menu in menus:
    #         if menu.menus:
    #             self.set_menus(menu.menus)
    #         else:
    #             menu.set_dependencies()

    # def find_menu_item_by_id(self, menus, menu_id):
    #     for menu in menus:
    #         if menu.id == menu_id:
    #             return menu
    #         item = find_menu_item_by_id(menu.menus, menu_id)
    #         if item:
    #             return item
    #     return None

# def check_variable(element):
#     # Check whether variables exist
#     if not "variable_group" in element:
#         print("Error : no group specified for element !")
#         return False
#     group = element["variable_group"]
#     if not name:
#         name = element["variable"]
#     if not group:
#         group = element["variable_group"]
#     if not name:
#         print("Error : no variable name specified for element !")
#         return False
#     if not group:
#         print("Error : no group specified for element !")
#         return False
#     # if not group in variables:
#     #     print("Error : GUI variables do not include group '" + group + "' !")
#     #     return False
#     # if not name in variables[group]:
#     #     print("Error : GUI variable group '" + group +
#     #           "' does not include variable '" + name + "' !")
#     #     return False
#
#     return True

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
