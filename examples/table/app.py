from pathlib import Path

import pandas as pd
from guitares.gui import GUI

class Application:
    def __init__(self):

        # Initialize GUI
        self.gui = GUI(self,
                       config_file="table.yml",
                       config_path=str(Path(__file__).resolve().parent))

        # Define GUI variables
        df = pd.DataFrame({"name": ["a2", "a1", "a3"], "path": ["pa2", "pa1", "pa3"]})
        self.gui.setvar("table", "dataframe", df)
        self.gui.setvar("table", "selected_row", [0])


app = Application()
