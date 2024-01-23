from PyQt5.QtWidgets import QTableView
from PyQt5.QtCore import QItemSelection, QItemSelectionModel
from PyQt5.QtWidgets import QLabel
from PyQt5 import QtCore
import traceback

from enum import Enum

import pandas as pd
import copy

class DataFrameModel(QtCore.QAbstractTableModel):
    """Class to create table view from dataframe"""

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
    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ):
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

    def data(self, index, role):
        if not index.isValid() or not (
            0 <= index.row() < self.rowCount()
            and 0 <= index.column() < self.columnCount()
        ):
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
            QtCore.Qt.DisplayRole: b"display",
            DataFrameModel.DtypeRole: b"dtype",
            DataFrameModel.ValueRole: b"value",
        }
        return roles

    def sort(self, column, order):
        colname = self._dataframe.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._dataframe.sort_values(
            colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True
        )
        self._dataframe.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class SelectionTable(Enum):
    # NoSelection = 0
    # SingleSelection = 1
    # MultiSelection = 2
    # ExtendedSelection = 3
    none = 0
    single = 1
    multiple = 2
    extended = 3


class TableView(QTableView):
    """Table pyqt Element"""

    def __init__(self, element):
        super().__init__(element.parent.widget)
        self.element = element

        # Add title
        if element.text:
            label = QLabel(element.text, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        # Connect callback when event happens
        self.clicked.connect(self.callback)

        # This allows for whole row or column selection and not individual cells. Use row as default
        selection_direction = QTableView.SelectRows
        if hasattr(self.element, "selection_direction"):
            if element.selection_direction == "column":
                selection_direction = QTableView.SelectColumns
                if self.element.sortable:
                    raise ValueError("Column selection cannot be sortable")
        self.setSelectionBehavior(selection_direction)

        # If the header is clicked and the selection direction is rows, the table is sorted and header_clicker is called
        if self.element.sortable and selection_direction == QTableView.SelectRows:
            self.setSortingEnabled(True)
            self.horizontalHeader().sectionClicked.connect(self.header_clicked)
            # Make sure that the sorting direction is shown
            self.horizontalHeader().setSortIndicatorShown(True)
        elif selection_direction == QTableView.SelectColumns:
            # If the selection direction is columns, the table is not sorted but it does count as selecting the column. Call the regular callback function
            self.horizontalHeader().sectionClicked.connect(self.callback)
        else:    
            self.setSortingEnabled(False)

        self.set_geometry()

        # Set selection mode
        selection_type = None
        if hasattr(self.element, "selection_type"):
            selection_type = getattr(SelectionTable, element.selection_type, None)
        self.multi_selection = False
        if selection_type:
            self.setSelectionMode(selection_type.value)
            if (
                selection_type == SelectionTable.multiple
                or selection_type == SelectionTable.extended
            ):
                self.multi_selection = True

        self.execute_callback = True

        self.sort_order = 0
        self.sort_column = 0

    def resize_columns(self, df):
        for i, col in enumerate(df.columns):
            max_char = max(max([len(str(x)) for x in df[col].values]), len(col))
            self.element.widget.setColumnWidth(i, max_char * 10)

    def set(self):
        # option_value
        df = self.element.getvar(self.element.option_value.variable_group, self.element.option_value.variable)
        if df is not None:
            self.df = df # Original unsorted dataframe
            df_sorted = copy.copy(df.reset_index()) # Sorted dataframe
            df_sorted = df_sorted.drop("index", axis=1)
        else:
            df_sorted = df
        # Update items
        self.clearSpans()
        model = DataFrameModel(df_sorted)
        self.setModel(model)
        # resizeColumnsToContents can be slow for large tables
        if df_sorted.shape[0] * df_sorted.shape[1] > 1000:
            self.resize_columns(df_sorted)
        else:
            self.resizeColumnsToContents()  
        self.verticalHeader().setVisible(False)

        if self.element.sortable:
            self.sortByColumn(self.sort_column, self.sort_order)

        # In case no selection is used skip
        if not self.element.variable:
            return

        # Find indices in sorted dataframe
        indices = self.find_sorted_indices()
        if self.selectionBehavior() == QTableView.SelectRows:
            self.select_rows(indices)
        elif self.selectionBehavior() == QTableView.SelectColumns:
            self.select_cols(indices)
        else:
            raise ValueError("Selection behavior not recognized")
        self.execute_callback = True

    def callback(self):
        # Find selected indices in the original dataframe
        if not self.element.variable:
            return
        if self.selectionBehavior() == QTableView.SelectRows:
            indices = self.find_original_indices()
        elif self.selectionBehavior() == QTableView.SelectColumns:
            # Column selection cannot be sorted
            indices = [index.column() for index in self.selectionModel().selectedColumns()]
        else:
            raise ValueError("Selection behavior not recognized")
        # Set the new value 
        name = self.element.variable
        group = self.element.variable_group
        self.element.setvar(group, name, indices)
        try:
            # Execute callback
            if self.isEnabled() and self.element.callback:
                self.element.callback(indices, self)
            # Update GUI
            self.element.window.update()
        except:
            traceback.print_exc()

    def header_clicked(self, column_index):
        """Callback when header is clicked to sort"""
        if not self.element.variable:
            return
        self.sort_column = column_index
        self.sort_order = self.horizontalHeader().sortIndicatorOrder()
        indices = self.find_sorted_indices()
        self.select_rows(indices)

    def select_rows(self, indices):
        # Select rows in table
        self.selectionModel().clearSelection()
        model = self.model() # get data model for indexes.
        selection = QItemSelection()
        for i in indices:
            # Get the model index for selection.
            # Column shouldn't matter for row-wise.
            model_index = model.index(i, 0)
            # Select single row.
            selection.select(model_index, model_index)  # top left, bottom right identical
        mode = QItemSelectionModel.Select | QtCore.QItemSelectionModel.Rows
        # Apply the selection, using the row-wise mode.
        self.selectionModel().select(selection, mode)

    def select_cols(self, indices):
        # Select rows in table
        self.selectionModel().clearSelection()
        model = self.model() # get data model for indexes.
        selection = QItemSelection()
        for i in indices:
            # Get the model index for selection.
            # Column shouldn't matter for row-wise.
            model_index = model.index(0, i)
            # Select single row.
            selection.select(model_index, model_index)  # top left, bottom right identical
        mode = QItemSelectionModel.Select | QtCore.QItemSelectionModel.Columns
        # Apply the selection, using the row-wise mode.
        self.selectionModel().select(selection, mode)

    def find_original_indices(self):
        # Find indices of row in original dataframe df0 that match the row in the sorted dataframe df
        indices = [index.row() for index in self.selectionModel().selectedRows()]
        df0 = self.df
        df = self.model()._dataframe
        for index in indices:
            row = df.iloc[index]
            index0 = df0.index[df0.apply(lambda r: r.equals(row), axis=1)].tolist()[0]
            indices[indices.index(index)] = index0
        return indices
        
    def find_sorted_indices(self):
        # Find indices of row in sorted dataframe df0 that match the row in the original dataframe df
        indices0 = self.element.getvar(self.element.variable_group, self.element.variable)
        df0 = self.df
        df = self.model()._dataframe
        indices = []
        for index in indices0:
            row = df0.loc[index]
            index0 = df.index[df.apply(lambda r: r.equals(row), axis=1)].tolist()[0]
            indices.append(index0)
        return indices

    def set_geometry(self):
        resize_factor = self.element.gui.resize_factor
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if self.element.text:
            label = self.text_widget
            fm = label.fontMetrics()
            wlab = int(fm.size(0, self.element.text).width())
            if (
                self.element.text_position == "above-center"
                or self.element.text_position == "above"
            ):
                label.setAlignment(QtCore.Qt.AlignCenter)
                label.setGeometry(
                    x0, int(y0 - 20 * resize_factor), wdt, int(20 * resize_factor)
                )
            elif self.element.text_position == "above-left":
                label.setAlignment(QtCore.Qt.AlignLeft)
                label.setGeometry(
                    x0, int(y0 - 20 * resize_factor), wlab, int(20 * resize_factor)
                )
            else:
                # Assuming left
                label.setAlignment(QtCore.Qt.AlignRight)
                label.setGeometry(
                    int(x0 - wlab - 3 * resize_factor),
                    int(y0 + 5 * self.element.gui.resize_factor),
                    wlab,
                    int(20 * resize_factor),
                )
