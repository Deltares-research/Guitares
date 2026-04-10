"""PySide6 dialog helpers: message boxes, progress bars, file choosers, and more."""

import os
import time
from typing import Any, List, Optional

from PySide6 import QtCore
from PySide6.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QGraphicsOpacityEffect,
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
        The window title.
    button_text : List[str]
        Labels for each button.
    """

    def __init__(self, text: str, title: str, button_text: List[str]) -> None:
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
        """Store the clicked button text as the answer.

        Parameters
        ----------
        *args : Any
            The clicked button widget.
        """
        self.answer = args[0].text().strip()


class AutoCloseDialog(QDialog):
    """Dialog that automatically closes after a timeout.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The message to display.
    timeout : int
        Time in milliseconds before the dialog closes.
    """

    def __init__(self, window: Any, text: str, timeout: int = 500) -> None:
        super().__init__(window)
        self.setWindowTitle("Auto Close")
        self.layout = QVBoxLayout(self)
        self.layout.addWidget(QLabel(text))
        QtCore.QTimer.singleShot(timeout, self.accept)


class FadeLabel(QLabel):
    """Overlay label that fades in, pauses, then fades out and self-destructs.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The message to display.
    timeout : int
        Time in milliseconds to show the label before fading out.
    """

    def __init__(self, window: Any, text: str, timeout: int = 1500) -> None:
        super().__init__(text, window)

        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setStyleSheet("""
            QLabel {
                color: white;
                background-color: rgba(0, 0, 0, 180);
                padding: 10px 20px;
                border-radius: 8px;
            }
        """)

        font = QFont()
        font.setBold(True)
        font.setPointSize(14)
        self.setFont(font)

        self.adjustSize()

        # center inside parent
        self.move(
            (window.width() - self.width()) // 2,
            (window.height() - self.height()) // 2,
        )

        # opacity effect
        self.effect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(self.effect)

        self.fade_anim = QPropertyAnimation(self.effect, b"opacity")
        self.fade_anim.setDuration(400)
        self.fade_anim.setStartValue(0)
        self.fade_anim.setEndValue(1)
        self.fade_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.fade_out_anim = QPropertyAnimation(self.effect, b"opacity")
        self.fade_out_anim.setDuration(400)
        self.fade_out_anim.setStartValue(1)
        self.fade_out_anim.setEndValue(0)
        self.fade_out_anim.setEasingCurve(QEasingCurve.InOutQuad)

        self.duration = timeout

    def showEvent(self, event: Any) -> None:
        """Start the fade-in animation and schedule fade-out.

        Parameters
        ----------
        event : Any
            The Qt show event.
        """
        self.fade_anim.start()
        QTimer.singleShot(self.duration, self.fade_out)

    def fade_out(self) -> None:
        """Start the fade-out animation and schedule widget deletion."""
        self.fade_out_anim.finished.connect(self.deleteLater)
        self.fade_out_anim.start()


class StringDialog(QDialog):
    """Dialog that prompts the user to enter a string.

    Parameters
    ----------
    text : str
        The prompt message.
    title : str
        The window title.
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
        """Store the entered string and OK/Cancel status.

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


class PopupmenuDialog(QDialog):
    """Dialog that prompts the user to select from a dropdown.

    Parameters
    ----------
    text : str
        The prompt message.
    title : str
        The window title.
    options : List[str]
        The dropdown options.
    """

    def __init__(self, text: str, title: str, options: List[str]) -> None:
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
        # Add a combo box with options
        self.combo = QComboBox()
        self.combo.addItems(options)
        self.layout.addWidget(self.combo)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clicked(self, *args: Any) -> None:
        """Store the selected option and OK/Cancel status.

        Parameters
        ----------
        *args : Any
            The clicked button widget.
        """
        answer = args[0].text().strip()
        if answer == "OK":
            self.answer = (self.combo.currentText(), True)
        else:
            self.answer = ("", False)


class ProgressDialog(QProgressDialog):
    """Progress dialog with elapsed and estimated remaining time labels.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The progress label text.
    title : str
        The window title.
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
        """Update progress value and time estimates.

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
            The new minimum value.
        """
        self.nmax = nmin
        self.setMaximum(nmin)

    def set_maximum(self, nmax: int) -> None:
        """Set the maximum progress value.

        Parameters
        ----------
        nmax : int
            The new maximum value.
        """
        self.nmax = nmax
        self.setMaximum(nmax)

    def was_canceled(self) -> bool:
        """Check whether the user pressed Abort.

        Returns
        -------
        bool
            True if the dialog was canceled.
        """
        QApplication.processEvents()
        return self.wasCanceled()


class WaitDialog(QProgressDialog):
    """Indeterminate wait dialog without a progress bar or cancel button.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The label text.
    title : str
        The window title.
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
        """Set the internal progress value (bar is hidden).

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
    button_text: Optional[List[str]] = None,
    options: Optional[List[str]] = None,
    nmax: int = 100,
    cancel: Optional[Any] = None,
    filter: Optional[str] = None,
    selected_filter: Optional[str] = None,
    path: Optional[str] = None,
    file_name: Optional[str] = None,
    timeout: int = 500,
    string: str = "",
) -> Any:
    """Show a dialog of the given type and return the result.

    Parameters
    ----------
    window : Any
        The parent window widget.
    text : str
        The message or prompt text.
    title : str
        The dialog title.
    type : str
        Dialog type: "warning", "info", "auto_close", "fade_label", "critical",
        "question", "question_yes_no", "custom", "progress", "wait",
        "open_file", "open_files", "save_file", "select_path", "string",
        or "popupmenu".
    button_text : Optional[List[str]]
        Button labels for "custom" type.
    options : Optional[List[str]]
        Dropdown options for "popupmenu" type.
    nmax : int
        Maximum for "progress" type.
    cancel : Optional[Any]
        Unused, reserved for future use.
    filter : Optional[str]
        File filter string for file dialogs.
    selected_filter : Optional[str]
        Pre-selected filter for file dialogs.
    path : Optional[str]
        Initial directory for file dialogs.
    file_name : Optional[str]
        Initial file name for file dialogs.
    timeout : int
        Timeout in ms for "auto_close" type.
    string : str
        Initial value for "string" type.

    Returns
    -------
    Any
        The dialog result (varies by type).
    """
    if options is None:
        options = []
    if type == "warning":
        ret = QMessageBox.warning(window, title, text, QMessageBox.Ok, QMessageBox.Ok)
        return ret
    elif type == "info":
        ret = QMessageBox.information(
            window, title, text, QMessageBox.Ok, QMessageBox.Ok
        )
        return ret
    elif type == "auto_close":
        dlg = AutoCloseDialog(window, text, timeout=timeout)
        dlg.exec()
    elif type == "fade_label":
        dlg = FadeLabel(window, text, timeout=timeout).show()
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
    elif type == "popupmenu":
        dlg = PopupmenuDialog(text, title, options)
        dlg.exec()
        return dlg.answer[0], dlg.answer[1]
