from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="listboxes.yml")

        # Define GUI variables
        self.gui.setvar("listboxes", "value_a", ["a1", "a2", "a3"])
        self.gui.setvar("listboxes", "text_a", ["A1", "A2", "A3"])
        self.gui.setvar("listboxes", "value_b", ["b1", "b2", "b3"])
        self.gui.setvar("listboxes", "text_b", ["B1", "B2", "B3"])
        self.gui.setvar("listboxes", "text_c", ["C1", "C2", "C3"])
        self.gui.setvar("listboxes", "text_d", ["D1", "D2", "D3"])

        self.gui.setvar("listboxes", "a", "a1")
        self.gui.setvar("listboxes", "b", ["b1"])
        self.gui.setvar("listboxes", "c", 0)
        self.gui.setvar("listboxes", "d", [0, 1])

app = Application()
