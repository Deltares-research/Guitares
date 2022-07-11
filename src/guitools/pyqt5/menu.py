import importlib


class PyQt5Menu:

    def __init__(self, menu_items, parent):
        menu = parent.menuBar()
        self.add_menu_item(menu, menu_items)

    def add_menu_item(self, menu, menu_items):
        # Recursively add menu items
        for menu_item in menu_items:
            if "menu_item" in menu_item:
                f = menu.addMenu("&" + menu_item["string"])
                self.add_menu_item(f, menu_item["menu_item"])
            else:
                f = menu.addAction(menu_item["string"])
                if "callback" in menu_item:
                    callback = menu_item["callback"]
                    option = menu_item["option"]
                    f.triggered.connect(lambda state, x=callback, y=option: menu_item_selected(x, y))
            menu_item["widget"] = f

    def menu_item_selected(self, callback, option):
        try:
            module = importlib.import_module(callback)
            module.callback(option)
        except:
            print(callback + ".py does not exist !")
