"""
Data input panel — two datasets with table editing, copy-paste, and file import.
Bilingual: Romanian / English.
"""

import numpy as np
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QPushButton, QLabel, QFileDialog, QMessageBox,
    QTextEdit, QDialog, QDialogButtonBox, QHeaderView
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent
from PyQt5.QtWidgets import QApplication as QtApp

from i18n import tr, get_language, on_language_change


class PasteDialog(QDialog):
    """Dialog for pasting tabular data from clipboard."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_paste_title"))
        self.setMinimumSize(500, 350)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QTextEdit { background-color: #252526; color: #d4d4d4; border: 1px solid #3c3c3c;
                       font-family: 'DejaVu Sans Mono', 'Consolas', monospace; font-size: 13px; }
            QLabel { color: #d4d4d4; font-size: 13px; }
            QPushButton { background-color: #3c3c3c; color: #d4d4d4; border: none;
                         padding: 8px 20px; border-radius: 4px; font-size: 13px; }
            QPushButton:hover { background-color: #4c4c4c; }
        """)

        layout = QVBoxLayout(self)

        self.lbl = QLabel(tr("dlg_paste_label"))
        layout.addWidget(self.lbl)

        self.text_edit = QTextEdit()
        self.text_edit.setPlaceholderText("e.g.:\n12 15 18\n14 16 19\n...")
        layout.addWidget(self.text_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)


class DataTable(QTableWidget):
    """Editable table for one dataset."""

    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setColumnCount(1)
        self.setRowCount(20)
        self.setHorizontalHeaderLabels([tr("table_header")])
        self.horizontalHeader().setStretchLastSection(True)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.verticalHeader().setVisible(True)
        self.setAlternatingRowColors(True)
        self.setStyleSheet("""
            QTableWidget {
                background-color: #252526; color: #d4d4d4;
                gridline-color: #3c3c3c; border: 1px solid #3c3c3c;
                font-size: 13px; selection-background-color: #264f78;
            }
            QTableWidget::item:selected { background-color: #264f78; }
            QHeaderView::section {
                background-color: #2d2d2d; color: #d4d4d4;
                border: 1px solid #3c3c3c; padding: 4px;
                font-weight: bold; font-size: 13px;
            }
            QTableWidget QTableCornerButton::section {
                background-color: #2d2d2d; border: 1px solid #3c3c3c;
            }
        """)
        self.cellChanged.connect(self._on_cell_changed)
        self._suppress_signals = False

    def refresh_header(self):
        self.setHorizontalHeaderLabels([tr("table_header")])

    def _on_cell_changed(self, row, col):
        if not self._suppress_signals:
            self.data_changed.emit()

    def event(self, e):
        if e.type() == e.KeyPress:
            mods = e.modifiers()
            # Ctrl+C - copy
            if e.key() == Qt.Key_C and (mods & Qt.ControlModifier):
                item = self.currentItem()
                if item:
                    QtApp.clipboard().setText(item.text())
                return True
            # Ctrl+V - paste
            if e.key() == Qt.Key_V and (mods & Qt.ControlModifier):
                text = QtApp.clipboard().text().strip()
                if text:
                    tokens = []
                    for line in text.split('\n'):
                        for token in line.replace('\t', ' ').replace(',', ' ').split():
                            token = token.strip()
                            if token:
                                tokens.append(token)
                    if tokens:
                        self._suppress_signals = True
                        current = self.currentIndex()
                        row = current.row()
                        for i, token in enumerate(tokens):
                            if row + i >= self.rowCount():
                                self.setRowCount(row + i + 1)
                            self.setItem(row + i, 0, QTableWidgetItem(token))
                        self._suppress_signals = False
                        self.data_changed.emit()
                return True
            # Enter/Return - next row
            if e.key() in (Qt.Key_Return, Qt.Key_Enter):
                current = self.currentIndex()
                next_row = current.row() + 1
                if next_row < self.rowCount():
                    self.setCurrentCell(next_row, current.column())
                    self.edit(self.currentIndex())
                else:
                    self._suppress_signals = True
                    self.setRowCount(self.rowCount() + 1)
                    self._suppress_signals = False
                    self.setCurrentCell(next_row, current.column())
                    self.edit(self.currentIndex())
                return True
        return super().event(e)

    def get_data(self) -> np.ndarray:
        """Extract numeric data from table, skipping empty/invalid cells."""
        values = []
        for row in range(self.rowCount()):
            item = self.item(row, 0)
            if item and item.text().strip():
                try:
                    values.append(float(item.text().strip().replace(',', '.')))
                except ValueError:
                    pass
        return np.array(values) if values else np.array([])

    def set_data(self, data: np.ndarray):
        """Fill table with data."""
        self._suppress_signals = True
        self.setRowCount(max(len(data) + 5, 20))
        for i, val in enumerate(data):
            self.setItem(i, 0, QTableWidgetItem(f"{val:.6g}"))
        for i in range(len(data), self.rowCount()):
            self.setItem(i, 0, QTableWidgetItem(""))
        self._suppress_signals = False

    def clear_data(self):
        """Clear all data."""
        self._suppress_signals = True
        self.setRowCount(20)
        for i in range(20):
            self.setItem(i, 0, QTableWidgetItem(""))
        self._suppress_signals = False


