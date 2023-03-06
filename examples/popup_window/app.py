from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="main_window.yml")

        # Define GUI variables
        self.gui.setvar("main", "response", "No response given.")
        self.gui.setvar("popup", "string_in_popup_window", "")

app = Application()
