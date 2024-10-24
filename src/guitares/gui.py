import os
import yaml
import sys
import copy
import shutil

from pathlib import Path
import toml
from PyQt5.QtWidgets import QApplication
from PyQt5 import QtCore, QtGui

from guitares.window import Window
from guitares.server import start_server

import guitares.icons_rc

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
                 server_nodejs=False,
                 js_messages=True,
                 copy_mapbox_server_folder=True,
                 icon_path=None,
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
        self.server_thread = None
        self.server_nodejs = server_nodejs
        self.js_messages = js_messages
        self.popup_window = {}
        self.popup_data   = {}
        self.resize_factor = 1.0        

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        self.qtapp = QApplication(sys.argv)

        # Show splash screen
        self.show_splash()

        if not self.config_path:
            self.config_path = os.getcwd()

        self.image_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "img")
        self.image_path = self.image_path.replace(os.sep, '/')

        if server_path:
            # Need to run http server (e.g. for MapBox)
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
          
            # Check if mapbox token file exists in config path or in current working directory
            token_file_name = None    
            if os.path.exists(os.path.join(self.config_path, mapbox_token_file)):
                token_file_name = os.path.join(self.config_path, mapbox_token_file)
            if os.path.exists(os.path.join(os.getcwd(), mapbox_token_file)):
                token_file_name = os.path.join(os.getcwd(), mapbox_token_file)    

            # Read mapbox token and store in js file in server path
            if token_file_name:
                fid = open(token_file_name, "r")
                mapbox_token = fid.readlines()
                fid.close()
                fid = open(os.path.join(server_path, "mapbox_token.js"), "w")
                fid.write("mapbox_token = '" + mapbox_token[0].strip() + "';")
                fid.close()

            if icon_path:
                # Copy all files in icon_path to server_path/icons
                if not os.path.exists(os.path.join(server_path, "icons")):
                    os.mkdir(os.path.join(server_path, "icons"))
                for file in os.listdir(icon_path):
                    if file.endswith(".png"):
                        shutil.copy(os.path.join(icon_path, file), os.path.join(server_path, "icons", file))

            start_server(server_path, port=server_port, node=self.server_nodejs)

    def show_splash(self):
        if self.framework == "pyqt5" and self.splash_file:
            from .pyqt5.splash import Splash
            self.splash = Splash(self.splash_file, seconds=20.0).splash

    def close_splash(self):
        if self.splash:
            self.splash.close()

    def build(self):

        app = self.qtapp

        # Set the icon
        app.setWindowIcon(QtGui.QIcon(self.icon))

        if self.stylesheet:
            app.setStyleSheet(open(os.path.join(self.config_path, self.stylesheet), "r").read())

        if self.config_file:
            self.config = self.read_gui_config(self.config_path, self.config_file)

        # Make window object
        self.window = Window(self.config, self)
        self.window.build()

        # Call on_build method after building window
        if hasattr(self.module, "on_build"):
            self.module.on_build()
            
        # # # Close splash screen before GUI is initiated

        app.exec_()

    def setvar(self, group, name, value):
        if group not in self.variables:
            self.variables[group] = {}
        if name not in self.variables[group]:
            self.variables[group][name] = {}
        self.variables[group][name]["value"] = value

    def getvar(self, group, name):
        if name is None:
            # There is no variable for the element
            return None
        if group not in self.variables:
            print("Error! Cannot get variable! GUI variable group '" + group + "' not defined!")
            return None
        elif name not in self.variables[group]:
            print("Error! Cannot get variable! GUI variable '" + name + "' not defined in group '" + group + "'!")
            return None
        return self.variables[group][name]["value"]
    
    def delvar(self, group, name):
        if group not in self.variables:
            print("Error! Cannot delete variable! GUI variable group '" + group + "' not defined!")
            return None
        elif name not in self.variables[group]:
            print("Error! Cannot delete variable! GUI variable '" + name + "' not defined in group '" + group + "'!")
            return None
        del self.variables[group][name]

    def popup(self, config, id="popup", data=None):
        # Make pop-up window
        # config needs to be file name of yml file, or configuration dict
        # Data is optional and can have any shape (e.g. dict, str, object, etc.)
        # Data will only be changed if Okay is clicked in the pop-up window
        if isinstance(config, str):
            path = os.path.dirname(config)
            file_name = os.path.basename(config)
            config = self.read_gui_config(path, file_name)
        if data:    
            self.popup_data[id] = copy.copy(data)
        else:
            self.popup_data[id] = None    
        self.popup_window[id] = Window(config, self, type="popup")
        p = self.popup_window[id].build()
        okay = False
        if p.result() == 1:
            okay = True
            data = self.popup_data[id]
        # Remove popup window and data    
        return okay, data

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
        config["statusbar"] = {}
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
        if "statusbar" in d:
            config["statusbar"] = d["statusbar"]
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

    def quit(self):
        QApplication.quit()

def yaml2dict(file_name):
    file = open(file_name,"r")
    dct = yaml.load(file, Loader=yaml.FullLoader)
    return dct
