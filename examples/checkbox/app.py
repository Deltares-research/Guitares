from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="checkbox.yml")

        # Define GUI variables
        self.gui.setvar("checkbox", "checked", False)
        self.gui.setvar("checkbox", "response", "The box is not checked.")

app = Application()
