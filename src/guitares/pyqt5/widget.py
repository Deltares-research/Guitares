class Widget:
    def __init__(self, element, parent, gui):

        self.element       = element # Is this necessary?
        self.parent        = parent
        self.gui           = gui
        self.widgets       = []
        self.okay          = True

    def delete(self):
        for w in self.widgets:
            pass

    def set_dependencies(self):

        if self.element["dependency"]:

            for dep in self.element["dependency"]:

                try:

                    getvar = self.element["widget"].gui.getvar

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

                            if self.check_variables(name=name, group=group):
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

                            if self.check_variables(name=name, group=group):
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
                            if self.check_variables(name=name, group=group):
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
                            for w in self.widgets:
                                w.setVisible(True)
                        else:
                            for w in self.widgets:
                                w.setVisible(False)
                    elif dep["action"] == "enable":
                        if okay:
                            for w in self.widgets:
                                w.setEnabled(True)
                                w.setStyleSheet("")
                        else:
                            for w in self.widgets:
                                w.setEnabled(False)
                except:
                    print("Error setting dependency !!!")

    def check_variables(self, group=None, name=None):

        if not name:
            name = self.element["variable"]
        if not group:
            group = self.element["variable_group"]

        if not name:
            print("Error : no variable name specified for element !")
            return False
        if not group:
            print("Error : no variable name specified for element !")
            return False
        # if not group in variables:
        #     print("Error : GUI variables do not include group '" + group + "' !")
        #     return False
        # if not name in variables[group]:
        #     print("Error : GUI variable group '" + group +
        #           "' does not include variable '" + name + "' !")
        #     return False

        return True

    def set(self):
        pass
