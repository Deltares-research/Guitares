# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QFileDialog
from pathlib import Path


def openFileNameDialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                              str(Path(Ra2ceGUI.ra2ce_config['database']['path']).joinpath('static', 'hazard')),
                                              "All Files (*);;GeoTIFF files (*.tif)", options=options)
    if fileName:
        print(f"File selected: {fileName}")
        Ra2ceGUI.selected_floodmap = fileName
        Ra2ceGUI.gui.setvar("ra2ceGUI", "selected_floodmap", Path(fileName).name)


def openFileNamesDialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    files, _ = QFileDialog.getOpenFileNames("QFileDialog.getOpenFileNames()", "",
                                            "All Files (*);;Python Files (*.py)", options=options)
    if files:
        print(files)


def saveFileDialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getSaveFileName("QFileDialog.getSaveFileName()", "",
                                              "All Files (*);;Text Files (*.txt)", options=options)
    if fileName:
        print(fileName)