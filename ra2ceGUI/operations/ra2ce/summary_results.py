# -*- coding: utf-8 -*-
import os
from pathlib import Path

from ra2ceGUI import Ra2ceGUI


def getSummaryResults():
    output_folder = Ra2ceGUI.ra2ceHandler.input_config.analysis_config.config_data['output']
    summary_results_path = Path(output_folder) / "summary_results.xlsx"
    os.system("start EXCEL.EXE {}".format(str(summary_results_path)))
