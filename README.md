# GUITools
A set of Python scripts to build configurable GUIs with PyQt5.

If running a development environment with Anaconda, the user may follow these steps in command line:
```
  conda env create -f gui_environment.yml
  cd <path of the main GUITools folder>
  pip install -e .
```


# RA2CE GUI
The RA2CE GUI is an application of GUITools. 

Installation
---------------------------
Please follow the instructions below to install the Python environment used for bothGUITools and RA2CE.

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


