"""PyQt5 table view widget backed by a pandas DataFrame model (legacy version)."""

import copy
import traceback
from enum import Enum
from typing import Any

import pandas as pd
from PyQt5 import QtCore
from PyQt5.QtWidgets import QLabel, QTableView


class DataFrameModel(QtCore.QAbstractTableModel):
    """Qt table model backed by a pandas DataFrame.

    Parameters
    ----------
    df : pd.DataFrame
        The initial DataFrame to display.
    parent : Any, optional
        The parent Qt object.
    """

    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df: pd.DataFrame = pd.DataFrame(), parent: Any = None) -> None:
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe: pd.DataFrame) -> None:
        """Replace the internal DataFrame.

        Parameters
        ----------
        dataframe : pd.DataFrame
            The new DataFrame.
        """
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self) -> pd.DataFrame:
        """Return the internal DataFrame.

        Returns
        -------
        pd.DataFrame
            The current DataFrame.
        """
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(
        self,
        section: int,
        orientation: QtCore.Qt.Orientation,
        role: int = QtCore.Qt.DisplayRole,
    ) -> Any:
        """Return header data for the given section.

        Parameters
        ----------
        section : int
            The column or row index.
        orientation : QtCore.Qt.Orientation
            Horizontal or vertical header.
        role : int
            The data role.

        Returns
        -------
        Any
            The header string or QVariant.
        """
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        """Return the number of rows.

        Parameters
        ----------
        parent : QtCore.QModelIndex
            The parent index (unused for flat tables).

        Returns
        -------
        int
            The row count.
        """
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent: QtCore.QModelIndex = QtCore.QModelIndex()) -> int:
        """Return the number of columns.

        Parameters
        ----------
        parent : QtCore.QModelIndex
            The parent index (unused for flat tables).

        Returns
        -------
        int
            The column count.
        """
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index: QtCore.QModelIndex, role: int) -> Any:
        """Return cell data for the given index and role.

        Parameters
        ----------
        index : QtCore.QModelIndex
            The cell index.
        role : int
            The data role.

        Returns
        -------
        Any
            The cell value or QVariant.
        """
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

    def roleNames(self) -> dict[int, bytes]:
        """Return the mapping of roles to role names.

        Returns
        -------
        dict[int, bytes]
            Role name mapping.
        """
        roles = {
            QtCore.Qt.DisplayRole: b"display",
            DataFrameModel.DtypeRole: b"dtype",
            DataFrameModel.ValueRole: b"value",
        }
        return roles

    def sort(self, column: int, order: QtCore.Qt.SortOrder) -> None:
        """Sort the DataFrame by the given column.

        Parameters
        ----------
        column : int
            The column index to sort by.
        order : QtCore.Qt.SortOrder
            Ascending or descending sort order.
        """
        colname = self._dataframe.columns.tolist()[column]
        self.layoutAboutToBeChanged.emit()
        self._dataframe.sort_values(
            colname, ascending=order == QtCore.Qt.AscendingOrder, inplace=True
        )
        self._dataframe.reset_index(inplace=True, drop=True)
        self.layoutChanged.emit()


class SelectionTable(Enum):
    """Selection mode enumeration for the table view."""

    NoSelection = 0
    SingleSelection = 1
    MultiSelection = 2
    ExtendedSelection = 3


class TableView(QTableView):
    """Table view widget backed by a DataFrame with sortable columns.

    Parameters
    ----------
    element : Any
        The GUI element descriptor with option values, variable binding,
        text label, sortable flag, selection type, and callback.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)
        self.element = element

        # Add title
        if element.text:
            label = QLabel(element.text, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        # Connect callback when event happens
        self.clicked.connect(self.callback)

        # If the header is clicked, the table is sorted and header_clicked is called
        if self.element.sortable:
            self.horizontalHeader().sectionClicked.connect(self.header_clicked)
            self.setSortingEnabled(True)
            self.horizontalHeader().setSortIndicatorShown(True)

        self.set_geometry()

        # This allows for whole row selection and not individual cells
        self.setSelectionBehavior(QTableView.SelectRows)

        # Set selection mode
        selection_type = None
        if hasattr(self.element, "selection_type"):
            selection_type = getattr(SelectionTable, element.selection_type, None)
        self.multi_selection = False
        if selection_type:
            self.setSelectionMode(selection_type.value)
            if (
                selection_type == SelectionTable.MultiSelection
                or selection_type == SelectionTable.ExtendedSelection
            ):
                self.multi_selection = True

        self.execute_callback = True

        self.sort_order = 0
        self.sort_column = 0

    def set(self) -> None:
        """Update the table data and selection from bound variables."""
        # option_value
        df = self.element.getvar(
            self.element.option_value.variable_group, self.element.option_value.variable
        )
        if df is not None:
            self.df = df  # Original unsorted dataframe
            df_sorted = copy.copy(df.reset_index())  # Sorted dataframe
            df_sorted = df_sorted.drop("index", axis=1)

        # Update items
        self.clearSpans()
        model = DataFrameModel(df_sorted)
        self.setModel(model)
        self.resizeColumnsToContents()
        self.verticalHeader().setVisible(False)

        if self.element.sortable:
            self.sortByColumn(self.sort_column, self.sort_order)

        # In case no selection is used skip
        if not self.element.variable:
            return

        # Find indices in sorted dataframe
        indices = self.find_sorted_indices()
        self.select_rows(indices)
        self.execute_callback = True

    def callback(self) -> None:
        """Handle cell click events by updating the bound variable."""
        if not self.element.variable:
            return
        indices = self.find_original_indices()
        name = self.element.variable
        group = self.element.variable_group
        self.element.setvar(group, name, indices)
        try:
            if self.isEnabled() and self.element.callback:
                self.element.callback(indices, self)
            self.element.window.update()
        except Exception:
            traceback.print_exc()

    def header_clicked(self, column_index: int) -> None:
        """Handle header click to sort and re-select rows.

        Parameters
        ----------
        column_index : int
            The clicked column index.
        """
        if not self.element.variable:
            return
        self.sort_column = column_index
        self.sort_order = self.horizontalHeader().sortIndicatorOrder()
        indices = self.find_sorted_indices()
        self.select_rows(indices)

    def select_rows(self, indices: list[int]) -> None:
        """Select the specified rows in the table.

        Parameters
        ----------
        indices : list[int]
            Row indices to select.
        """
        self.selectionModel().clearSelection()
        for i in indices:
            self.selectRow(i)

    def find_original_indices(self) -> list[int]:
        """Map selected rows in the sorted view back to the original DataFrame.

        Returns
        -------
        list[int]
            Row indices in the original DataFrame.
        """
        indices = [index.row() for index in self.selectionModel().selectedRows()]
        df0 = self.df
        df = self.model()._dataframe
        for index in indices:
            row = df.iloc[index]
            index0 = df0.index[df0.apply(lambda r: r.equals(row), axis=1)].tolist()[0]
            indices[indices.index(index)] = index0
        return indices

    def find_sorted_indices(self) -> list[int]:
        """Map selected indices from the original DataFrame to the sorted view.

        Returns
        -------
        list[int]
            Row indices in the sorted DataFrame.
        """
        indices0 = self.element.getvar(
            self.element.variable_group, self.element.variable
        )
        df0 = self.df
        df = self.model()._dataframe
        indices = []
        for index in indices0:
            row = df0.iloc[index]
            index0 = df.index[df.apply(lambda r: r.equals(row), axis=1)].tolist()[0]
            indices.append(index0)
        return indices

    def set_geometry(self) -> None:
        """Set widget position and size, including the text label."""
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
