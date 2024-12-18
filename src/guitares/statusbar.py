class StatusBar:
    def __init__(self, window, widths):

        if self.window.gui.framework == "pyqt5":
            from PyQt5.QtWidgets import QStatusBar, QLabel, QFrame
        elif self.window.gui.framework == "pyside6":
            from PySide6.QtWidgets import QStatusBar, QLabel, QFrame

        sb = QStatusBar()
        window.setStatusBar(sb)
        self.window = window
        self.widget = sb
        self.field  = []
        for w in widths:
            self.field.append({"width": w})

        # Add fields
        ww = window.geometry().width()
        x = 0
        for field in self.field:
            frame = QFrame()
            sb.addWidget(frame)
            label = QLabel("text01", frame)
            field["frame"] = frame
            field["label"] = label
            x = x + int(ww*w) + 5

        self.set_geometry()    

    def set_geometry(self):
        window_width = self.window.geometry().width()
        x = 0
        for field in self.field:
            frame = field["frame"]
            frame.setGeometry(x, 0, int(window_width*field["width"]), 20)
            x = x + int(window_width*field["width"]) + 5
