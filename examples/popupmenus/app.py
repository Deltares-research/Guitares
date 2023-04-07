from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="popupmenus.yml")

        # Define GUI variables
        self.gui.setvar("popupmenus", "a", "a1")
        self.gui.setvar("popupmenus", "value_a", ["a1", "a2", "a3"])
        self.gui.setvar("popupmenus", "text_a", ["A1", "A2", "A3"])

        self.gui.setvar("popupmenus", "b", "b2")

        self.gui.setvar("popupmenus", "c", 0)
        self.gui.setvar("popupmenus", "text_c", ["C1", "C2", "C3"])

        self.gui.setvar("popupmenus", "d", 0)

app = Application()
