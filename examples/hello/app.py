from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="hello.yml")

        # Define GUI variables
        self.gui.setvar("hello", "name", "")
        self.gui.setvar("hello", "response", "Hello, person whose name I do not yet know.")

app = Application()
