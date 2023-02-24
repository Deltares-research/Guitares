from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="menu_example.yml")

        # Define GUI variables
        self.gui.setvar("menu_example", "name", "")
        self.gui.setvar("menu_example", "response", "Hello, person whose name I do not yet know.")

app = Application()
