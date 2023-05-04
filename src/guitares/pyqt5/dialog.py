from PyQt5.QtWidgets import QMessageBox

def dialog(window, text, title="", type="warning"):
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
