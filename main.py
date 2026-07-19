#!/usr/bin/env python3
"""
Statistical Analysis Tool — PyQt5 Desktop Application
Compares two datasets with full statistical analysis and visualization.
Bilingual: Romanian / English.

Author: Agent Gogu (Hermes) — for Alex
"""

import os
import sys

# ── High-DPI / Retina display support ──────────────────────────────
# Must be set BEFORE any PyQt5 imports to take effect on Linux/X11.
os.environ.setdefault("QT_AUTO_SCREEN_SCALE_FACTOR", "1")
os.environ.setdefault("QT_ENABLE_HIGHDPI_SCALING", "1")

from PyQt5.QtWidgets import QApplication
from PyQt5.QtGui import QPalette, QColor
from PyQt5.QtCore import Qt
from main_window import MainWindow


def apply_dark_theme(app: QApplication):
    """Apply dark Fusion theme with custom palette."""
    app.setStyle('Fusion')

    dark_palette = QPalette()
    dark_palette.setColor(QPalette.Window, QColor('#1e1e1e'))
    dark_palette.setColor(QPalette.WindowText, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.Base, QColor('#252526'))
    dark_palette.setColor(QPalette.AlternateBase, QColor('#2d2d2d'))
    dark_palette.setColor(QPalette.ToolTipBase, QColor('#1e1e1e'))
    dark_palette.setColor(QPalette.ToolTipText, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.Text, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.Button, QColor('#3c3c3c'))
    dark_palette.setColor(QPalette.ButtonText, QColor('#d4d4d4'))
    dark_palette.setColor(QPalette.BrightText, QColor('#ce9178'))
    dark_palette.setColor(QPalette.Link, QColor('#569cd6'))
    dark_palette.setColor(QPalette.Highlight, QColor('#264f78'))
    dark_palette.setColor(QPalette.HighlightedText, QColor('#ffffff'))
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, QColor('#666666'))
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, QColor('#666666'))
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, QColor('#666666'))

    app.setPalette(dark_palette)

    stylesheet = (
        "QToolTip {"
        " background-color: #1e1e1e; color: #d4d4d4;"
        " border: 1px solid #3c3c3c; padding: 4px; font-size: 12px;"
        " }"
        " QScrollBar:vertical {"
        " background-color: #1e1e1e; width: 12px; border: none;"
        " }"
        " QScrollBar::handle:vertical {"
        " background-color: #5a5a5a; border-radius: 4px; min-height: 30px;"
        " }"
        " QScrollBar::handle:vertical:hover { background-color: #6a6a6a; }"
        " QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }"
        " QScrollBar:horizontal {"
        " background-color: #1e1e1e; height: 12px; border: none;"
        " }"
        " QScrollBar::handle:horizontal {"
        " background-color: #5a5a5a; border-radius: 4px; min-width: 30px;"
        " }"
        " QScrollBar::handle:horizontal:hover { background-color: #6a6a6a; }"
        " QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }"
    )
    app.setStyleSheet(stylesheet)


def main():
    # Enable high-DPI scaling (must be set before QApplication is created)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Statistical Analysis Tool")
    app.setOrganizationName("AlexTools")

    apply_dark_theme(app)

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == '__main__':
    main()