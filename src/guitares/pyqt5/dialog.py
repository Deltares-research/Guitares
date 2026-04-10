"""PyQt5 dialog widgets for messages, progress bars, file selection, and string input."""

import os
import time
from typing import Any, Optional

from PyQt5 import QtCore
from PyQt5.QtWidgets import (
    QApplication,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressDialog,
    QVBoxLayout,
)


class CustomDialog(QDialog):
    """Dialog with custom button labels.

    Parameters
    ----------
    text : str
        The message to display.
    title : str
        The dialog window title.
    button_text : list[str]
        Labels for the dialog buttons.
    """

    def __init__(self, text: str, title: str, button_text: list[str]) -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox()
        for txt in button_text:
            self.buttonBox.addButton(f"  {txt}  ", QDialogButtonBox.AcceptRole)
        self.buttonBox.clicked.connect(self.clicked)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel(text)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clicked(self, *args: Any) -> None:
        """Record which button was clicked.

        Parameters
        ----------
        *args : Any
            The clicked button widget.
        """
        self.answer = args[0].text().strip()


class StringDialog(QDialog):
    """Dialog that prompts the user for a string value.

    Parameters
    ----------
    text : str
        The prompt message.
    title : str
        The dialog window title.
    string : str
        The initial string value.
    """

    def __init__(self, text: str, title: str, string: str) -> None:
        super().__init__()
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("  OK  ", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("  Cancel  ", QDialogButtonBox.AcceptRole)
        self.buttonBox.clicked.connect(self.clicked)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel(text)
        self.layout.addWidget(message)
        self.edit = QLineEdit(string)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clicked(self, *args: Any) -> None:
        """Record the user's response.

        Parameters
        ----------
        *args : Any
            The clicked button widget.
        """
        answer = args[0].text().strip()
        if answer == "OK":
            self.answer = (self.edit.text(), True)
        else:
            self.answer = ("", False)


class ProgressDialog(QProgressDialog):
    """Progress dialog with elapsed and estimated remaining time display.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The progress label text.
    title : str
        The dialog window title.
    nmax : int
        The maximum progress value.
    """

    def __init__(self, window: Any, text: str, title: str, nmax: int) -> None:
        super().__init__(text, "Abort", 0, nmax, window)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimum(0)
        self.setMaximum(100)
        self.setWindowTitle(title)
        self.time_elapsed = QLabel("Time elapsed :", self)
        self.time_elapsed.setGeometry(15, 65, 200, 20)
        self.time_remaining = QLabel("Est. time remaining :", self)
        self.time_remaining.setGeometry(15, 85, 200, 20)
        self.t0 = time.time()
        self.nmax = nmax
        self.setMinimumDuration(100)
        self.setValue(0)
        self.show()

    def set_value(self, i: int) -> None:
        """Update the progress value and time labels.

        Parameters
        ----------
        i : int
            The current progress value.
        """
        self.setValue(i)
        t = time.time()
        dt = t - self.t0
        if dt > 60.0:
            tmin = int(dt / 60)
            tsec = dt - tmin * 60.0
            new_string = f"Time elapsed : {int(tmin)}m {int(tsec)}s"
        else:
            new_string = f"Time elapsed : {int(dt)}s"

        self.time_elapsed.setText(new_string)
        frac = max(i, 1) / self.nmax
        trem = dt / frac - dt

        if trem > 60.0:
            tmin = int(trem / 60)
            tsec = trem - tmin * 60.0
            new_string = f"Est. time remaining : {int(tmin)}m {int(tsec)}s"
        else:
            new_string = f"Est. time remaining : {int(trem)}s"
        self.time_remaining.setText(new_string)
        self.show()
        QApplication.processEvents()

    def set_text(self, text: str) -> None:
        """Update the progress label text.

        Parameters
        ----------
        text : str
            The new label text.
        """
        self.setLabelText(text)

    def set_minimum(self, nmin: int) -> None:
        """Set the minimum (and maximum) progress value.

        Parameters
        ----------
        nmin : int
            The minimum value.
        """
        self.nmax = nmin
        self.setMaximum(nmin)

    def set_maximum(self, nmax: int) -> None:
        """Set the maximum progress value.

        Parameters
        ----------
        nmax : int
            The maximum value.
        """
        self.nmax = nmax
        self.setMaximum(nmax)

    def was_canceled(self) -> bool:
        """Check whether the user pressed the cancel button.

        Returns
        -------
        bool
            True if the dialog was canceled.
        """
        QApplication.processEvents()
        return self.wasCanceled()


class WaitDialog(QProgressDialog):
    """Non-interactive wait dialog without a visible progress bar or button.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The wait message text.
    title : str
        The dialog window title.
    """

    def __init__(self, window: Any, text: str, title: str) -> None:
        super().__init__(text, "Abort", 0, 100, window)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimumDuration(1)
        self.setMaximum(100)
        self.setWindowTitle(title)
        self.children()[1].setVisible(False)  # Make progress bar invisible
        self.children()[3].setVisible(False)  # Make push button invisible
        self.show()

    def set_value(self, i: int) -> None:
        """Update the internal progress value.

        Parameters
        ----------
        i : int
            The progress value.
        """
        self.setValue(i)


def dialog(
    window: Any,
    text: str,
    title: str = " ",
    type: str = "warning",
    button_text: Optional[list[str]] = None,
    nmax: int = 100,
    cancel: Optional[Any] = None,
    filter: Optional[str] = None,
    selected_filter: Optional[str] = None,
    path: Optional[str] = None,
    file_name: Optional[str] = None,
    string: str = "",
) -> Any:
    """Show a dialog of the specified type.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The dialog message or prompt text.
    title : str
        The dialog window title.
    type : str
        Dialog type: "warning", "info", "critical", "question", "question_yes_no",
        "custom", "progress", "wait", "open_file", "open_files", "save_file",
        "select_path", or "string".
    button_text : list[str], optional
        Button labels for "custom" type dialogs.
    nmax : int
        Maximum value for "progress" type dialogs.
    cancel : Any, optional
        Unused, reserved for future use.
    filter : str, optional
        File filter string for file dialogs.
    selected_filter : str, optional
        Initially selected filter for file dialogs.
    path : str, optional
        Initial directory path for file dialogs.
    file_name : str, optional
        Initial file name for file dialogs.
    string : str
        Initial string value for "string" type dialogs.

    Returns
    -------
    Any
        The dialog result; type depends on the dialog type.
    """
    if type == "warning":
        ret = QMessageBox.warning(window, title, text, QMessageBox.Ok, QMessageBox.Ok)
        return ret
    elif type == "info":
        ret = QMessageBox.information(
            window, title, text, QMessageBox.Ok, QMessageBox.Ok
        )
        return ret
    elif type == "critical":
        ret = QMessageBox.critical(window, title, text, QMessageBox.Ok, QMessageBox.Ok)
        return ret
    elif type == "question":
        ret = QMessageBox.question(
            window, title, text, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel
        )
        if ret == QMessageBox.Ok:
            return True
        else:
            return False
    elif type == "question_yes_no":
        ret = QMessageBox.question(
            window, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if ret == QMessageBox.Yes:
            return True
        else:
            return False
    elif type == "custom":
        dlg = CustomDialog(text, title, button_text)
        dlg.exec()
        return dlg.answer
    elif type == "progress":
        dlg = ProgressDialog(window, text, title, nmax)
        return dlg
    elif type == "wait":
        dlg = WaitDialog(window, text, title)
        for i in range(5):
            time.sleep(0.001)
            dlg.set_value(i)
        return dlg
    elif type == "open_file":
        if path is None:
            path = os.getcwd()
        if file_name:
            path = os.path.join(path, file_name)
        fname = QFileDialog.getOpenFileName(window, text, path, filter, selected_filter)
        return fname
    elif type == "open_files":
        if path is None:
            path = os.getcwd()
        if file_name:
            path = os.path.join(path, file_name)
        fname = QFileDialog.getOpenFileNames(
            window, text, path, filter, selected_filter
        )
        return fname
    elif type == "save_file":
        if path is None:
            path = os.getcwd()
        if file_name:
            path = os.path.join(path, file_name)
        fname = QFileDialog.getSaveFileName(window, text, path, filter, selected_filter)
        return fname
    elif type == "select_path":
        if path is None:
            path = os.getcwd()
        new_path = QFileDialog.getExistingDirectory(window, text, path)
        return new_path
    elif type == "string":
        dlg = StringDialog(text, title, string)
        dlg.exec()
        return dlg.answer[0], dlg.answer[1]
