# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QFileDialog
from typing import Union, Optional
from pathlib import Path


def openFileNameDialog(defaultOpenFolder: Union[str, Path], fileTypes: list) -> Optional[str]:
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                              str(defaultOpenFolder),
                                              ";;".join(fileTypes), options=options)
    if fileName:
        print(f"File selected: {fileName}")
        return fileName
    else:
        return None


def openFolderNameDialog(defaultOpenFolder: Union[str, Path]):
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    folderName = QFileDialog.getExistingDirectory(None, caption='Select Directory',
                                                  directory=str(defaultOpenFolder),
                                                  options=options)

    if folderName:
        print(f"Folder selected: {folderName}")
        return folderName
    else:
        return None


def openFileNamesDialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    files, _ = QFileDialog.getOpenFileNames("QFileDialog.getOpenFileNames()", "",  # Perhaps None must be added as first argument
                                            "All Files (*);;Python Files (*.py)", options=options)
    if files:
        print(files)


def saveFileDialog():
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getSaveFileName("QFileDialog.getSaveFileName()", "",  # Perhaps None must be added as first argument
                                              "All Files (*);;Text Files (*.txt)", options=options)
    if fileName:
        print(fileName)