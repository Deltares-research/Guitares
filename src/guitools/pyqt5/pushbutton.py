# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

from PyQt5.QtWidgets import QPushButton
from PyQt5.QtGui import QIcon

from .widget_group import WidgetGroup


class PushButton(WidgetGroup):
    def __init__(self, element, parent):
        super().__init__(element, parent)

        b = QPushButton(element["text"], parent)
        self.widgets.append(b)

        x0, y0, wdt, hgt = element["window"].get_position_from_string(element["position"], parent)
        b.setGeometry(x0, y0, wdt, hgt)

        if element["module"]:
            if "method" in element:
                fcn = getattr(element["module"], element["method"])
                b.clicked.connect(fcn)
            else:
                print("No method found in element !")
        if "icon" in element.keys():
            b.setIcon(QIcon(element["icon"]))
        if "tooltip" in element.keys():
            b.setToolTip(element["tooltip"])

    def set(self):
        self.set_dependencies()

    def callback(self):
        # Callback already set
        pass
