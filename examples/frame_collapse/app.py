import os
from guitares.gui import GUI

class Application:
    def __init__(self):

        self.main_path = os.path.dirname(os.path.abspath(__file__))
        self.server_path = os.path.join(self.main_path, "server")

        # Initialize GUI
        self.gui = GUI(self,
                       config_path=self.main_path,
                       server_path=self.server_path,
                       server_port=3000,
                       config_file="frame_collapse.yml")

        # Define GUI variables
        self.gui.setvar("frame_collapse", "collapsed", False)

app = Application()
