from PyQt5.QtWidgets import (
    QMessageBox,
    QDialogButtonBox,
    QVBoxLayout,
    QLabel,
    QDialog,
    QProgressDialog,
    QFileDialog,
    QLineEdit
)
from PyQt5 import QtCore
import time
import os

class CustomDialog(QDialog):
    def __init__(self, text, title, button_text):
        super().__init__()
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox()
        for txt in button_text:
            self.buttonBox.addButton("  " + txt + "  ", QDialogButtonBox.AcceptRole)
        self.buttonBox.clicked.connect(self.clicked)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel(text)
        self.layout.addWidget(message)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clicked(self, *args):
        self.answer = args[0].text().strip()

class StringDialog(QDialog):
    def __init__(self, text, title, string):
        super().__init__()
        self.setWindowTitle(title)
        self.buttonBox = QDialogButtonBox()
        button_text = ["Cancel", "OK"]
        for txt in button_text:
            self.buttonBox.addButton("  " + txt + "  ", QDialogButtonBox.AcceptRole)
        self.buttonBox.clicked.connect(self.clicked)
        self.buttonBox.accepted.connect(self.accept)
        self.layout = QVBoxLayout()
        message = QLabel(text)
        self.layout.addWidget(message)
        self.edit = QLineEdit(string)
        self.layout.addWidget(self.edit)
        self.layout.addWidget(self.buttonBox)
        self.setLayout(self.layout)

    def clicked(self, *args):
        answer = args[0].text().strip()
        if answer == "OK":
            self.answer = (self.edit.text(), True)
        else:
            self.answer = ("", False)

class ProgressDialog(QProgressDialog):
    def __init__(self, window, text, title, nmax):
        super().__init__(text, "Abort", 0, nmax, window)
        self.setWindowModality(QtCore.Qt.WindowModal)
#        self.setMinimum(1)
        self.setMaximum(nmax)
        self.setWindowTitle(title)
        self.time_elapsed = QLabel("Time elapsed :", self)
        self.time_elapsed.setGeometry(15, 65, 200, 20)
        self.time_remaining = QLabel("Est. time remaining :", self)
        self.time_remaining.setGeometry(15, 85, 200, 20)
        self.t0 = time.time()
        self.nmax = nmax
        self.setMinimumDuration(0)
        self.setValue(0)
#        self.show()

    def set_value(self, i):
        self.setValue(i)
        t = time.time()
        dt = t - self.t0
        if dt > 60.0:
            tmin = int(dt / 60)
            tsec = dt - tmin * 60.0
            new_string = (
                "Time elapsed : " + str(int(tmin)) + "m " + str(int(tsec)) + "s"
            )
        else:
            new_string = "Time elapsed : " + str(int(dt)) + "s"

        self.time_elapsed.setText(new_string)
        frac = max(i, 1) / self.nmax
        trem = dt / frac - dt

        if trem > 60.0:
            tmin = int(trem / 60)
            tsec = trem - tmin * 60.0
            new_string = (
                "Est. time remaining : " + str(int(tmin)) + "m " + str(int(tsec)) + "s"
            )
        else:
            new_string = "Est. time remaining : " + str(int(trem)) + "s"
        self.time_remaining.setText(new_string)

    def set_text(self, text):
        self.setLabelText(text)

    def set_maximum(self, nmax):
        self.nmax = nmax
        self.setMaximum(nmax)

    def was_canceled(self):
        return self.wasCanceled()


class WaitDialog(QProgressDialog):
    def __init__(self, window, text, title):
        super().__init__(text, "Abort", 0, 100, window)
        self.setWindowModality(QtCore.Qt.WindowModal)
        self.setMinimumDuration(1)
        self.setMaximum(100)
        self.setWindowTitle(title)
        self.children()[1].setVisible(False)  # Make progress bar invisible
        self.children()[3].setVisible(False)  # Make push button invisible
        self.show()

    def set_value(self, i):
        self.setValue(i)

# class StringDialog(QProgressDialog):
#     def __init__(self, window, text, title):
#         super().__init__(text, "Abort", 0, 100, window)
#         self.setWindowModality(QtCore.Qt.WindowModal)
#         self.setMinimumDuration(1)
#         self.setMaximum(100)
#         self.setWindowTitle(title)
#         self.children()[1].setVisible(False)  # Make progress bar invisible
#         self.children()[3].setVisible(False)  # Make push button invisible
#         self.show()

#     def set_value(self, i):
#         self.setValue(i)

def dialog(
    window,
    text,
    title=" ",
    type="warning",
    button_text=None,
    nmax=100,
    cancel=None,
    filter=None,
    selected_filter=None,
    path=None,
    file_name=None,
    string=""
):
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
        if path == None:
            path = os.getcwd()
        if file_name:
            path = os.path.join(path, file_name)
        fname = QFileDialog.getOpenFileName(window, text, path, filter, selected_filter)
        return fname
    elif type == "save_file":
        if path == None:
            path = os.getcwd()
        if file_name:
            path = os.path.join(path, file_name)
        fname = QFileDialog.getSaveFileName(window, text, path, filter, selected_filter)
        return fname
    elif type == "select_path":
        if path == None:
            path = os.getcwd()
        new_path = QFileDialog.getExistingDirectory(window, text, path)
        return new_path
    elif type == "string":
        dlg = StringDialog(text, title, string)
        dlg.exec()
        return dlg.answer[0], dlg.answer[1]
