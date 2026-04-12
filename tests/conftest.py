"""Shared fixtures for guitares widget tests."""

import os

import pytest
from PySide6.QtWidgets import QApplication

from guitares.gui import GUI
from guitares.window import Window


@pytest.fixture(scope="session")
def qapp():
    """Create a single QApplication for the entire test session."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


class DummyApp:
    """Minimal application object expected by GUI."""

    pass


def build_gui(config_yaml: str, variables: dict | None = None) -> GUI:
    """Create a GUI from an inline YAML string without entering the event loop.

    Parameters
    ----------
    config_yaml : str
        The YAML configuration (same format as a .yml config file).
    variables : dict, optional
        Mapping of ``{group: {name: value}}`` to pre-set.

    Returns
    -------
    GUI
        A fully built GUI object (window created, widgets instantiated).
    """
    import tempfile

    app = DummyApp()

    with tempfile.TemporaryDirectory() as tmpdir:
        config_file = os.path.join(tmpdir, "test.yml")
        with open(config_file, "w") as f:
            f.write(config_yaml)

        gui = GUI(app, config_file="test.yml", config_path=tmpdir, framework="pyside6")

        if variables:
            for group, vars_ in variables.items():
                for name, value in vars_.items():
                    gui.setvar(group, name, value)

        # Build the window and widgets without entering the event loop
        gui.window = Window(gui.config, gui)
        gui.window.build()

    return gui


@pytest.fixture
def make_gui(qapp):
    """Factory fixture that returns a build_gui callable."""
    return build_gui
