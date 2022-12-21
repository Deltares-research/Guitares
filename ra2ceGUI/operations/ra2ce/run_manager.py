# -*- coding: utf-8 -*-
from ra2ceGUI import Ra2ceGUI
from src.guitools.pyqt5.io import openFolderNameDialog
from PyQt5.QtWidgets import QMessageBox

from pathlib import Path
import shutil

# class RunManager:
#     def __init__(self):


def checkFileExists(file_path: Path) -> bool:
    if file_path.is_file():
        return True
    else:
        return False


def getRunName():
    Ra2ceGUI.run_name = Ra2ceGUI.gui.getvar("ra2ceGUI", "run_name")
    print(f"Run name set to '{Ra2ceGUI.run_name}'")

    createNewRunFolders()


def createNewRunFolders():
    # Look what directories are already made. If the directory already exists, display a message.
    list_dir_names = [d.stem for d in Ra2ceGUI.ra2ce_config['database']['path'].glob('*') if d.is_dir()]
    if Ra2ceGUI.run_name in list_dir_names:
        Ra2ceGUI.gui.elements['run_name']['widget_group'].widgets[0].setStyleSheet(f'QWidget {{color: red;}}')
        Ra2ceGUI.gui.update()
        print("Run name already used, please choose another name.")

        # TODO: weghalen?
        Ra2ceGUI.current_project = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name)
    else:
        print(f"Create new run folders for '{Ra2ceGUI.run_name}'")
        Ra2ceGUI.current_project = Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name)

        Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name).mkdir(parents=True, exist_ok=False)
        Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'network').mkdir(
            parents=True, exist_ok=False)
        Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'hazard').mkdir(
            parents=True, exist_ok=False)
        Ra2ceGUI.ra2ce_config['database']['path'].joinpath(Ra2ceGUI.run_name, 'static', 'output_graph').mkdir(
            parents=True, exist_ok=False)

        # Copy the ini files
        for ini_file in ['network.ini', 'analyses.ini']:
            if checkFileExists(Ra2ceGUI.ra2ce_config['base_data']['path'].joinpath('templates', ini_file)):
                shutil.copy(Ra2ceGUI.ra2ce_config['base_data']['path'].joinpath('templates', ini_file),
                            Ra2ceGUI.current_project.joinpath(ini_file))
            else:
                print(f"The {ini_file} file is not found at {Ra2ceGUI.ra2ce_config['base_data']['path'].joinpath('templates', ini_file)}. "
                      f"Please ensure this 'base data' file is present in that location.")


def selectPreviousRun():
    _path = openFolderNameDialog(Ra2ceGUI.ra2ce_config['database']['path'])
    if _path:
        Ra2ceGUI.current_project = Path(_path)

        # Check if the ini files are present
        for ini_file in ['network.ini', 'analyses.ini']:
            if not Ra2ceGUI.current_project.joinpath(ini_file).is_file():
                print(f"{ini_file} not found at {Ra2ceGUI.current_project.joinpath(ini_file)}!"
                      f"Please choose a previous run folder with the '{ini_file}' present.")
                return

        # Update the run name and show in the GUI
        Ra2ceGUI.run_name = Ra2ceGUI.current_project.stem
        Ra2ceGUI.gui.setvar("ra2ceGUI", "run_name", Ra2ceGUI.run_name)
        Ra2ceGUI.gui.update()