class DatasetPanel(QWidget):
    """Panel for one dataset: table + buttons."""

    data_changed = pyqtSignal()

    def __init__(self, name_key: str = "ds1_title", parent=None):
        super().__init__(parent)
        self.name_key = name_key
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(8)

        # Title
        self.title = QLabel(tr(self.name_key))
        self.title.setStyleSheet("font-size: 15px; font-weight: bold; color: #d4d4d4; padding: 4px;")
        layout.addWidget(self.title)

        # Table
        self.table = DataTable()
        self.table.data_changed.connect(self.data_changed.emit)
        layout.addWidget(self.table)

        # Button row
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(6)

        btn_style = """
            QPushButton {
                background-color: #3c3c3c; color: #d4d4d4; border: none;
                padding: 6px 14px; border-radius: 4px; font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #4c4c4c; }
        """

        self.btn_import = QPushButton(tr("btn_import"))
        self.btn_import.setStyleSheet(btn_style)
        self.btn_import.clicked.connect(self._import_file)
        btn_layout.addWidget(self.btn_import)

        self.btn_paste = QPushButton(tr("btn_paste"))
        self.btn_paste.setStyleSheet(btn_style)
        self.btn_paste.clicked.connect(self._paste_data)
        btn_layout.addWidget(self.btn_paste)

        self.btn_clear = QPushButton(tr("btn_clear"))
        self.btn_clear.setStyleSheet(btn_style)
        self.btn_clear.clicked.connect(self._clear_data)
        btn_layout.addWidget(self.btn_clear)

        self.lbl_count = QLabel(tr("lbl_count", n=0))
        self.lbl_count.setStyleSheet("color: #888888; font-size: 12px;")
        btn_layout.addWidget(self.lbl_count)
        btn_layout.addStretch()

        layout.addLayout(btn_layout)

        # Connect count update
        self.table.data_changed.connect(self._update_count)

    def refresh_language(self):
        """Update all translatable strings."""
        self.title.setText(tr(self.name_key))
        self.btn_import.setText(tr("btn_import"))
        self.btn_paste.setText(tr("btn_paste"))
        self.btn_clear.setText(tr("btn_clear"))
        self.table.refresh_header()
        self._update_count()

    def _update_count(self):
        data = self.table.get_data()
        self.lbl_count.setText(tr("lbl_count", n=len(data)))

    def get_data(self) -> np.ndarray:
        return self.table.get_data()

    def _import_file(self):
        name = tr(self.name_key)
        filepath, _ = QFileDialog.getOpenFileName(
            self, tr("dlg_import_title", name=name), "",
            tr("dlg_import_filter")
        )
        if not filepath:
            return

        try:
            if filepath.lower().endswith(('.xlsx', '.xls')):
                import pandas as pd
                df = pd.read_excel(filepath, header=None)
                for col in df.columns:
                    numeric = pd.to_numeric(df[col], errors='coerce')
                    if numeric.notna().sum() > 0:
                        data = numeric.dropna().values
                        if len(data) > 0:
                            self.table.set_data(data)
                            self.data_changed.emit()
                            return
                QMessageBox.warning(self, tr("err_import_error"), tr("err_import_no_numeric"))
            else:
                data = []
                with open(filepath, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line:
                            for token in line.replace(',', ' ').replace('\t', ' ').split():
                                try:
                                    data.append(float(token))
                                except ValueError:
                                    pass
                if data:
                    self.table.set_data(np.array(data))
                    self.data_changed.emit()
                else:
                    QMessageBox.warning(self, tr("err_import_error"), tr("err_import_no_values"))
        except Exception as e:
            QMessageBox.critical(self, tr("err_import_error"), str(e))

    def _paste_data(self):
        # First try clipboard directly
        text = QtApp.clipboard().text().strip()
        if text:
            data = []
            for line in text.split('\n'):
                line = line.strip()
                if line:
                    for token in line.replace('\t', ' ').replace(',', ' ').split():
                        try:
                            data.append(float(token))
                        except ValueError:
                            pass
            if data:
                self.table.set_data(np.array(data))
                self.data_changed.emit()
                return

        # Fallback: show paste dialog
        dialog = PasteDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            text = dialog.text_edit.toPlainText().strip()
            if text:
                data = []
                for line in text.split('\n'):
                    line = line.strip()
                    if line:
                        for token in line.replace('\t', ' ').replace(',', ' ').split():
                            try:
                                data.append(float(token))
                            except ValueError:
                                pass
                if data:
                    self.table.set_data(np.array(data))
                    self.data_changed.emit()
                else:
                    QMessageBox.warning(self, tr("err_paste_error"), tr("err_paste_no_values"))

    def _clear_data(self):
        self.table.clear_data()
        self.data_changed.emit()


class DataInputPanel(QWidget):
    """Main data input panel with two dataset tabs."""

    data_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.dataset1 = DatasetPanel("ds1_title")
        self.dataset2 = DatasetPanel("ds2_title")

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3c3c3c; background-color: #1e1e1e; }
            QTabBar::tab { background-color: #2d2d2d; color: #888888; padding: 8px 24px;
                          font-size: 13px; font-weight: bold; border: 1px solid #3c3c3c;
                          border-bottom: none; margin-right: 2px; }
            QTabBar::tab:selected { background-color: #1e1e1e; color: #569cd6;
                                   border-bottom: 2px solid #569cd6; }
            QTabBar::tab:hover { color: #d4d4d4; }
        """)
        self.ds1_idx = self.tabs.addTab(self.dataset1, tr("ds1_tab"))
        self.ds2_idx = self.tabs.addTab(self.dataset2, tr("ds2_tab"))
        layout.addWidget(self.tabs)

        self.dataset1.data_changed.connect(self.data_changed.emit)
        self.dataset2.data_changed.connect(self.data_changed.emit)

    def refresh_language(self):
        """Update tab names and sub-panels."""
        self.tabs.setTabText(self.ds1_idx, tr("ds1_tab"))
        self.tabs.setTabText(self.ds2_idx, tr("ds2_tab"))
        self.dataset1.refresh_language()
        self.dataset2.refresh_language()

    def get_data1(self) -> np.ndarray:
        return self.dataset1.get_data()

    def get_data2(self) -> np.ndarray:
        return self.dataset2.get_data()