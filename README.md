# RA2CE GUI
The RA2CE GUI is an application of GUITools. 

Installation
---------------------------
Please follow the instructions below to install the Python environment used for both GUITools and RA2CE. Note that you must have access to the RA2CE repository which is currently private.

If running a development environment with Anaconda, the user may follow these steps in command line:
```
  cd <path of the main GUITools folder>
  conda env create -f ra2ce_gui_env.yml
  conda activate ra2ce_gui
  cd <path of the main RA2CE folder>
  poetry install
  cd <path of the main GUITools folder>
  pip install -e .
```
