from PyQt5.QtWidgets import QStatusBar, QLabel

class StatusBar:
    def __init__(self, window):
        self.parent = window.window_widget
        sb = QStatusBar()
        self.parent.setStatusBar(sb)
        self.widget = sb
        field_list = window.statusbar_fields
        self.field  = {}
        for field in field_list:
            id = field["id"]
            w = field["width"]
            text = field["text"]
            label = QLabel(text)
            # label.setStyleSheet("border :2px solid blue;") 
            self.field[id] = label
            sb.addPermanentWidget(label, w)
        # self.set_geometry()    

    def set_geometry(self):
        return

    def show_message(self, message, time):
        self.widget.showMessage(message, time)        

    def set_text(self, id, text):
        self.field[id].setText(text)
