"""Application window: builds the main or popup window, manages elements, menus, and dialogs."""

import importlib
import os
import pathlib
from typing import Any, List, Optional, Tuple

from guitares.dialog import window_dialog
from guitares.element import Element
from guitares.menu import Menu


class MenuBar:
    """Container for the window's menu bar widget."""

    def __init__(self) -> None:
        self.parent: Any = None
        self.widget: Any = None


class Window:
    """Represents a main or popup application window.

    Parameters
    ----------
    config_dict : dict
        Parsed GUI configuration dictionary.
    gui : Any
        The parent :class:`~guitares.gui.GUI` instance.
    type : str, optional
        Window type: ``"main"`` or ``"popup"``, by default ``"main"``.
    data : Any, optional
        Arbitrary data passed to popup windows.
    """

    def __init__(
        self,
        config_dict: dict,
        gui: Any,
        type: str = "main",
        data: Any = None,
    ) -> None:
        self.type: str = type
        self.gui: Any = gui
        self.data: Any = data
        self.width: int = 800
        self.height: int = 600
        self.minimum_width: int = 400
        self.minimum_height: int = 300
        self.maximize: bool = False
        self.fixed_size: bool = False
        self.title: str = ""
        self.module: Any = None
        self.variable_group: str = "_main"
        self.method: Optional[str] = None
        self.icon: Optional[str] = None
        self.modal: bool = False
        self.okay_method: Any = None
        if "width" in config_dict["window"]:
            self.width = config_dict["window"]["width"]
        if "height" in config_dict["window"]:
            self.height = config_dict["window"]["height"]
        if "minimum_width" in config_dict["window"]:
            self.minimum_width = config_dict["window"]["minimum_width"]
        else:
            self.minimum_width = self.width
        if "minimum_height" in config_dict["window"]:
            self.minimum_height = config_dict["window"]["minimum_height"]
        else:
            self.minimum_height = self.height
        if "maximize" in config_dict["window"]:
            self.maximize = config_dict["window"]["maximize"]
        if "fixed_size" in config_dict["window"]:
            self.fixed_size = config_dict["window"]["fixed_size"]
        if "title" in config_dict["window"]:
            self.title = config_dict["window"]["title"]
        if "module" in config_dict["window"]:
            self.module = importlib.import_module(config_dict["window"]["module"])
        if "method" in config_dict["window"]:
            self.method = config_dict["window"]["method"]
        if "variable_group" in config_dict["window"]:
            self.variable_group = config_dict["window"]["variable_group"]
        if "icon" in config_dict["window"]:
            self.icon = config_dict["window"]["icon"]
        if "modal" in config_dict["window"]:
            self.modal = config_dict["window"]["modal"]
        if self.module and "okay_method" in config_dict["window"]:
            self.okay_method = getattr(
                self.module, config_dict["window"]["okay_method"]
            )
        if self.fixed_size:
            self.maximize = False
        self.elements: List[Element] = []
        self.menus: List[Menu] = []
        self.toolbar: list = []
        self.statusbar: Any = {}

        if self.type == "popup":
            # Add OK and Cancel elements
            cancel = {
                "style": "pushbutton",
                "text": "Cancel",
                "position": {"x": -100, "y": 10, "width": 50, "height": 20},
                "method": self.cancel,
                "dependency": [],
                "enable": True,
            }
            ok = {
                "style": "pushbutton",
                "text": "OK",
                "position": {"x": -30, "y": 10, "width": 50, "height": 20},
                "method": self.ok,
                "dependency": [],
                "enable": True,
            }
            config_dict["element"].append(cancel)
            config_dict["element"].append(ok)

        self.add_elements_to_tree(config_dict["element"], self, self)
        if "menu" in config_dict:
            self.add_menu_to_tree(self.menus, config_dict["menu"], self)

        self.statusbar_fields: list = []  # temporary list
        if "statusbar" in config_dict:
            if "field" in config_dict["statusbar"]:
                for field in config_dict["statusbar"]["field"]:
                    self.statusbar_fields.append(field)

    def add_elements_to_tree(
        self, dcts: List[dict], parent: Any, window: "Window"
    ) -> None:
        """Recursively parse element dictionaries and attach them to the parent.

        Parameters
        ----------
        dcts : List[dict]
            List of element configuration dictionaries.
        parent : Any
            Parent element, tab, or window.
        window : Window
            The window these elements belong to.
        """
        parent.elements = []
        for dct in dcts:
            element = Element(dct, parent, window)
            if element.style == "tabpanel":
                for itab, tab_dct in enumerate(dct["tab"]):
                    if "element" in tab_dct:
                        self.add_elements_to_tree(
                            tab_dct["element"], element.tabs[itab], window
                        )
            elif dct["style"] == "panel":
                if "element" in dct:
                    self.add_elements_to_tree(dct["element"], element, window)
            parent.elements.append(element)

    def add_menu_to_tree(
        self, menu_list: List[Menu], dcts: List[dict], parent: Any
    ) -> None:
        """Recursively parse menu dictionaries into Menu objects.

        Parameters
        ----------
        menu_list : List[Menu]
            List to append parsed Menu objects to.
        dcts : List[dict]
            List of menu configuration dictionaries.
        parent : Any
            Parent menu or window.
        """
        for dct in dcts:
            menu = Menu(dct, parent)
            if "menu" in dct:
                self.add_menu_to_tree(menu.menus, dct["menu"], menu)
            menu_list.append(menu)

    def build(self) -> Any:
        """Create the Qt window, add all elements and menus, and show it.

        Returns
        -------
        Any
            The framework-specific window widget.
        """
        if self.gui.framework == "pyqt5":
            from PyQt5.QtWidgets import QVBoxLayout, QWidget
        elif self.gui.framework == "pyside6":
            from PySide6.QtWidgets import (
                QVBoxLayout,
                QWidget,
            )

        if self.type == "main":
            # Add main window

            mod = importlib.import_module(f"guitares.{self.gui.framework}.main_window")
            window = mod.MainWindow(self)

            # Add menu
            menu_bar = MenuBar()
            menu_bar.widget = window.menuBar()
            self.add_menus(self.menus, menu_bar, self.gui)

            # Add toolbar
            # TODO

            # Central widget
            central_widget = QWidget()
            layout = QVBoxLayout()
            central_widget.setLayout(layout)
            window.setCentralWidget(central_widget)
            self.widget = central_widget
            self.window_widget = window

        else:
            # Add pop-up window
            mod = importlib.import_module(f"guitares.{self.gui.framework}.popup_window")
            window = mod.PopupWindow(self)
            self.widget = window

        # Add elements
        self.add_elements(self.elements)

        # Add status bar (unless it is an empty dict)
        if self.statusbar_fields:
            mod = importlib.import_module(f"guitares.{self.gui.framework}.statusbar")
            self.statusbar = mod.StatusBar(self)

        # Set elements
        self.update()

        if self.maximize:
            window.showMaximized()

        window.show()

        # Check if a call start up callback function is needed
        if self.module and self.method:
            start_up_fcn = getattr(self.module, self.method)
            start_up_fcn()
            # Set elements again
            self.update()

        self.resize()

        if self.type == "popup":
            window.exec_()

        return window

    def ok(self, *args: Any) -> None:
        """Handle OK button click in popup windows."""
        # If there is no okay method or the okay method returns True, close the window. Otherwise, do nothing.
        if not self.okay_method or self.okay_method():
            self.widget.done(1)

    def cancel(self, *args: Any) -> None:
        """Handle Cancel button click in popup windows."""
        self.widget.done(0)

    def closeEvent(self, event: Any) -> None:
        """Handle window close event (currently a no-op).

        Parameters
        ----------
        event : Any
            Qt close event.
        """
        pass

    def update(self) -> None:
        """Refresh all element values, dependencies, and menu states."""
        self.set_elements(self.elements)
        self.set_menus(self.menus)

    def resize(self) -> None:
        """Recalculate geometry for all elements after a window resize."""
        self.resize_elements(self.elements)

    def add_elements(self, elements: List[Element]) -> None:
        """Recursively instantiate widgets for all elements.

        Parameters
        ----------
        elements : List[Element]
            Elements to add.
        """
        for element in elements:
            if element.style == "tabpanel":
                # Add tab panel
                element.add()
                # Loop through tabs in tab panel
                for tab in element.tabs:
                    # And now add the elements in this tab
                    if tab.elements:
                        self.add_elements(tab.elements)
            elif element.style == "panel":
                # Add panel
                element.add()
                # And now add the elements in this frame
                if element.elements:
                    self.add_elements(element.elements)
            else:
                element.add()

    def set_elements(self, elements: List[Element]) -> None:
        """Recursively set widget values and apply dependencies.

        Parameters
        ----------
        elements : List[Element]
            Elements to update.
        """
        for element in elements:
            try:
                if element.visible:
                    if element.style == "tabpanel":
                        # Set possible tab dependencies
                        element.set_dependencies()
                        # Only update the elements in the active tab
                        index = element.widget.currentIndex()
                        # Loop through elements in tab
                        for j, tab in enumerate(element.tabs):
                            # Check if tab has elements
                            if tab.elements and j == index:
                                # And now add the elements in this tab
                                self.set_elements(tab.elements)
                    elif element.style == "panel":
                        # Set the dependencies
                        element.set_dependencies()
                        # Check if this frame has elements
                        if element.elements:
                            # Set elements in this frame
                            self.set_elements(element.elements)
                    else:
                        # Set the element values
                        element.widget.set()
                        # Set the dependencies
                        element.set_dependencies()
            except Exception as err:
                print(err)

    def find_element_by_id(
        self, element_id: str, elements: Optional[List[Element]] = None
    ) -> Optional[Element]:
        """Search the element tree for an element with the given ID.

        Parameters
        ----------
        element_id : str
            The element ID to search for.
        elements : List[Element] or None, optional
            Subtree to search; defaults to the window's top-level elements.

        Returns
        -------
        Element or None
            The matching element, or ``None`` if not found.
        """
        element_found = None
        if elements is None:
            elements = self.elements
        for element in elements:
            if element.id == element_id:
                return element
            if element.style == "tabpanel":
                # Loop through tabs
                for tab in element.tabs:
                    # Look for elements in this tab
                    if tab.elements:
                        element_found = self.find_element_by_id(
                            element_id, elements=tab.elements
                        )
                        if element_found:
                            return element_found
            elif element.style == "panel":
                # Look for elements in this frame
                if element.elements:
                    element_found = self.find_element_by_id(
                        element_id, elements=element.elements
                    )
                    if element_found:
                        return element_found
        return None

    def resize_elements(self, elements: List[Element]) -> None:
        """Recursively recalculate geometry for all elements.

        Parameters
        ----------
        elements : List[Element]
            Elements to resize.
        """
        for element in elements:
            # Set geometry of this element
            element.set_geometry()
            # Check for children
            if element.style == "tabpanel":
                # Loop through tabs
                for tab in element.tabs:
                    # And resize elements in this tab
                    if tab.elements:
                        self.resize_elements(tab.elements)
            elif element.style == "panel":
                self.resize_elements(element.elements)

    def add_menus(self, menus: List[Menu], parent: Any, gui: Any) -> None:
        """Recursively create framework-specific menu widgets.

        Parameters
        ----------
        menus : List[Menu]
            Menu items to add.
        parent : Any
            Parent menu bar or menu.
        gui : Any
            The GUI instance.
        """
        for menu in menus:
            menu.parent = parent
            menu.gui = gui
            menu.add()
            if menu.menus:
                self.add_menus(menu.menus, menu, gui)

    def add_menu_from_dict(
        self, menu_dict: dict, parent_id: str, has_children: bool = False
    ) -> None:
        """Dynamically add a menu item from a dictionary at runtime.

        Parameters
        ----------
        menu_dict : dict
            Menu configuration dictionary.
        parent_id : str
            ID of the parent menu item.
        has_children : bool, optional
            Whether the new menu should be a submenu.
        """
        parent = self.find_menu_item_by_id(parent_id)
        menu = Menu(menu_dict, parent)
        parent.menus.append(menu)
        menu.add(has_children=has_children)

    def set_menus(self, menus: List[Menu]) -> None:
        """Recursively apply dependency rules to all menu items.

        Parameters
        ----------
        menus : List[Menu]
            Menu items to update.
        """
        for menu in menus:
            if menu.menus:
                self.set_menus(menu.menus)
            else:
                menu.set_dependencies()

    def find_menu_item_by_id(
        self, menu_id: str, menus: Optional[List[Menu]] = None
    ) -> Optional[Menu]:
        """Search the menu tree for a menu item with the given ID.

        Parameters
        ----------
        menu_id : str
            The menu item ID to search for.
        menus : List[Menu] or None, optional
            Subtree to search; defaults to the window's top-level menus.

        Returns
        -------
        Menu or None
            The matching menu item, or ``None`` if not found.
        """
        if menus is None:
            menus = self.menus
        for menu in menus:
            if menu.id == menu_id:
                return menu
            item = self.find_menu_item_by_id(menu_id, menus=menu.menus)
            if item:
                return item
        return None

    def dialog_ok_cancel(self, text: str, title: str = " ") -> Any:
        """Show an OK/Cancel dialog.

        Parameters
        ----------
        text : str
            Message to display.
        title : str, optional
            Dialog title.

        Returns
        -------
        Any
            Dialog result.
        """
        return window_dialog(self, text, type="question", title=title)

    def dialog_yes_no(self, text: str, title: str = " ") -> Any:
        """Show a Yes/No dialog.

        Parameters
        ----------
        text : str
            Message to display.
        title : str, optional
            Dialog title.

        Returns
        -------
        Any
            Dialog result.
        """
        return window_dialog(self, text, type="question_yes_no", title=title)

    def dialog_custom(
        self,
        text: str,
        title: str = " ",
        button_text: Optional[List[str]] = None,
    ) -> Any:
        """Show a dialog with custom button labels.

        Parameters
        ----------
        text : str
            Message to display.
        title : str, optional
            Dialog title.
        button_text : List[str] or None, optional
            Custom button labels.

        Returns
        -------
        Any
            Dialog result.
        """
        return window_dialog(
            self, text, type="custom", title=title, button_text=button_text
        )

    def dialog_warning(self, text: str, title: str = "Warning") -> None:
        """Show a warning dialog.

        Parameters
        ----------
        text : str
            Warning message.
        title : str, optional
            Dialog title, by default ``"Warning"``.
        """
        window_dialog(self, text, type="warning", title=title)

    def dialog_info(self, text: str, title: str = " ") -> None:
        """Show an informational dialog.

        Parameters
        ----------
        text : str
            Message to display.
        title : str, optional
            Dialog title.
        """
        window_dialog(self, text, type="info", title=title)

    def dialog_auto_close(self, text: str, timeout: int = 1500) -> None:
        """Show a dialog that closes automatically after a timeout.

        Parameters
        ----------
        text : str
            Message to display.
        timeout : int, optional
            Auto-close timeout in milliseconds, by default 1500.
        """
        window_dialog(self, text, type="auto_close", timeout=timeout)

    def dialog_fade_label(self, text: str, timeout: int = 1500) -> None:
        """Show a fading label dialog.

        Parameters
        ----------
        text : str
            Message to display.
        timeout : int, optional
            Fade timeout in milliseconds, by default 1500.
        """
        window_dialog(self, text, type="fade_label", timeout=timeout)

    def dialog_critical(self, text: str, title: str = "Critical") -> None:
        """Show a critical error dialog.

        Parameters
        ----------
        text : str
            Error message.
        title : str, optional
            Dialog title, by default ``"Critical"``.
        """
        window_dialog(self, text, type="critical", title=title)

    def dialog_progress(self, text: str, nmax: int, title: str = " ") -> Any:
        """Show a progress dialog.

        Parameters
        ----------
        text : str
            Progress message.
        nmax : int
            Maximum progress value.
        title : str, optional
            Dialog title.

        Returns
        -------
        Any
            The progress dialog object.
        """
        dlg = window_dialog(self, text, title=title, type="progress", nmax=nmax)
        return dlg

    def dialog_wait(self, text: str, title: str = " ") -> Any:
        """Show a wait/busy dialog.

        Parameters
        ----------
        text : str
            Wait message.
        title : str, optional
            Dialog title.

        Returns
        -------
        Any
            The wait dialog object.
        """
        dlg = window_dialog(self, text, title=title, type="wait")
        return dlg

    def dialog_open_file(
        self,
        text: str,
        filter: str,
        path: Optional[str] = None,
        file_name: Optional[str] = None,
        selected_filter: Optional[str] = None,
        allow_directory_change: bool = True,
        multiple: bool = False,
    ) -> Tuple[Any, str, str, str, Any]:
        """Show a file-open dialog.

        Parameters
        ----------
        text : str
            Dialog prompt text.
        filter : str
            File filter string.
        path : str or None, optional
            Initial directory.
        file_name : str or None, optional
            Pre-filled file name.
        selected_filter : str or None, optional
            Pre-selected file filter.
        allow_directory_change : bool, optional
            If ``False``, reject files from other directories.
        multiple : bool, optional
            Allow selecting multiple files.

        Returns
        -------
        Tuple[Any, str, str, str, Any]
            ``(full_name, path, name, extension, filter)`` or all empty strings
            on cancel.
        """
        if path is None:
            path = os.getcwd()
        dialog_type = "open_files" if multiple else "open_file"
        results = window_dialog(
            self,
            text,
            type=dialog_type,
            path=path,
            file_name=file_name,
            filter=filter,
            selected_filter=selected_filter,
        )
        full_name = results[0]
        if not full_name:
            return "", "", "", "", ""
        fltr = results[1]
        pth = pathlib.Path(full_name[0] if multiple else full_name)
        if not allow_directory_change:
            if str(pth.parent) != path:
                self.dialog_warning(
                    "Sorry, you cannot select a file from another directory !"
                )
                return "", "", "", "", ""
        path = str(pth.parent)
        name = pth.name
        ext = pth.suffix
        return full_name, path, name, ext, fltr

    def dialog_save_file(
        self,
        text: str,
        filter: str,
        path: Optional[str] = None,
        file_name: Optional[str] = None,
        selected_filter: Optional[str] = None,
        allow_directory_change: bool = True,
    ) -> Tuple[Any, str, str, str, Any]:
        """Show a file-save dialog.

        Parameters
        ----------
        text : str
            Dialog prompt text.
        filter : str
            File filter string.
        path : str or None, optional
            Initial directory.
        file_name : str or None, optional
            Pre-filled file name.
        selected_filter : str or None, optional
            Pre-selected file filter.
        allow_directory_change : bool, optional
            If ``False``, reject paths outside the initial directory.

        Returns
        -------
        Tuple[Any, str, str, str, Any]
            ``(full_name, path, name, extension, filter)`` or all empty strings
            on cancel.
        """
        if path is None:
            path = os.getcwd()
        results = window_dialog(
            self,
            text,
            type="save_file",
            path=path,
            file_name=file_name,
            filter=filter,
            selected_filter=selected_filter,
        )
        full_name = results[0]
        if not full_name:
            return "", "", "", "", ""
        fltr = results[1]
        pth = pathlib.Path(full_name)
        if not allow_directory_change:
            if str(pth.parent) != path:
                self.dialog_warning(
                    "Sorry, you cannot save this file to another directory !"
                )
                return "", "", "", "", ""
        path = str(pth.parent)
        name = pth.name
        ext = pth.suffix
        return full_name, path, name, ext, fltr

    def dialog_select_path(
        self, text: str, path: Optional[str] = None
    ) -> Optional[str]:
        """Show a directory selection dialog.

        Parameters
        ----------
        text : str
            Dialog prompt text.
        path : str or None, optional
            Initial directory.

        Returns
        -------
        str or None
            Selected directory path, or ``None`` on cancel.
        """
        new_path = window_dialog(
            self, text, filter=filter, type="select_path", path=path
        )
        return new_path

    def dialog_string(self, text: str, title: str = " ") -> Any:
        """Show a text-input dialog.

        Parameters
        ----------
        text : str
            Prompt text.
        title : str, optional
            Dialog title.

        Returns
        -------
        Any
            The entered string, or ``None`` on cancel.
        """
        return window_dialog(self, text, type="string", title=title)

    def dialog_popupmenu(
        self,
        text: str,
        title: str = " ",
        options: Optional[List[str]] = None,
    ) -> Any:
        """Show a popup-menu selection dialog.

        Parameters
        ----------
        text : str
            Prompt text.
        title : str, optional
            Dialog title.
        options : List[str] or None, optional
            List of selectable options.

        Returns
        -------
        Any
            The selected option.
        """
        if options is None:
            options = []
        return window_dialog(self, text, type="popupmenu", title=title, options=options)
