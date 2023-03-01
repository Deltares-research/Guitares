# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

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
