from PyQt5.QtWidgets import QSlider, QLabel, QStyle, QStyleOptionSlider
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QPainter
from PyQt5 import QtWidgets
import traceback


class Slider(QSlider):

    def __init__(self, element, parent, gui):
        super().__init__(Qt.Horizontal, parent=parent)

        self.element = element
        self.parent  = parent
        self.gui     = gui

        # ToDO: Make minimum and maximum flexible
        minimum = element["minimum"]
        maximum = element["maximum"]
        interval = 10
        self.setMinimum(minimum)
        self.setMaximum(maximum)
        self.setTickInterval(interval)
        self.setSingleStep(1)
        self.setTickPosition(QSlider.TicksBelow)

        x0, y0, wdt, hgt = gui.get_position(element["position"], parent)

        self.setGeometry(x0, y0, wdt, hgt)
        if element["text"]:
            label = QLabel(element["text"], parent)
            fm = label.fontMetrics()
            wlab = fm.size(0, element["text"]).width() + 15
            label.setAlignment(Qt.AlignRight)
            label.setGeometry(x0 - wlab - 3, y0 + 5, wlab, hgt)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        # set tick labels
        ticks = [x0,x0+wdt]
        self.tick_label = []
        for ii, ticklabel in enumerate([minimum,maximum]):
            xlab = ticks[ii]
            label = QLabel(str(ticklabel), self.parent)
            fm = label.fontMetrics()
            hlab = fm.height()
            wlab = fm.width(str(ticklabel), label.fontInfo().pointSize())
            label.setAlignment(Qt.AlignHCenter)
            label.setAlignment(Qt.AlignTop)
            label.setGeometry(xlab - ii*20, y0 + hgt, wlab, hlab)
            label.setStyleSheet("background: transparent; border: none")
            self.tick_widget.append(label)

        value_changed_callback = lambda: self.first_callback()
        self.valueChanged.connect(value_changed_callback)

        if self.element["module"] and "slide_method" in element:
            # Called when the slider is moved
            self.slide_callback = getattr(element["module"], element["slide_method"])
        else:
            self.slide_callback = None

        if element["module"] and "method" in element:
            # Called when the slider is released
            self.callback = getattr(element["module"], element["method"])
            slider_released_callback = lambda: self.second_callback()
            self.sliderReleased.connect(slider_released_callback)

    def set(self):
        group = self.element["variable_group"]
        name = self.element["variable"]
        val = self.gui.getvar(group, name)
        self.setValue(val)

    def first_callback(self):
        self.okay = True
        val = self.value()
        # Update value in variable dict
        group = self.element["variable_group"]
        name = self.element["variable"]
        self.gui.setvar(group, name, val)
        self.setValue(val)
        if self.slide_callback:
            self.slide_callback(val, self)

    def second_callback(self):
        try:
            if self.isEnabled():
                group = self.element["variable_group"]
                name  = self.element["variable"]
                val   = self.gui.getvar(group, name)
                self.callback(val, self)
                # Update GUI
                self.gui.update()
        except:
            traceback.print_exc()

