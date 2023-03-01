# © Deltares 2023.
# License notice: This file is part of RA2CE GUI. RA2CE GUI is free software: you can redistribute it and/or modify it
# under the terms of the GNU Lesser General Public License as published by the Free Software Foundation, either version
# 3 of the License, or (at your option) any later version. RA2CE GUI is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
# See the GNU Lesser General Public License for more details. You should have received a copy of the GNU Lesser General
# Public License along with RA2CE GUI. If not, see <https://www.gnu.org/licenses/>.

import os
from pathlib import Path

from app.ra2ceGUI_base import Ra2ceGUI


def getSummaryResults():
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    summary_results_path = Path(output_folder) / "summary_results.xlsx"
    os.system("start EXCEL.EXE {}".format(str(summary_results_path)))
