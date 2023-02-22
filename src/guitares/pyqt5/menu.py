import traceback

class Menu:
    def __init__(self, menu):
        menu.widget = menu.parent.widget.addMenu("&" + menu.text)
        if menu.separator:
            menu.parent.widget.addSeparator()

class Action:
    def __init__(self, menu):
        menu.widget = menu.parent.widget.addAction("&" + menu.text)
        if menu.checkable:
            menu.widget.setCheckable(True)
        if menu.callback:
            menu.widget.triggered.connect(lambda state, f=menu.callback, o=menu.option: self.menu_item_selected(f, o))
        if menu.separator:
            menu.parent.widget.addSeparator()

    def menu_item_selected(self, callback, option):
        try:
            callback(option)
        except:
            traceback.print_exc()
