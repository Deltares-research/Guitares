import pandas as pd
from app import app
        
def button(*args):
    df = pd.DataFrame({"name": ["b1", "a2", "a3"], "path": ["pa1", "pa2", "pa3"]})
    app.gui.setvar("table", "dataframe", df)

def select(*args):
    df = app.gui.getvar("table", "dataframe")
    name = df.loc[args[0][0], "name"]
    app.gui.setvar("table", "response", f"row {name} selected")