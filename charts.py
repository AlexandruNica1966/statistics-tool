"""
Matplotlib charts embedded in PyQt5 for statistical visualization.
Bilingual: Romanian / English.
Double-click or click Detach to open in a separate scalable window.

IMPORTANT: matplotlib.use('Qt5Agg') MUST be called BEFORE any other matplotlib import.
"""

import matplotlib
matplotlib.use('Qt5Agg')

import io
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

from PyQt5.QtWidgets import (
    QSizePolicy, QMainWindow, QVBoxLayout, QWidget, QLabel, QScrollArea
)
from PyQt5.QtCore import Qt as QtCore_Qt
from PyQt5.QtGui import QPalette, QColor, QPixmap

from i18n import tr, get_language, on_language_change

# Dark theme for matplotlib
DARK_BG = '#1e1e1e'
DARK_FG = '#d4d4d4'
GRID_COLOR = '#3c3c3c'
ACCENT = '#569cd6'
ACCENT2 = '#ce9178'

matplotlib.rcParams.update({
    'figure.facecolor': DARK_BG,
    'axes.facecolor': '#252526',
    'axes.edgecolor': GRID_COLOR,
    'axes.labelcolor': DARK_FG,
    'axes.titlecolor': DARK_FG,
    'text.color': DARK_FG,
    'xtick.color': DARK_FG,
    'ytick.color': DARK_FG,
    'grid.color': GRID_COLOR,
    'grid.alpha': 0.5,
    'legend.facecolor': DARK_BG,
    'legend.edgecolor': GRID_COLOR,
    'legend.labelcolor': DARK_FG,
    'figure.dpi': 100,
})


class ChartPopup(QMainWindow):
    """A standalone, resizable window showing a chart that adapts to window size."""

    def __init__(self, canvas: FigureCanvas, title: str = "Chart"):
        super().__init__()
        self.setWindowTitle(title)
        self.setMinimumSize(400, 300)
        self.resize(900, 600)
        self._canvas = canvas

        # Dark palette
        dark = QPalette()
        dark.setColor(QPalette.Window, QColor('#1e1e1e'))
        dark.setColor(QPalette.WindowText, QColor('#d4d4d4'))
        self.setPalette(dark)
        self.setStyleSheet("background-color: #1e1e1e;")

        self.img_label = QLabel()
        self.img_label.setAlignment(QtCore_Qt.AlignCenter)
        self.img_label.setStyleSheet("background-color: #1e1e1e;")
        self.img_label.setScaledContents(True)
        self.setCentralWidget(self.img_label)

        self._render()

    def _render(self):
        """Re-render the figure at the current window size."""
        w = self.img_label.width()
        h = self.img_label.height()
        if w < 10 or h < 10:
            w, h = 900, 600

        dpi = self._canvas.fig.dpi
        fig_w = w / dpi
        fig_h = h / dpi

        # Temporarily resize figure, render, restore
        old_size = self._canvas.fig.get_size_inches()
        self._canvas.fig.set_size_inches(fig_w, fig_h, forward=True)
        self._canvas.fig.tight_layout()

        buf = io.BytesIO()
        self._canvas.fig.savefig(buf, format='png', dpi=dpi, facecolor=DARK_BG, edgecolor='none')
        buf.seek(0)
        pixmap = QPixmap()
        pixmap.loadFromData(buf.read())

        self._canvas.fig.set_size_inches(*old_size, forward=True)
        self._canvas.fig.tight_layout()

        self.img_label.setPixmap(pixmap)

    def resizeEvent(self, event):
        self._render()
        super().resizeEvent(event)


class StatsCanvas(FigureCanvas):
    """Base canvas for matplotlib figures in PyQt5.
    Double-click to open in a separate scalable window.
    """

    def __init__(self, parent=None, width=16, height=9, title="Chart"):
        self.fig = Figure(figsize=(width, height), tight_layout=True)
        super().__init__(self.fig)
        self.setParent(parent)
        self.setStyleSheet("background-color: #1e1e1e;")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumHeight(120)
        self._popup_title = title

    def mouseDoubleClickEvent(self, event):
        """Open this chart in a separate scalable window."""
        self.popup = ChartPopup(self, self._popup_title)
        self.popup.show()
        self.popup.raise_()

    def set_popup_title(self, title: str):
        self._popup_title = title


def create_histogram_chart(d1: np.ndarray, d2: np.ndarray,
                           name1: str = "Dataset 1", name2: str = "Dataset 2") -> StatsCanvas:
    """Side-by-side histograms with KDE overlay."""
    canvas = StatsCanvas(width=10, title=tr("chart_hist_inner"))
    ax = canvas.fig.add_subplot(111)

    def fd_bins(data):
        iqr = np.percentile(data, 75) - np.percentile(data, 25)
        if iqr == 0:
            return max(10, int(np.sqrt(len(data))))
        bin_width = 2 * iqr / (len(data) ** (1/3))
        data_range = np.max(data) - np.min(data)
        return max(5, int(data_range / bin_width)) if bin_width > 0 else 10

    bins1 = fd_bins(d1)
    bins2 = fd_bins(d2)
    bins = max(5, int(np.mean([bins1, bins2])))

    ax.hist(d1, bins=bins, alpha=0.6, label=name1, color=ACCENT, density=True)
    ax.hist(d2, bins=bins, alpha=0.6, label=name2, color=ACCENT2, density=True)

    from scipy.stats import gaussian_kde
    x_range = np.linspace(min(d1.min(), d2.min()), max(d1.max(), d2.max()), 200)
    try:
        kde1 = gaussian_kde(d1)
        ax.plot(x_range, kde1(x_range), color=ACCENT, linewidth=2)
    except Exception:
        pass
    try:
        kde2 = gaussian_kde(d2)
        ax.plot(x_range, kde2(x_range), color=ACCENT2, linewidth=2)
    except Exception:
        pass

    ax.set_title(tr("chart_hist_inner"), fontsize=13, fontweight='bold')
    ax.set_xlabel(tr("chart_axis_value"))
    ax.set_ylabel(tr("chart_axis_density"))
    ax.legend(loc='upper right')
    ax.grid(True, alpha=0.3)

    return canvas


