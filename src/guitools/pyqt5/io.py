# -*- coding: utf-8 -*-
from PyQt5.QtWidgets import QFileDialog
from typing import Union, Optional
from pathlib import Path
import logging


def openFileNameDialog(defaultOpenFolder: Union[str, Path], fileTypes: list) -> Optional[str]:
    options = QFileDialog.Options()
    options |= QFileDialog.DontUseNativeDialog
    fileName, _ = QFileDialog.getOpenFileName(None, "QFileDialog.getOpenFileName()",
                                              str(defaultOpenFolder),
                                              ";;".join(fileTypes), options=options)
    if fileName:
        logging.info(f"File selected: {fileName}")
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
        logging.info(f"Folder selected: {folderName}")
        return folderName
    else:
        return None
