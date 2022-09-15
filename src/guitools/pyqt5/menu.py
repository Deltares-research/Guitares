import importlib


class Menu:

    def __init__(self, menu_list, parent):
        menu = parent.menuBar()
        self.add_menu(menu_list, menu)

    def add_menu(self, menu_list, parent):
        for menu in menu_list:
            if "menu" in menu:
                p = parent.addMenu("&" + menu["text"])
                self.add_menu(menu["menu"], p)
            else:
                p = parent.addAction("&" + menu["text"])
                if "checkable" in menu:
                    if menu["checkable"]:
                        p.setCheckable(True)
                # if "callback" in menu_item:
                #     callback = menu_item["callback"]
                #     option = menu_item["option"]
                #     f.triggered.connect(lambda state, x=callback, y=option: menu_item_selected(x, y))
            if "separator" in menu:
                if menu["separator"]:
                    parent.addSeparator()
            menu["widget"] = p

    #
    # def add_menu_item(self, menu, menu_items):
    #     # Recursively add menu items
    #     for menu_item in menu_items:
    #         if "menu_item" in menu_item:
    #             f = menu.addMenu("&" + menu_item["string"])
    #             self.add_menu_item(f, menu_item["menu_item"])
    #         else:
    #             f = menu.addAction(menu_item["string"])
    #             if "callback" in menu_item:
    #                 callback = menu_item["callback"]
    #                 option = menu_item["option"]
    #                 f.triggered.connect(lambda state, x=callback, y=option: menu_item_selected(x, y))
    #         menu_item["widget"] = f

    def menu_item_selected(self, callback, option):
        try:
            module = importlib.import_module(callback)
            module.callback(option)
        except:
            print(callback + ".py does not exist !")
