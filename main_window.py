"""
Main application window — dark-themed PyQt5 statistical analysis app.
Bilingual: Romanian / English with toggle button.
"""

import numpy as np
import os
from PyQt5.QtWidgets import (
    QMainWindow, QSplitter, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QMessageBox, QStatusBar, QSpinBox,
    QDialog, QDialogButtonBox, QFormLayout, QDoubleSpinBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPalette, QColor

from data_panel import DataInputPanel
from results_panel import ResultsPanel
from analysis import run_all_analyses
from i18n import tr, set_language, get_language, on_language_change


class HypothesizedMeanDialog(QDialog):
    """Dialog for setting hypothesized means for one-sample t-tests."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(tr("dlg_hyp_title"))
        self.setMinimumWidth(350)
        self.setStyleSheet("""
            QDialog { background-color: #1e1e1e; color: #d4d4d4; }
            QLabel { color: #d4d4d4; font-size: 13px; }
            QDoubleSpinBox {
                background-color: #252526; color: #d4d4d4; border: 1px solid #3c3c3c;
                padding: 5px; font-size: 13px; border-radius: 3px;
            }
            QPushButton { background-color: #3c3c3c; color: #d4d4d4; border: none;
                         padding: 8px 20px; border-radius: 4px; font-size: 13px; }
            QPushButton:hover { background-color: #4c4c4c; }
        """)

        layout = QFormLayout(self)

        self.spin1 = QDoubleSpinBox()
        self.spin1.setRange(-1e9, 1e9)
        self.spin1.setDecimals(4)
        self.spin1.setValue(0.0)
        layout.addRow(tr("dlg_hyp_mean1"), self.spin1)

        self.spin2 = QDoubleSpinBox()
        self.spin2.setRange(-1e9, 1e9)
        self.spin2.setDecimals(4)
        self.spin2.setValue(0.0)
        layout.addRow(tr("dlg_hyp_mean2"), self.spin2)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def values(self):
        return self.spin1.value(), self.spin2.value()


class MainWindow(QMainWindow):
    """Main statistical analysis window."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle(tr("app_title"))
        self.setMinimumSize(1200, 800)
        self.hypothesized_mean1 = 0.0
        self.hypothesized_mean2 = 0.0

        self._setup_ui()
        self._connect_signals()

        # React to language changes
        on_language_change(self._on_language_changed)

    def _setup_ui(self):
        # Central splitter
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(4, 4, 4, 4)
        main_layout.setSpacing(4)

        # Top toolbar
        toolbar = QHBoxLayout()

        btn_style = """
            QPushButton {
                background-color: #0e639c; color: #ffffff; border: none;
                padding: 10px 24px; border-radius: 6px; font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #1177bb; }
            QPushButton:pressed { background-color: #094771; }
        """

        self.btn_analyze = QPushButton(tr("btn_analyze"))
        self.btn_analyze.setStyleSheet(btn_style)
        self.btn_analyze.setMinimumHeight(40)
        toolbar.addWidget(self.btn_analyze)

        self.btn_hyp_mean = QPushButton(tr("btn_hyp_mean"))
        self.btn_hyp_mean.setStyleSheet(btn_style.replace('#0e639c', '#5a5a5a').replace('#1177bb', '#6a6a6a').replace('#094771', '#4a4a4a'))
        self.btn_hyp_mean.setMinimumHeight(40)
        toolbar.addWidget(self.btn_hyp_mean)

        # Export button
        self.btn_export = QPushButton("📥 Export")
        self.btn_export.setStyleSheet(btn_style.replace('#0e639c', '#2d6a2d').replace('#1177bb', '#3a8a3a').replace('#094771', '#1e4d1e'))
        self.btn_export.setMinimumHeight(40)
        self.btn_export.setEnabled(False)
        toolbar.addWidget(self.btn_export)

        toolbar.addStretch()

        # Language toggle buttons
        lang_btn_base = """
            QPushButton {
                background-color: #3c3c3c; color: #888888; border: none;
                padding: 6px 14px; border-radius: 4px; font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { color: #d4d4d4; }
        """
        lang_btn_active = """
            QPushButton {
                background-color: #0e639c; color: #ffffff; border: none;
                padding: 6px 14px; border-radius: 4px; font-size: 12px;
                font-weight: bold;
            }
        """

        self.btn_lang_en = QPushButton("EN")
        self.btn_lang_en.setFixedWidth(50)
        self.btn_lang_en.clicked.connect(lambda: set_language("en"))
        toolbar.addWidget(self.btn_lang_en)

        self.btn_lang_ro = QPushButton("RO")
        self.btn_lang_ro.setFixedWidth(50)
        self.btn_lang_ro.clicked.connect(lambda: set_language("ro"))
        toolbar.addWidget(self.btn_lang_ro)

        self._update_lang_buttons()

        self.lbl_status = QLabel(tr("status_enter_data"))
        self.lbl_status.setStyleSheet("color: #888888; font-size: 13px; padding: 6px;")
        toolbar.addWidget(self.lbl_status)

        main_layout.addLayout(toolbar)

        # Horizontal splitter: input | results
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.setStyleSheet("QSplitter::handle { background-color: #3c3c3c; width: 3px; }")

        # Left: data input
        self.data_panel = DataInputPanel()
        self.splitter.addWidget(self.data_panel)

        # Right: results
        self.results_panel = ResultsPanel()
        self.splitter.addWidget(self.results_panel)

        self.splitter.setSizes([450, 750])
        main_layout.addWidget(self.splitter)

        # Bottom bar with credit
        credit_bar = QHBoxLayout()
        credit_bar.addStretch()
        self.lbl_credit = QLabel(tr("app_credit"))
        self.lbl_credit.setStyleSheet("color: #ffffff; font-size: 16px; padding: 2px 8px; font-weight: bold;")
        credit_bar.addWidget(self.lbl_credit)
        main_layout.addLayout(credit_bar)

        # Status bar
        self.statusBar().setStyleSheet("""
            QStatusBar { background-color: #007acc; color: #ffffff; font-size: 12px; padding: 4px; }
        """)
        self.statusBar().showMessage(tr("status_ready"))

    def _update_lang_buttons(self):
        lang = get_language()
        active = """
            QPushButton {
                background-color: #0e639c; color: #ffffff; border: none;
                padding: 6px 14px; border-radius: 4px; font-size: 12px;
                font-weight: bold;
            }
        """
        inactive = """
            QPushButton {
                background-color: #3c3c3c; color: #888888; border: none;
                padding: 6px 14px; border-radius: 4px; font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover { color: #d4d4d4; }
        """
        self.btn_lang_en.setStyleSheet(active if lang == "en" else inactive)
        self.btn_lang_ro.setStyleSheet(active if lang == "ro" else inactive)

    def _on_language_changed(self, lang):
        """Refresh all UI strings when language changes."""
        self.setWindowTitle(tr("app_title"))
        self.btn_analyze.setText(tr("btn_analyze"))
        self.btn_hyp_mean.setText(tr("btn_hyp_mean"))
        self.lbl_status.setText(tr("status_enter_data"))
        self.lbl_credit.setText(tr("app_credit"))
        self.statusBar().showMessage(tr("status_ready"))
        self._update_lang_buttons()

        # Refresh data panel
        self.data_panel.refresh_language()

        # Refresh results panel if there are results
        if self.results_panel.results is not None:
            self.results_panel.update_results(
                self.results_panel.results,
                self.results_panel.d1,
                self.results_panel.d2
            )

    def _connect_signals(self):
        self.btn_analyze.clicked.connect(self._run_analysis)
        self.btn_hyp_mean.clicked.connect(self._set_hypothesized_mean)
        self.btn_export.clicked.connect(self._export_results)

    def _set_hypothesized_mean(self):
        dialog = HypothesizedMeanDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.hypothesized_mean1, self.hypothesized_mean2 = dialog.values()
            self.statusBar().showMessage(
                f"H₀ means set: μ₁={self.hypothesized_mean1:.4f}, μ₂={self.hypothesized_mean2:.4f}")

    def _run_analysis(self):
        d1 = self.data_panel.get_data1()
        d2 = self.data_panel.get_data2()

        if len(d1) < 2:
            QMessageBox.warning(self, tr("err_analysis_error"), tr("err_insufficient_1"))
            return
        if len(d2) < 2:
            QMessageBox.warning(self, tr("err_analysis_error"), tr("err_insufficient_2"))
            return

        self.statusBar().showMessage(tr("status_running"))
        self.btn_analyze.setEnabled(False)

        try:
            results = run_all_analyses(d1, d2,
                hypothesized_mean1=self.hypothesized_mean1,
                hypothesized_mean2=self.hypothesized_mean2)

            if "error" in results:
                QMessageBox.critical(self, tr("err_analysis_error"), results["error"])
            else:
                self.results_panel.update_results(results, d1, d2)
                self.btn_export.setEnabled(True)
                self.statusBar().showMessage(
                    tr("statusbar_done", n1=len(d1), n2=len(d2)))
                self.lbl_status.setText(
                    tr("status_done", n1=len(d1), n2=len(d2)))
                self.lbl_status.setStyleSheet("color: #4ec9b0; font-size: 13px; padding: 6px;")

        except Exception as e:
            QMessageBox.critical(self, tr("err_analysis_error"), str(e))
            self.statusBar().showMessage(tr("status_failed"))

        finally:
            self.btn_analyze.setEnabled(True)

    def _export_results(self):
        """Export all results to a directory chosen by the user."""
        from PyQt5.QtWidgets import QFileDialog, QMessageBox
        from export_results import export_all

        directory = QFileDialog.getExistingDirectory(
            self, "Select Export Directory", os.path.expanduser("~"))
        if not directory:
            return

        try:
            name1 = self.results_panel.results["descriptive1"]["name"]
            name2 = self.results_panel.results["descriptive2"]["name"]
            paths = export_all(self.results_panel.results,
                              self.results_panel.d1, self.results_panel.d2,
                              name1, name2, directory)

            msg = (
                f"Export complete!\n\n"
                f"📄 HTML: {paths['html']}\n"
                f"📊 Excel: {paths['excel']}\n"
                f"🖼️ Charts: {len(paths['charts'])} PNG files in {os.path.join(directory, 'charts')}/"
            )
            QMessageBox.information(self, "Export Complete", msg)
            self.statusBar().showMessage(f"Exported to {directory}")
        except Exception as e:
            QMessageBox.critical(self, "Export Error", str(e))