def create_boxplot_chart(d1: np.ndarray, d2: np.ndarray,
                         name1: str = "Dataset 1", name2: str = "Dataset 2") -> StatsCanvas:
    """Side-by-side box plots."""
    canvas = StatsCanvas(width=10, title=tr("chart_box_inner"))
    ax = canvas.fig.add_subplot(111)

    bp = ax.boxplot([d1, d2], labels=[name1, name2], patch_artist=True,
                    medianprops={'color': '#ffffff', 'linewidth': 2},
                    flierprops={'marker': 'o', 'markerfacecolor': '#ce9178', 'markersize': 6})

    bp['boxes'][0].set_facecolor(ACCENT)
    bp['boxes'][1].set_facecolor(ACCENT2)

    ax.set_title(tr("chart_box_inner"), fontsize=13, fontweight='bold')
    ax.set_ylabel(tr("chart_axis_value"))
    ax.grid(True, alpha=0.3, axis='y')

    return canvas


def create_scatter_chart(x: np.ndarray, y: np.ndarray,
                         x_name: str = "X", y_name: str = "Y",
                         slope: float = None, intercept: float = None,
                         r: float = None) -> StatsCanvas:
    """Scatter plot with optional regression line."""
    canvas = StatsCanvas(width=10, title=tr("chart_scatter_inner"))
    ax = canvas.fig.add_subplot(111)

    ax.scatter(x, y, alpha=0.6, s=30, c=ACCENT, edgecolors='none')

    if slope is not None and intercept is not None:
        x_range = np.linspace(x.min(), x.max(), 100)
        y_pred = intercept + slope * x_range
        ax.plot(x_range, y_pred, color=ACCENT2, linewidth=2,
                label=f'y = {intercept:.3f} + {slope:.3f}x')
        ax.legend(loc='best')

    title = tr("chart_scatter_inner")
    if r is not None:
        title += f"  (r = {r:.4f})"
    ax.set_title(title, fontsize=13, fontweight='bold')
    ax.set_xlabel(x_name)
    ax.set_ylabel(y_name)
    ax.grid(True, alpha=0.3)

    return canvas


def create_qq_chart(data: np.ndarray, name: str = "Dataset") -> StatsCanvas:
    """Q-Q plot for normality assessment."""
    title = tr("chart_qq_inner", name=name)
    canvas = StatsCanvas(width=10, title=title)
    ax = canvas.fig.add_subplot(111)

    from scipy.stats import probplot
    (osm, osr), (slope, intercept, r) = probplot(data, dist="norm")

    ax.scatter(osm, osr, alpha=0.6, s=20, c=ACCENT, edgecolors='none')
    ax.plot(osm, intercept + slope * osm, color=ACCENT2, linewidth=1.5, linestyle='--')

    ax.set_title(title, fontsize=12, fontweight='bold')
    ax.set_xlabel(tr("chart_axis_theoretical"))
    ax.set_ylabel(tr("chart_axis_sample"))
    ax.grid(True, alpha=0.3)

    return canvas


def create_qq_side_by_side(d1: np.ndarray, d2: np.ndarray,
                           name1: str = "Dataset 1", name2: str = "Dataset 2") -> StatsCanvas:
    """Two Q-Q plots side by side."""
    canvas = StatsCanvas(width=16, height=9, title=tr("chart_qq_title"))
    canvas.set_popup_title(tr("chart_qq_title"))

    from scipy.stats import probplot

    for i, (data, name) in enumerate([(d1, name1), (d2, name2)]):
        ax = canvas.fig.add_subplot(1, 2, i + 1)
        (osm, osr), (slope, intercept, r) = probplot(data, dist="norm")

        ax.scatter(osm, osr, alpha=0.6, s=15, c=ACCENT if i == 0 else ACCENT2, edgecolors='none')
        ax.plot(osm, intercept + slope * osm, color='#ffffff', linewidth=1, linestyle='--')

        ax.set_title(tr("chart_qq_inner", name=name), fontsize=11, fontweight='bold')
        ax.set_xlabel(tr("chart_axis_theoretical_short"))
        ax.set_ylabel(tr("chart_axis_sample_short"))
        ax.grid(True, alpha=0.3)

    return canvas


def create_residuals_chart(residuals: list, predictions: list) -> StatsCanvas:
    """Residuals vs fitted values plot."""
    canvas = StatsCanvas(width=10, title=tr("chart_resid_inner"))
    ax = canvas.fig.add_subplot(111)

    residuals = np.array(residuals)
    predictions = np.array(predictions)

    ax.scatter(predictions, residuals, alpha=0.6, s=25, c=ACCENT, edgecolors='none')
    ax.axhline(y=0, color=ACCENT2, linewidth=1.5, linestyle='--')

    ax.set_title(tr("chart_resid_inner"), fontsize=13, fontweight='bold')
    ax.set_xlabel(tr("chart_axis_fitted"))
    ax.set_ylabel(tr("chart_axis_residuals"))
    ax.grid(True, alpha=0.3)

    return canvas