# class LabeledSlider(WidgetGroup):
#     def __init__(self, element, parent):
#         super().__init__(element, parent)
#         # super(LabeledSlider, self).__init__(element, parent=parent)
#
#         minimum = 2000
#         maximum = 2300
#         interval = 10
#         orientation = Qt.Horizontal
#         labels = None
#
#         levels=range(minimum, maximum+interval, interval)
#         if labels is not None:
#             if not isinstance(labels, (tuple, list)):
#                 raise Exception("<labels> is a list or tuple.")
#             if len(labels) != len(levels):
#                 raise Exception("Size of <labels> doesn't match levels.")
#             self.levels=list(zip(levels,labels))
#         else:
#             self.levels=list(zip(levels,map(str,levels)))
#
#         # if orientation==Qt.Horizontal:
#         #     self.layout=QtWidgets.QVBoxLayout(self)
#         # elif orientation==Qt.Vertical:
#         #     self.layout=QtWidgets.QHBoxLayout(self)
#         # else:
#         #     raise Exception("<orientation> wrong.")
#         #
#         # # gives some space to print labels
#         # self.left_margin=10
#         # self.top_margin=10
#         # self.right_margin=10
#         # self.bottom_margin=10
#         #
#         # self.layout.setContentsMargins(self.left_margin,self.top_margin,
#         #         self.right_margin,self.bottom_margin)
#
#         self.sl=QSlider(orientation, parent=parent)
#         self.sl.setMinimum(minimum)
#         self.sl.setMaximum(maximum)
#         self.sl.setValue(minimum)
#         if orientation==Qt.Horizontal:
#             self.sl.setTickPosition(QtWidgets.QSlider.TicksBelow)
#             self.sl.setMinimumWidth(300) # just to make it easier to read
#         else:
#             self.sl.setTickPosition(QtWidgets.QSlider.TicksLeft)
#             self.sl.setMinimumHeight(300) # just to make it easier to read
#         self.sl.setTickInterval(interval)
#         self.sl.setSingleStep(1)
#
#         x0, y0, wdt, hgt = element["window"].get_position(self.element["position"], self.parent)
#         self.sl.setGeometry(x0, y0, wdt, hgt)
#
#         self.widgets.append(self.sl)
#         # self.layout.addWidget(self.sl)
#
#     def paintEvent(self, e):
#
#         super(LabeledSlider,self).paintEvent(e)
#
#         style=self.sl.style()
#         painter=QPainter(self)
#         st_slider=QStyleOptionSlider()
#         st_slider.initFrom(self.sl)
#         st_slider.orientation=self.sl.orientation()
#
#         length=style.pixelMetric(QStyle.PM_SliderLength, st_slider, self.sl)
#         available=style.pixelMetric(QStyle.PM_SliderSpaceAvailable, st_slider, self.sl)
#
#         for v, v_str in self.levels:
#
#             # get the size of the label
#             rect=painter.drawText(QRect(), Qt.TextDontPrint, v_str)
#
#             if self.sl.orientation()==Qt.Horizontal:
#                 # I assume the offset is half the length of slider, therefore
#                 # + length//2
#                 x_loc=QStyle.sliderPositionFromValue(self.sl.minimum(),
#                         self.sl.maximum(), v, available)+length//2
#
#                 # left bound of the text = center - half of text width + L_margin
#                 left=x_loc-rect.width()//2+self.left_margin
#                 bottom=self.rect().bottom()
#
#                 # enlarge margins if clipping
#                 if v==self.sl.minimum():
#                     if left<=0:
#                         self.left_margin=rect.width()//2-x_loc
#                     if self.bottom_margin<=rect.height():
#                         self.bottom_margin=rect.height()
#
#                     self.layout.setContentsMargins(self.left_margin,
#                             self.top_margin, self.right_margin,
#                             self.bottom_margin)
#
#                 if v==self.sl.maximum() and rect.width()//2>=self.right_margin:
#                     self.right_margin=rect.width()//2
#                     self.layout.setContentsMargins(self.left_margin,
#                             self.top_margin, self.right_margin,
#                             self.bottom_margin)
#
#             else:
#                 y_loc=QStyle.sliderPositionFromValue(self.sl.minimum(),
#                         self.sl.maximum(), v, available, upsideDown=True)
#
#                 bottom=y_loc+length//2+rect.height()//2+self.top_margin-3
#                 # there is a 3 px offset that I can't attribute to any metric
#
#                 left=self.left_margin-rect.width()
#                 if left<=0:
#                     self.left_margin=rect.width()+2
#                     self.layout.setContentsMargins(self.left_margin,
#                             self.top_margin, self.right_margin,
#                             self.bottom_margin)
#
#             pos=QPoint(left, bottom)
#             painter.drawText(pos, v_str)
#
#         return
#
#     def set(self):
#         if self.check_variables():
#             getvar = self.element["getvar"]
#             group = self.element["variable_group"]
#             name = self.element["variable"]
#             val = getvar(group, name)
#             self.widgets[0].setValue(val)
#             self.set_dependencies()
#
#     def callback(self):
#         self.okay = True
#         if self.check_variables():
#             newval = self.widgets[0].value()
#
#             # Update value in variable dict
#             if self.okay:
#                 setvar = self.element["setvar"]
#                 group = self.element["variable_group"]
#                 name = self.element["variable"]
#                 setvar(group, name, newval)
#                 self.widgets[0].setValue(newval)