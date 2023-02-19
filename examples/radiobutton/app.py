from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="radiobutton.yml")

        # Define GUI variables
        self.gui.setvar("radiobutton", "button", 2)
        self.gui.setvar("radiobutton", "response", "Button 2 is checked.")

app = Application()
