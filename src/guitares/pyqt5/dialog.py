from PyQt5.QtWidgets import QMessageBox, QDialogButtonBox, QVBoxLayout, QLabel, QDialog

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

def dialog(window, text, title=" ", type="warning", button_text=None):
    if type == "warning":
        ret = QMessageBox.warning(window, title, text, QMessageBox.Ok, QMessageBox.Ok)
        return ret
    elif type == "info":
        ret = QMessageBox.information(window, title, text, QMessageBox.Ok, QMessageBox.Ok)
        return ret
    elif type == "critical":
        ret = QMessageBox.critical(window, title, text, QMessageBox.Ok, QMessageBox.Ok)
        return ret
    elif type == "question":    
        ret = QMessageBox.question(window, title, text, QMessageBox.Ok | QMessageBox.Cancel, QMessageBox.Cancel)
        if ret == QMessageBox.Ok:
            return True
        else:
            return False
    elif type == "question_yes_no":
        ret = QMessageBox.question(window, title, text, QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if ret == QMessageBox.Yes:
            return True
        else:
            return False
    elif type == "custom":
        dlg = CustomDialog(text, title, button_text)
        dlg.exec()
        return dlg.answer    
