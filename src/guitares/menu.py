import importlib

from guitares.dependencies import Dependency, DependencyCheck

class Text:
    def __init__(self, variable_group):
        self.variable       = ""
        self.variable_group = variable_group

class Menu:
    def __init__(self, dct, parent):
        self.style = None
        self.menus = []
        self.dependencies = []
        self.parent = parent
        self.text = ""
        self.option = None
        self.checkable = False
        self.separator = False
        self.dependencies = []
        self.visible = True
        self.enable = True
        self.id = ""
        self.variable_group = parent.variable_group
        self.module = parent.module
        self.method = ""
        self.callback = None
        self.gui = parent.gui
        self.getvar = parent.gui.getvar
        self.setvar = parent.gui.setvar
        self.icon = ""

        # Now update element attributes based on dict

        if "variable_group" in dct:
            self.variable_group = dct["variable_group"]
        if "id" in dct:
            self.id = dct["id"]
        if "option" in dct:
            self.option = dct["option"]
        if "checkable" in dct:
            self.checkable = dct["checkable"]
        if "separator" in dct:
            self.separator = dct["separator"]
        if "module" in dct:
            if type(dct["module"]) == str:
                try:
                    self.module = importlib.import_module(dct["module"])
                except:
                    print("Error! Could not import module " + dct["module"])
        if "method" in dct:
            self.method = dct["method"]
        if self.method and self.module:
            if hasattr(self.module, self.method):
                self.callback = getattr(self.module, self.method)
            else:
                print("Error! Could not find method " + self.method)
        if "text" in dct:
            if type(dct["text"]) == dict:
                self.text = Text(self.variable_group)
                if "variable" in dct:
                    self.text.variable(dct["variable"])
                if "variable_group" in dct:
                    self.text.variable_group(dct["variable_group"])
            else:
                self.text = dct["text"]

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


    def add(self):
        if self.menus:
            from .pyqt5.menu import Menu
            Menu(self)
        else:
            # End node
            from .pyqt5.menu import Action
            Action(self)

    def set_dependencies(self):
        for dependency in self.dependencies:
            okay = dependency.get()
            if dependency.action == "enable":
                if okay:
                    self.widget.setEnabled(True)
                else:
                    self.widget.setEnabled(False)
            elif dependency.action == "check":
                if okay:
                    self.widget.setChecked(True)
                else:
                    self.widget.setChecked(False)
