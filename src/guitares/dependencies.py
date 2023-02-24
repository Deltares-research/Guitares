import traceback

class DependencyCheck:
    def __init__(self, variable_group):
        self.variable       = ""
        self.variable_group = variable_group
        self.operator       = "eq"
        self.value          = None

class Dependency:
    def __init__(self):
        self.action         = "enable"
        self.checkfor       = "all"
        self.checks         = []

    def get(self):
        try:
            getvar = self.gui.getvar
            if self.checkfor == "all":
                okay = True
                for check in self.checks:
                    name = check.variable
                    group = check.variable_group
                    value = getvar(group, name)
                    if type(check.value) == dict:
                        check_value = getvar(check.value.variable_group, check.value.variable)
                    else:
                        check_value = check.value
                        if type(value) == int:
                            check_value = int(check_value)
                        elif type(value) == float:
                            check_value = float(check_value)
                    # if self.check_variables(name=name, group=group):
                    if check.operator == "eq":
                        if value != check_value:
                            okay = False
                            break
                    elif check.operator == "ne":
                        if value == check_value:
                            okay = False
                            break
                    elif check.operator == "gt":
                        if value <= check_value:
                            okay = False
                            break
                    elif check.operator == "ge":
                        if value < check_value:
                            okay = False
                            break
                    elif check.operator == "lt":
                        if value >= check_value:
                            okay = False
                            break
                    elif check.operator == "le":
                        if value > check_value:
                            okay = False
                            break
            elif self.checkfor == "any":
                okay = False
                for check in self.checks:
                    name = check.variable
                    group = check.variable_group
                    value = getvar(group, name)
                    if type(check.value) == dict:
                        check_value = getvar(check.value.variable_group, check.value.variable)
                    else:
                        check_value = check.value
                        if type(value) == int:
                            check_value = int(check_value)
                        elif type(value) == float:
                            check_value = float(check_value)
                    # if self.check_variables(name=name, group=group):
                    if check.operator == "eq":
                        if value == check_value:
                            okay = True
                            break
                    elif check.operator == "ne":
                        if value != check_value:
                            okay = True
                            break
                    elif check.operator == "gt":
                        if value > check_value:
                            okay = True
                            break
                    elif check.operator == "ge":
                        if value >= check_value:
                            okay = True
                            break
                    elif check.operator == "lt":
                        if value < check_value:
                            okay = True
                            break
                    elif check.operator == "le":
                        if value <= check_value:
                            okay = True
                            break
            elif self.checkfor == "none":
                okay = True
                for check in self.checks:
                    name = check.variable
                    group = check.variable_group
                    value = getvar(group, name)
                    if type(check.value) == dict:
                        check_value = getvar(check.value.variable_group, check.value.variable)
                    else:
                        check_value = check.value
                        if type(value) == int:
                            check_value = int(check_value)
                        elif type(value) == float:
                            check_value = float(check_value)
                    if check.operator == "eq":
                        if value == check_value:
                            okay = False
                            break
                    elif check.operator == "ne":
                        if value != check_value:
                            okay = False
                            break
                    elif check.operator == "gt":
                        if value > check_value:
                            okay = False
                            break
                    elif check.operator == "ge":
                        if value >= check_value:
                            okay = False
                            break
                    elif check.operator == "lt":
                        if value < check_value:
                            okay = False
                            break
                    elif check.operator == "le":
                        if value <= check_value:
                            okay = False
                            break
            return okay

        except:
            traceback.print_exc()
            return False
        