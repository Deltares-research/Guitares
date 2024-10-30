import traceback

class Menu:
    def __init__(self, menu):
        menu.widget = menu.parent.widget.addMenu("&" + menu.text)
        if menu.separator:
            menu.parent.widget.addSeparator()

class Action:
    def __init__(self, menu):
        menu.widget = menu.parent.widget.addAction("&" + menu.text)
        self.menu = menu
        if menu.checkable:
            menu.widget.setCheckable(True)
        if menu.callback:
            menu.widget.triggered.connect(lambda state, f=menu.callback, o=menu.option: self.menu_item_selected(f, o))
        if menu.separator:
            menu.parent.widget.addSeparator()

    def menu_item_selected(self, callback, option):
        try:
            # Check if widget is checkable
            if self.menu.checkable:
                # Check if widget is checked
                if self.menu.widget.isChecked():
                    checked = True
                else:
                    checked = False
                # If there is a variable, set it
                if self.menu.variable_group and self.menu.variable:
                    self.menu.setvar(self.menu.variable_group, self.menu.variable, checked)
            # Should change this so that it always sends option and checked?
            if self.menu.variable_group and self.menu.variable:
                callback(option, checked)
            else:
                callback(option)
        except:
            traceback.print_exc()
