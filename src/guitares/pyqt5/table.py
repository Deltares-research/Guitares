from PyQt5.QtWidgets import QTableView
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

import pandas as pd

class DataFrameModel(QtCore.QAbstractTableModel):
    """ Class to create table view from dataframe"""
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtype

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles
    
    def sort(self, column, order):
        colname = self._dataframe.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._dataframe.sort_values(colname, ascending= order == QtCore.Qt.AscendingOrder, inplace=True)
        self._dataframe.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()

class Table(QTableView):
    """Table pyqt Element"""
    def __init__(self, element):
        super().__init__(element.parent.widget)
        self.element = element

        self.add_items()

        # Add title
        if element.text:
            label = QLabel(element.text, element.parent.widget)

            label.setStyleSheet("background: transparent; border: none")

            self.text_widget = label

        # Connect callback when event happens
        self.clicked.connect(self.callback)
        # self.selectionModel().selectionChanged.connect(self.callback)
        

        self.set_geometry()
        
        # This allows for whole row selection and not individual cells
        self.setSelectionBehavior(QTableView.SelectRows)

        self.execute_callback = True

    def set(self):
        # Update items
        if self.element.option_value.variable:
            self.add_items()

        # Get value
        index = self.element.getvar(self.element.variable_group, self.element.variable)
        self.selectRow(index[0])
        
        self.execute_callback = True    

    def callback(self):
        indexes = [index.row() for index in self.selectionModel().selectedRows()]

        name  = self.element.variable
        group = self.element.variable_group
        self.element.setvar(group, name, indexes)

        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(indexes, self)
            # Update GUI
            self.element.window.update()
        except:
            traceback.print_exc()

    def add_items(self):
        self.clearSpans()
        # Only way to set dataframe is by variable
        model = DataFrameModel(self.element.getvar(self.element.option_value.variable_group, 
                                                   self.element.option_value.variable))
        self.setModel(model)
        self.setSortingEnabled(True)
        # self.sortByColumn(0, QtCore.SortOrder())
        self.resizeColumnsToContents()
        self.verticalHeader().setVisible(False)

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if self.element.text:
            label = self.text_widget
            fm = label.fontMetrics()
            wlab = int(fm.size(0, self.element.text).width())
            if self.element.text_position == "above-center" or self.element.text_position == "above":
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setGeometry(x0, int(y0 - 20 * resize_factor), wdt, int(20 * resize_factor))
            elif self.element.text_position == "above-left":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(x0, int(y0 - 20 * resize_factor), wlab, int(20 * resize_factor))
            else:
                # Assuming left
                label.setAlignment(QtCore.Qt.AlignRight)
                label.setGeometry(int(x0 - wlab - 3 * resize_factor),
                                  int(y0 + 5 * self.element.gui.resize_factor),
                                  wlab,
                                  int(20 * resize_factor))
