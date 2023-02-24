from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="radiobutton.yml",
                       splash_file="c:\\work\\checkouts\\svn\\OET\\matlab\\applications\\DelftDashBoard\\settings\\icons\\DelftDashBoard.jpg")

        # Define GUI variables
        self.gui.setvar("radiobutton", "button", 2)
        self.gui.setvar("radiobutton", "response", "Button 2 is checked.")

app = Application()
