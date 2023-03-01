# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5 import QtCore


class Frame:

    def __init__(self, element, parent):

        # Add tab panel
        frame = QFrame(parent)
        element["widget"] = frame
        element["parent"] = parent

        x0, y0, wdt, hgt = element["window"].get_position_from_string(element["position"], parent)

        frame.setGeometry(x0, y0, wdt, hgt)
        frame.setFrameShape(QFrame.StyledPanel)
        frame.setLineWidth(2)

        if element["title"]:
            label = QLabel(element["title"], parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["title"]).width() + 20
            label.setGeometry(x0 + 10, y0 - 9, wlab, 16)
            label.setAlignment(QtCore.Qt.AlignTop)
            label.adjustSize()
            # label.setAutoFillBackground(True)
            element["title_width"] = wlab
            element["label"] = label

        frame.setVisible(True)
