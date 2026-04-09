"""PySide6 editable table widget backed by a pandas DataFrame.

Uses ``QTableWidget`` for native cell editing — clicking a cell selects
it, double-clicking (or pressing a key) opens the editor with the
existing value pre-filled.
"""

import traceback
from typing import Any, Optional

import numpy as np
import pandas as pd
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QLabel,
    QTableWidget,
    QTableWidgetItem,
)


class Table(QTableWidget):
    """Editable table widget backed by a pandas DataFrame.

    Parameters
    ----------
    element : Any
        The Guitares element descriptor for this table.
    """

    def __init__(self, element: Any) -> None:
        super().__init__(element.parent.widget)
        self.element = element
        self._updating = False  # Guard against recursive updates

        # Title label
        if element.text:
            label = QLabel(element.text, element.parent.widget)
            label.setStyleSheet("background: transparent; border: none")
            self.text_widget = label

        # Selection behaviour
        if self.element.editable:
            self.setSelectionBehavior(QAbstractItemView.SelectItems)
            self.setSelectionMode(QAbstractItemView.SingleSelection)
            self.setEditTriggers(
                QAbstractItemView.DoubleClicked | QAbstractItemView.EditKeyPressed
            )
        else:
            self.setSelectionBehavior(QAbstractItemView.SelectRows)
            self.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # No vertical header (row numbers)
        self.verticalHeader().setVisible(False)

        # Horizontal scrollbar for wide tables
        self.horizontalHeader().setStretchLastSection(False)
        self.setHorizontalScrollMode(QAbstractItemView.ScrollPerPixel)

        # Sorting
        if not self.element.sortable:
            self.setSortingEnabled(False)
        else:
            self.setSortingEnabled(True)

        # Connect cell change signal
        self.cellChanged.connect(self._on_cell_changed)

        self.set_geometry()

    def set_geometry(self) -> None:
        """Position and size the widget from the element descriptor."""
        x0, y0, wdt, hgt = self.element.get_position()
        self.setGeometry(x0, y0, wdt, hgt)
        if hasattr(self, "text_widget"):
            self.text_widget.setGeometry(x0, y0 + hgt, wdt, 16)

    def set(self) -> None:
        """Populate the table from the linked DataFrame GUI variable."""
        df = self.element.getvar(
            self.element.option_value.variable_group,
            self.element.option_value.variable,
        )

        if df is None or not isinstance(df, pd.DataFrame) or len(df) == 0:
            self._updating = True
            self.setRowCount(0)
            self.setColumnCount(0)
            self._updating = False
            return

        self._updating = True

        nrows, ncols = df.shape
        self.setRowCount(nrows)
        self.setColumnCount(ncols)
        self.setHorizontalHeaderLabels([str(c) for c in df.columns])

        for row in range(nrows):
            for col in range(ncols):
                val = df.iloc[row, col]
                item = QTableWidgetItem(str(val))

                # Right-align numeric values
                dtype = df.iloc[:, col].dtype
                if dtype in (np.float64, np.int64, float, int):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # Non-editable mode: make cells read-only
                if not self.element.editable:
                    item.setFlags(item.flags() & ~Qt.ItemIsEditable)

                self.setItem(row, col, item)

        self.resizeColumnsToContents()
        self._updating = False

    def _on_cell_changed(self, row: int, col: int) -> None:
        """Handle a cell edit by the user.

        Writes the new value back to the DataFrame and calls the
        element's callback.
        """
        if self._updating:
            return

        item = self.item(row, col)
        if item is None:
            return

        # Get the current DataFrame
        df = self.element.getvar(
            self.element.option_value.variable_group,
            self.element.option_value.variable,
        )
        if df is None or row >= len(df) or col >= len(df.columns):
            return

        # Parse the new value with the correct type
        new_text = item.text()
        dtype = df.iloc[:, col].dtype
        try:
            if dtype in (np.float64, float):
                new_val = float(new_text)
            elif dtype in (np.int64, int):
                new_val = int(new_text)
            else:
                new_val = new_text
        except (ValueError, TypeError):
            # Revert to old value on parse error
            old_val = df.iloc[row, col]
            self._updating = True
            item.setText(str(old_val))
            self._updating = False
            return

        # Update the DataFrame
        df.iloc[row, col] = new_val
        self.element.setvar(
            self.element.option_value.variable_group,
            self.element.option_value.variable,
            df,
        )

        # Call the element's callback if defined
        if hasattr(self.element, "callback") and self.element.callback:
            try:
                self.element.callback()
            except Exception:
                traceback.print_exc()

    def get_dataframe(self) -> Optional[pd.DataFrame]:
        """Return the current DataFrame from the GUI variable.

        Returns
        -------
        pd.DataFrame or None
            The current table data.
        """
        return self.element.getvar(
            self.element.option_value.variable_group,
            self.element.option_value.variable,
        )
