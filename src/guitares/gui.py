"""Main GUI class that initialises the Qt application, reads config, and builds the window."""

import copy
import importlib
import os
import shutil
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import toml
import yaml

from guitares.server import start_server
from guitares.window import Window


class GUI:
    """Top-level GUI object that owns the Qt application, configuration, and variables.

    Parameters
    ----------
    module : Any
        Application module with optional ``on_build`` callback.
    framework : str, optional
        Qt framework to use (``"pyqt5"`` or ``"pyside6"``), by default ``"pyqt5"``.
    splash_file : str or None, optional
        Path to splash screen image.
    stylesheet : str or None, optional
        Path to a Qt stylesheet file.
    config_path : str or None, optional
        Directory containing configuration files.
    config_file : str or None, optional
        Name of the GUI config file (YAML or TOML).
    icon : str or None, optional
        Path to the application icon file.
    server_path : str or None, optional
        Path to serve via the built-in HTTP server (for map tiles).
    server_port : int, optional
        HTTP server port, by default 3000.
    server_nodejs : bool, optional
        Use a Node.js server instead of the built-in Python server.
    js_messages : bool, optional
        Enable JavaScript message passing, by default ``True``.
    copy_map_server_folder : bool, optional
        Copy the map engine server folder to *server_path*, by default ``True``.
    icon_path : str or None, optional
        Directory containing icon PNG files to copy to the server folder.
    map_engine : str, optional
        Map engine to use (``"mapbox"`` or ``"maplibre"``), by default ``"mapbox"``.
    mapbox_token_file : str, optional
        Filename of the Mapbox access token, by default ``"mapbox_token.txt"``.
    """

    def __init__(
        self,
        module: Any,
        framework: str = "pyqt5",
        splash_file: Optional[str] = None,
        stylesheet: Optional[str] = None,
        config_path: Optional[str] = None,
        config_file: Optional[str] = None,
        icon: Optional[str] = None,
        server_path: Optional[str] = None,
        server_port: int = 3000,
        server_nodejs: bool = False,
        js_messages: bool = True,
        copy_map_server_folder: bool = True,
        icon_path: Optional[str] = None,
        map_engine: str = "mapbox",
        mapbox_token_file: str = "mapbox_token.txt",
    ) -> None:
        self.module: Any = module
        self.framework: str = framework
        self.splash_file: Optional[str] = splash_file
        self.stylesheet: Optional[str] = stylesheet
        self.config_file: Optional[str] = config_file
        self.config_path: Optional[str] = config_path
        self.map_engine: str = map_engine
        self.splash: Any = None
        self.icon: Optional[str] = icon
        self.config: Dict[str, Any] = {}
        self.variables: Dict[str, Dict[str, Any]] = {}
        self.server_thread: Any = None
        self.server_path: Optional[str] = server_path
        self.server_port: int = server_port
        self.server_nodejs: bool = server_nodejs
        self.js_messages: bool = js_messages
        self.popup_window: Dict[str, Any] = {}
        self.popup_data: Dict[str, Any] = {}
        self.resize_factor: float = 1.0

        if self.framework == "pyqt5":
            from PyQt5 import QtCore
            from PyQt5.QtWidgets import QApplication

        elif self.framework == "pyside6":
            from PySide6 import QtCore
            from PySide6.QtWidgets import QApplication

            import guitares.pyside6.icons_rc  # noqa: F401

        QtCore.QCoreApplication.setAttribute(QtCore.Qt.AA_ShareOpenGLContexts)
        self.qtapp = QApplication.instance()
        if self.qtapp is None:
            self.qtapp = QApplication(sys.argv)

        # Show splash screen
        self.show_splash()

        if not self.config_path:
            self.config_path = os.getcwd()

        if self.config_file:
            # Read configuration file
            self.config = self.read_gui_config(self.config_path, self.config_file)
        else:
            # No configuration file, so just set config to empty dict, which MUST be filled by the developer before calling build
            self.config = {}

        self.image_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "img"
        )
        self.image_path = self.image_path.replace(os.sep, "/")

        if server_path:
            # Need to run http server (e.g. for MapBox or MapLibre)
            print("Starting http server ...")
            # Run http server in separate thread
            # Use daemon=True to make sure the server stops after the application is finished
            if copy_map_server_folder:
                mppth = os.path.join(
                    os.path.dirname(os.path.abspath(__file__)),
                    "map",
                    self.map_engine,
                    "server",
                )
                # Delete current server folder (with safety check)
                if os.path.exists(server_path):
                    abs_path = os.path.abspath(server_path)
                    # Guard against deleting dangerous paths
                    if len(abs_path) < 10 or abs_path in (
                        os.path.expanduser("~"),
                        os.sep,
                        os.path.abspath(os.sep),
                    ):
                        raise ValueError(
                            f"Refusing to delete unsafe server_path: {abs_path}"
                        )
                    shutil.rmtree(server_path)
                # Now copy over folder from mapbox or maplibre
                shutil.copytree(mppth, server_path)

            # Check if mapbox token file exists in config path or in current working directory
            token_file_name = None
            if os.path.exists(os.path.join(self.config_path, mapbox_token_file)):
                token_file_name = os.path.join(self.config_path, mapbox_token_file)
            if os.path.exists(os.path.join(os.getcwd(), mapbox_token_file)):
                token_file_name = os.path.join(os.getcwd(), mapbox_token_file)

            # Read mapbox token and store in js file in server path
            if token_file_name:
                with open(token_file_name, "r") as fid:
                    mapbox_token = fid.readlines()
                with open(os.path.join(server_path, "mapbox_token.js"), "w") as fid:
                    fid.write(f"mapbox_token = '{mapbox_token[0].strip()}';")

            if icon_path:
                # Copy all files in icon_path to server_path/icons
                if not os.path.exists(os.path.join(server_path, "icons")):
                    os.mkdir(os.path.join(server_path, "icons"))
                for file in os.listdir(icon_path):
                    if file.endswith(".png"):
                        shutil.copy(
                            os.path.join(icon_path, file),
                            os.path.join(server_path, "icons", file),
                        )

            # Set map styles
            if self.map_engine == "mapbox":
                self.map_style = "mapbox://styles/mapbox/streets-v12"
            elif self.map_engine == "maplibre":
                self.map_style = "osm"

            start_server(server_path, port=server_port, node=self.server_nodejs)

    def show_splash(self) -> None:
        """Display the splash screen if a splash file was provided."""
        if self.splash_file:
            mod = importlib.import_module(f"guitares.{self.framework}.splash")
            self.splash = mod.Splash(self.splash_file, seconds=20.0).splash

    def close_splash(self) -> None:
        """Close the splash screen if it is currently visible."""
        if self.splash:
            self.splash.close()

    def build(self) -> None:
        """Build and display the main application window, then start the Qt event loop."""
        app = self.qtapp

        # Set the icon
        if self.framework == "pyqt5":
            from PyQt5 import QtGui
        elif self.framework == "pyside6":
            from PySide6 import QtGui

        app.setWindowIcon(QtGui.QIcon(self.icon))

        if self.stylesheet:
            app.setStyleSheet(
                open(os.path.join(self.config_path, self.stylesheet), "r").read()
            )

        # Make window object
        self.window = Window(self.config, self)
        self.window.build()
        self.window.resize()

        # Call on_build method after building window
        if hasattr(self.module, "on_build"):
            self.module.on_build()

        app.exec_()

    def setvar(self, group: str, name: str, value: Any) -> None:
        """Set a GUI variable value.

        Parameters
        ----------
        group : str
            Variable group name.
        name : str
            Variable name within the group.
        value : Any
            Value to store.
        """
        if group not in self.variables:
            self.variables[group] = {}
        if name not in self.variables[group]:
            self.variables[group][name] = {}
        self.variables[group][name]["value"] = value

    def getvar(self, group: str, name: Optional[str]) -> Any:
        """Get a GUI variable value.

        Parameters
        ----------
        group : str
            Variable group name.
        name : str or None
            Variable name within the group.

        Returns
        -------
        Any
            The stored value, or ``None`` if the group or name does not exist.
        """
        if name is None:
            # There is no variable for the element
            return None
        if group not in self.variables:
            print(
                f"Error! Cannot get variable! GUI variable group '{group}' not defined!"
            )
            return None
        elif name not in self.variables[group]:
            print(
                f"Error! Cannot get variable! GUI variable '{name}' not defined in group '{group}'!"
            )
            return None
        return self.variables[group][name]["value"]

    def delvar(self, group: str, name: str) -> None:
        """Delete a single GUI variable.

        Parameters
        ----------
        group : str
            Variable group name.
        name : str
            Variable name to delete.
        """
        if group not in self.variables:
            print(
                f"Error! Cannot delete variable! GUI variable group '{group}' not defined!"
            )
            return None
        elif name not in self.variables[group]:
            print(
                f"Error! Cannot delete variable! GUI variable '{name}' not defined in group '{group}'!"
            )
            return None
        del self.variables[group][name]

    def delgroup(self, group: str) -> None:
        """Delete an entire variable group.

        Parameters
        ----------
        group : str
            Variable group name to delete.
        """
        if group not in self.variables:
            print(
                f"Error! Cannot delete group! GUI variable group '{group}' not defined!"
            )
            return
        del self.variables[group]

    def popup(
        self,
        config: Any,
        id: str = "popup",
        data: Optional[Any] = None,
    ) -> Tuple[bool, Any]:
        """Open a popup dialog window and return the result.

        Parameters
        ----------
        config : str or dict
            Path to a YAML config file, or a configuration dictionary.
        id : str, optional
            Unique identifier for this popup, by default ``"popup"``.
        data : Any, optional
            Data to pass into the popup (returned on OK).

        Returns
        -------
        Tuple[bool, Any]
            ``(okay, data)`` where *okay* is ``True`` if OK was clicked.
        """
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

    def read_gui_config(self, path: str, file_name: str) -> Dict[str, Any]:
        """Read a GUI configuration file (YAML or TOML) into a dictionary.

        Parameters
        ----------
        path : str
            Directory containing the config file.
        file_name : str
            Config file name.

        Returns
        -------
        Dict[str, Any]
            Parsed configuration with ``window``, ``toolbar``, ``menu``,
            ``element``, and ``statusbar`` keys.
        """
        suffix = Path(path).joinpath(file_name).suffix
        if suffix == ".yml":
            d = yaml2dict(os.path.join(path, file_name))
        elif suffix == ".toml":
            d = toml.load(os.path.join(path, file_name))
        config: Dict[str, Any] = {}
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

    def read_gui_elements(self, path: str, file_name: str) -> List[dict]:
        """Recursively read GUI element definitions, resolving file references.

        Parameters
        ----------
        path : str
            Directory containing the config file.
        file_name : str
            Config file name.

        Returns
        -------
        List[dict]
            List of element dictionaries.
        """
        suffix = Path(path).joinpath(file_name).suffix
        if suffix == ".yml":
            d = yaml2dict(os.path.join(path, file_name))
        elif suffix == ".toml":
            d = toml.load(os.path.join(path, file_name))
        element = d["element"]
        for el in d["element"]:
            if el["style"] == "tabpanel":
                # Loop through tabs
                for tab in el["tab"]:
                    if "element" in tab:
                        if isinstance(tab["element"], str):
                            # Must be a file
                            tab["element"] = self.read_gui_elements(
                                path, tab["element"]
                            )
                    else:
                        tab["element"] = []
        return element

    def string_width(self, string: str) -> int:
        """Return the pixel width of a string rendered in the application font.

        Parameters
        ----------
        string : str
            Text to measure.

        Returns
        -------
        int
            Width in pixels.
        """
        font = self.qtapp.font()
        if self.framework == "pyqt5":
            from PyQt5.QtGui import QFontMetrics

            wdt = QFontMetrics(font).width(string)
        elif self.framework == "pyside6":
            from PySide6.QtGui import QFontMetrics

            wdt = QFontMetrics(font).horizontalAdvance(string)
        return wdt

    def quit(self) -> None:
        """Quit the Qt application."""
        self.qtapp.quit()


def yaml2dict(file_name: str) -> dict:
    """Load a YAML file and return its contents as a dictionary.

    Parameters
    ----------
    file_name : str
        Path to the YAML file.

    Returns
    -------
    dict
        Parsed YAML contents.
    """
    with open(file_name, "r") as f:
        dct = yaml.load(f, Loader=yaml.FullLoader)
    return dct
