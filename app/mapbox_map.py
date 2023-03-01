# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

from app.ra2ceGUI_base import Ra2ceGUI


def map_moved(coords):
    print("Map move to :" + str(coords))


def coords_clicked(coords):
    print("Coords clicked: " + str(coords))
    Ra2ceGUI.gui.setvar("ra2ceGUI", "coords_clicked", coords)


