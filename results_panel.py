"""
Results panel — tables and embedded matplotlib charts displayed in tabs.
Bilingual: Romanian / English with per-section commentary/interpretation.
"""

import numpy as np
from functools import partial
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTabWidget, QTableWidget,
    QTableWidgetItem, QScrollArea, QLabel, QHeaderView, QSplitter,
    QFrame, QPushButton, QSizePolicy as QtSizePolicy
)
from PyQt5.QtCore import Qt

from charts import (
    create_histogram_chart, create_boxplot_chart, create_scatter_chart,
    create_qq_side_by_side, create_residuals_chart, ChartPopup
)
from i18n import tr, get_language


TABLE_STYLE = """
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
"""

LABEL_STYLE = "font-size: 14px; font-weight: bold; color: #569cd6; padding: 8px 4px 4px 4px;"
COMMENTARY_STYLE = "font-size: 12px; color: #888888; padding: 6px 8px; background-color: #252526; border-radius: 4px; border-left: 3px solid #569cd6;"
COMMENTARY_TITLE_STYLE = "font-size: 13px; font-weight: bold; color: #dcdcaa; padding: 8px 4px 2px 4px;"

SIGNIFICANT_STYLE = "color: #4ec9b0; font-weight: bold;"
NOT_SIGNIFICANT_STYLE = "color: #ce9178; font-weight: bold;"


def make_table(rows: list, headers: list) -> QTableWidget:
    """Create a styled read-only table from row data."""
    if not rows:
        return QTableWidget()

    table = QTableWidget(len(rows), len(headers))
    table.setHorizontalHeaderLabels(headers)
    table.setStyleSheet(TABLE_STYLE)
    table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
    table.setEditTriggers(QTableWidget.NoEditTriggers)
    table.setAlternatingRowColors(True)
    table.verticalHeader().setVisible(False)

    for r, row in enumerate(rows):
        for c, val in enumerate(row):
            item = QTableWidgetItem(str(val))
            item.setTextAlignment(Qt.AlignCenter)
            table.setItem(r, c, item)

    table.resizeRowsToContents()
    total_height = table.horizontalHeader().height() + sum(
        table.rowHeight(r) for r in range(table.rowCount())
    ) + 4
    table.setMaximumHeight(total_height)

    return table


def format_pvalue(p: float) -> str:
    """Format p-value nicely."""
    if p < 0.0001:
        return "p < 0.0001"
    elif p < 0.001:
        return f"p = {p:.4f}"
    elif p < 0.01:
        return f"p = {p:.5f}"
    else:
        return f"p = {p:.5f}"


def _commentary_label(text: str) -> QLabel:
    """Create a styled commentary label."""
    lbl = QLabel(text)
    lbl.setStyleSheet(COMMENTARY_STYLE)
    lbl.setWordWrap(True)
    return lbl


def _strength_tr(strength_en: str) -> str:
    """Translate strength labels."""
    key = f"strength_{strength_en.replace(' ', '_')}"
    return tr(key)


class ResultsPanel(QWidget):
    """Main results panel with all statistical outputs."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.results = None
        self.d1 = None
        self.d2 = None
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #3c3c3c; background-color: #1e1e1e; }
            QTabBar::tab { background-color: #2d2d2d; color: #888888; padding: 8px 16px;
                          font-size: 12px; font-weight: bold; border: 1px solid #3c3c3c;
                          border-bottom: none; margin-right: 1px; }
            QTabBar::tab:selected { background-color: #1e1e1e; color: #569cd6;
                                   border-bottom: 2px solid #569cd6; }
            QTabBar::tab:hover { color: #d4d4d4; }
        """)
        layout.addWidget(self.tabs)

    def update_results(self, results: dict, d1: np.ndarray, d2: np.ndarray):
        """Populate all result tabs."""
        self.results = results
        self.d1 = d1
        self.d2 = d2

        # Clear existing tabs
        while self.tabs.count() > 0:
            self.tabs.removeTab(0)

        if "error" in results:
            err_widget = QLabel(f"Error: {results['error']}")
            err_widget.setStyleSheet("color: #ce9178; font-size: 16px; padding: 20px;")
            err_widget.setAlignment(Qt.AlignCenter)
            self.tabs.addTab(err_widget, "Error")
            return

        name1 = self.results["descriptive1"]["name"]
        name2 = self.results["descriptive2"]["name"]
        self._add_descriptive_tab(name1, name2)
        self._add_correlation_tab(name1, name2)
        self._add_regression_tab(name1, name2)
        self._add_ttests_tab(name1, name2)
        self._add_normality_tab(name1, name2)
        self._add_distribution_comparison_tab()
        self._add_charts_tab(name1, name2)

    def _detach_chart(self, chart, title):
        """Open a chart in a separate popup window."""
        popup = ChartPopup(chart, title)
        popup.show()
        popup.raise_()
        popup.activateWindow()

    def _scroll_area(self, widget) -> QScrollArea:
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(widget)
        scroll.setStyleSheet("QScrollArea { border: none; background-color: #1e1e1e; }")
        return scroll

    # ═══════════════════════════════════════════
    # DESCRIPTIVE TAB
    # ═══════════════════════════════════════════
    def _add_descriptive_tab(self, name1: str, name2: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(4)

        desc1 = self.results["descriptive1"]
        desc2 = self.results["descriptive2"]

        title = QLabel(tr("desc_title"))
        title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(title)

        headers = [tr("desc_col_stat"), name1, name2]
        rows = [
            [tr("row_n"), str(desc1["n"]), str(desc2["n"])],
            [tr("row_mean"), f"{desc1['mean']:.6f}", f"{desc2['mean']:.6f}"],
            [tr("row_median"), f"{desc1['median']:.6f}", f"{desc2['median']:.6f}"],
            [tr("row_mode"), f"{desc1['mode']:.6f}", f"{desc2['mode']:.6f}"],
            [tr("row_std"), f"{desc1['std']:.6f}", f"{desc2['std']:.6f}"],
            [tr("row_variance"), f"{desc1['variance']:.6f}", f"{desc2['variance']:.6f}"],
            [tr("row_sem"), f"{desc1['sem']:.6f}", f"{desc2['sem']:.6f}"],
            [tr("row_min"), f"{desc1['min']:.6f}", f"{desc2['min']:.6f}"],
            [tr("row_q1"), f"{desc1['q1']:.6f}", f"{desc2['q1']:.6f}"],
            [tr("row_q3"), f"{desc1['q3']:.6f}", f"{desc2['q3']:.6f}"],
            [tr("row_iqr"), f"{desc1['iqr']:.6f}", f"{desc2['iqr']:.6f}"],
            [tr("row_max"), f"{desc1['max']:.6f}", f"{desc2['max']:.6f}"],
            [tr("row_range"), f"{desc1['range']:.6f}", f"{desc2['range']:.6f}"],
            [tr("row_skewness"), f"{desc1['skewness']:.4f}", f"{desc2['skewness']:.4f}"],
            [tr("row_kurtosis"), f"{desc1['kurtosis']:.4f}", f"{desc2['kurtosis']:.4f}"],
            [tr("row_ci_mean"), f"[{desc1['ci_95_lower']:.4f}, {desc1['ci_95_upper']:.4f}]",
                                f"[{desc2['ci_95_lower']:.4f}, {desc2['ci_95_upper']:.4f}]"],
            [tr("row_sum"), f"{desc1['sum']:.4f}", f"{desc2['sum']:.4f}"],
        ]

        layout.addWidget(make_table(rows, headers))

        # ── Commentary ──
        ctitle = QLabel(tr("commentary_title"))
        ctitle.setStyleSheet(COMMENTARY_TITLE_STYLE)
        layout.addWidget(ctitle)

        # Intro
        intro = tr("comment_desc_intro",
                   n1=desc1["n"], m1=desc1["mean"], s1=desc1["std"],
                   n2=desc2["n"], m2=desc2["mean"], s2=desc2["std"])
        layout.addWidget(_commentary_label(intro))

        # Skewness comment (average of both)
        avg_skew = (abs(desc1["skewness"]) + abs(desc2["skewness"])) / 2
        if avg_skew < 0.5:
            layout.addWidget(_commentary_label(tr("comment_skew_sym")))
        elif avg_skew < 1.0:
            layout.addWidget(_commentary_label(tr("comment_skew_mild")))
        else:
            layout.addWidget(_commentary_label(tr("comment_skew_strong")))

        # Kurtosis comment
        avg_kurt = (desc1["kurtosis"] + desc2["kurtosis"]) / 2
        if abs(avg_kurt) < 1:
            layout.addWidget(_commentary_label(tr("comment_kurt_meso")))
        elif avg_kurt > 0:
            layout.addWidget(_commentary_label(tr("comment_kurt_heavy")))
        else:
            layout.addWidget(_commentary_label(tr("comment_kurt_light")))

        layout.addStretch()
        self.tabs.addTab(self._scroll_area(widget), tr("tab_descriptive"))

    # ═══════════════════════════════════════════
    # CORRELATION TAB
    # ═══════════════════════════════════════════
    def _add_correlation_tab(self, name1: str, name2: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        # ── Pearson ──
        pearson = self.results["pearson"]
        p_title = QLabel(tr("corr_pearson_title"))
        p_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(p_title)

        p_headers = [tr("corr_col_measure"), tr("corr_col_value")]
        p_style = SIGNIFICANT_STYLE if pearson["significant"] else NOT_SIGNIFICANT_STYLE

        p_rows = [
            [tr("corr_r"), f"{pearson['r']:.6f}"],
            [tr("corr_r2"), f"{pearson['r2']:.6f}"],
            [tr("corr_pvalue"), format_pvalue(pearson['p_value'])],
            [tr("corr_ci"), f"[{pearson['ci_95_lower']:.4f}, {pearson['ci_95_upper']:.4f}]"],
            [tr("corr_strength"), _strength_tr(pearson["strength"])],
            [tr("corr_conclusion"),
             f"<span style='{p_style}'>" +
             (tr("corr_significant") if pearson['significant'] else tr("corr_not_significant")) +
             " (α = 0.05)</span>"],
        ]
        layout.addWidget(make_table(p_rows, p_headers))

        # ── Pearson commentary ──
        direction = tr("direction_positive") if pearson['r'] >= 0 else tr("direction_negative")
        strength_tr = _strength_tr(pearson['strength'])
        layout.addWidget(_commentary_label(
            tr("comment_corr_pearson", r=pearson['r'], strength=strength_tr,
               direction=direction, pct=pearson['r2']*100, r2=pearson['r2'])))
        if pearson['significant']:
            layout.addWidget(_commentary_label(
                tr("comment_corr_significant", p=format_pvalue(pearson['p_value']))))
        else:
            layout.addWidget(_commentary_label(
                tr("comment_corr_not_significant", p=format_pvalue(pearson['p_value']))))

        # ── Spearman ──
        spearman = self.results["spearman"]
        s_title = QLabel(tr("corr_spearman_title"))
        s_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(s_title)

        s_style = SIGNIFICANT_STYLE if spearman["significant"] else NOT_SIGNIFICANT_STYLE
        s_rows = [
            [tr("corr_rho"), f"{spearman['rho']:.6f}"],
            [tr("corr_pvalue"), format_pvalue(spearman['p_value'])],
            [tr("corr_n_pairs"), str(spearman['n'])],
            [tr("corr_strength"), _strength_tr(spearman["strength"])],
            [tr("corr_conclusion"),
             f"<span style='{s_style}'>" +
             (tr("corr_significant") if spearman['significant'] else tr("corr_not_significant")) +
             " (α = 0.05)</span>"],
        ]
        layout.addWidget(make_table(s_rows, [tr("desc_col_stat"), tr("corr_col_value")]))

        # ── Spearman commentary ──
        s_dir = tr("direction_positive") if spearman['rho'] >= 0 else tr("direction_negative")
        s_str = _strength_tr(spearman['strength'])
        layout.addWidget(_commentary_label(
            tr("comment_corr_spearman", rho=spearman['rho'], strength=s_str, direction=s_dir)))

        layout.addStretch()
        self.tabs.addTab(self._scroll_area(widget), tr("tab_correlations"))

    # ═══════════════════════════════════════════
    # REGRESSION TAB
    # ═══════════════════════════════════════════
    def _add_regression_tab(self, name1: str, name2: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        reg = self.results["regression_2on1"]  # Dataset 2 ~ Dataset 1

        r_title = QLabel(tr("reg_title", y=reg['y_name'], x=reg['x_name']))
        r_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(r_title)

        eq_label = QLabel(tr("reg_eq", eq=reg['equation']))
        eq_label.setStyleSheet("font-size: 13px; color: #dcdcaa; padding: 4px; font-family: monospace;")
        layout.addWidget(eq_label)

        reg_style = SIGNIFICANT_STYLE if reg["significant"] else NOT_SIGNIFICANT_STYLE
        reg_headers = [tr("desc_col_stat"), tr("corr_col_value")]

        reg_rows = [
            [tr("reg_r2"), f"{reg['r2']:.6f}"],
            [tr("reg_r2_adj"), f"{reg['r2_adj']:.6f}"],
            [tr("reg_f"), f"F({1}, {reg['df_residual']}) = {reg['f_statistic']:.4f}"],
            [tr("reg_f_pval"), format_pvalue(reg['f_pvalue'])],
            ["", ""],
            [tr("reg_intercept"), f"{reg['intercept']:.6f}"],
            [tr("reg_intercept_se"), f"{reg['intercept_se']:.6f}"],
            [tr("reg_intercept_t"), f"{reg['intercept_t']:.4f}"],
            [tr("reg_intercept_p"), format_pvalue(reg['intercept_p'])],
            [tr("reg_intercept_ci"), f"[{reg['intercept_ci_lower']:.4f}, {reg['intercept_ci_upper']:.4f}]"],
            ["", ""],
            [tr("reg_slope"), f"{reg['slope']:.6f}"],
            [tr("reg_slope_se"), f"{reg['slope_se']:.6f}"],
            [tr("reg_slope_t"), f"{reg['slope_t']:.4f}"],
            [tr("reg_slope_p"), format_pvalue(reg['slope_p'])],
            [tr("reg_slope_ci"), f"[{reg['slope_ci_lower']:.4f}, {reg['slope_ci_upper']:.4f}]"],
            ["", ""],
            [tr("reg_mse"), f"{reg['mse']:.6f}"],
            [tr("reg_n"), str(reg['n'])],
            [tr("reg_model_sig"),
             f"<span style='{reg_style}'>" +
             (tr("reg_yes") if reg['significant'] else tr("reg_no")) +
             " (α = 0.05)</span>"],
        ]
        layout.addWidget(make_table(reg_rows, reg_headers))

        # ── Regression commentary ──
        ctitle = QLabel(tr("commentary_title"))
        ctitle.setStyleSheet(COMMENTARY_TITLE_STYLE)
        layout.addWidget(ctitle)

        layout.addWidget(_commentary_label(
            tr("comment_reg_intro", pct=reg['r2']*100, y=reg['y_name'], r2=reg['r2'])))
        layout.addWidget(_commentary_label(
            tr("comment_reg_slope", x=reg['x_name'], y=reg['y_name'], slope=reg['slope'])))
        if reg['significant']:
            layout.addWidget(_commentary_label(tr("comment_reg_sig")))
        else:
            layout.addWidget(_commentary_label(tr("comment_reg_not_sig")))

        layout.addStretch()
        self.tabs.addTab(self._scroll_area(widget), tr("tab_regression"))

    # ═══════════════════════════════════════════
    # t-TESTS TAB
    # ═══════════════════════════════════════════
    def _add_ttests_tab(self, name1: str, name2: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        ind = self.results["independent_ttest"]

        # ── Independent t-tests ──
        ind_title = QLabel(tr("ttest_ind_title"))
        ind_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(ind_title)

        ind_headers = [tr("ttest_col_stat"), tr("ttest_col_student"), tr("ttest_col_welch")]
        ind_rows = [
            [tr("ttest_t"), f"{ind['student_t']:.4f}", f"{ind['welch_t']:.4f}"],
            [tr("ttest_df"), str(ind['student_df']),
             "≈ " + str(round(
                (ind['welch_t']**2) / (ind['mean_difference']**2) *
                (ind['n1'] + ind['n2'] - 2) if ind['welch_t'] != 0 else 0, 1))],
            [tr("ttest_pvalue"), format_pvalue(ind['student_pvalue']), format_pvalue(ind['welch_pvalue'])],
            [tr("ttest_significant"),
             tr("ttest_yes") if ind['student_significant'] else tr("ttest_no"),
             tr("ttest_yes") if ind['welch_significant'] else tr("ttest_no")],
        ]
        layout.addWidget(make_table(ind_rows, ind_headers))

        # Levene's test result
        lev_style = "color: #4ec9b0;" if ind['variances_equal'] else "color: #ce9178;"
        if ind['variances_equal']:
            levene_text = tr("levene_equal", f=ind['levene_statistic'],
                            p=format_pvalue(ind['levene_pvalue']))
        else:
            levene_text = tr("levene_unequal", f=ind['levene_statistic'],
                            p=format_pvalue(ind['levene_pvalue']))
        lev_label = QLabel(f"<span style='{lev_style}'>{levene_text}</span>")
        lev_label.setStyleSheet("font-size: 12px; padding: 4px;")
        lev_label.setWordWrap(True)
        layout.addWidget(lev_label)

        # t-test commentary
        ctitle = QLabel(tr("commentary_title"))
        ctitle.setStyleSheet(COMMENTARY_TITLE_STYLE)
        layout.addWidget(ctitle)

        layout.addWidget(_commentary_label(
            tr("comment_ttest_intro", diff=ind['mean_difference'],
               cil=ind['ci_95_lower'], ciu=ind['ci_95_upper'],
               d=ind['cohens_d'], d_strength=_strength_tr(ind['cohens_d_strength']))))

        var_status = tr("var_equal") if ind['variances_equal'] else tr("var_unequal")
        which = "Student" if ind['variances_equal'] else "Welch"
        layout.addWidget(_commentary_label(
            tr("comment_ttest_which", var_status=var_status, which=which)))

        # Use Welch p for significance check (more robust)
        if ind['welch_significant']:
            layout.addWidget(_commentary_label(tr("comment_ttest_sig")))
        else:
            layout.addWidget(_commentary_label(tr("comment_ttest_not_sig")))

        # ── Paired t-test ──
        paired = self.results["paired_ttest"]
        p_title = QLabel(tr("ttest_paired_title"))
        p_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(p_title)

        p_style = SIGNIFICANT_STYLE if paired["significant"] else NOT_SIGNIFICANT_STYLE
        p_rows = [
            [tr("ttest_paired_n"), str(paired['n_pairs'])],
            [tr("ttest_paired_mean_diff"), f"{paired['mean_difference']:.6f}"],
            [tr("ttest_paired_std_diff"), f"{paired['std_difference']:.6f}"],
            [tr("ttest_paired_t"), f"t({paired['df']}) = {paired['t_statistic']:.4f}"],
            [tr("ttest_paired_p"), format_pvalue(paired['p_value'])],
            [tr("ttest_paired_ci"), f"[{paired['ci_95_lower']:.4f}, {paired['ci_95_upper']:.4f}]"],
            [tr("ttest_paired_d"), f"{paired['cohens_d']:.4f} ({_strength_tr(paired['cohens_d_strength'])})"],
            [tr("ttest_paired_conclusion"),
             f"<span style='{p_style}'>" +
             (tr("ttest_paired_sig") if paired['significant'] else tr("ttest_paired_not_sig")) +
             "</span>"],
        ]
        layout.addWidget(make_table(p_rows, [tr("desc_col_stat"), tr("corr_col_value")]))

        # Paired commentary
        layout.addWidget(_commentary_label(
            tr("comment_ttest_paired", diff=paired['mean_difference'], d=paired['cohens_d'])))

        # ── One-sample t-tests ──
        os1 = self.results["onesample_ttest1"]
        os2 = self.results["onesample_ttest2"]

        os_title = QLabel(tr("ttest_one_title"))
        os_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(os_title)

        os_headers = [tr("desc_col_stat"), name1, name2]
        os_rows = [
            [tr("ttest_one_h0") + " ", str(os1['hypothesized_mean']), str(os2['hypothesized_mean'])],
            [tr("ttest_one_mean"), f"{os1['mean']:.4f}", f"{os2['mean']:.4f}"],
            [tr("ttest_one_t"),
             f"t({os1['df']}) = {os1['t_statistic']:.4f}",
             f"t({os2['df']}) = {os2['t_statistic']:.4f}"],
            [tr("ttest_one_p"), format_pvalue(os1['p_value']), format_pvalue(os2['p_value'])],
            [tr("ttest_one_ci"),
             f"[{os1['ci_95_lower']:.4f}, {os1['ci_95_upper']:.4f}]",
             f"[{os2['ci_95_lower']:.4f}, {os2['ci_95_upper']:.4f}]"],
            [tr("ttest_one_d"), f"{os1['cohens_d']:.4f}", f"{os2['cohens_d']:.4f}"],
            [tr("ttest_one_sig"),
             tr("ttest_yes") if os1['significant'] else tr("ttest_no"),
             tr("ttest_yes") if os2['significant'] else tr("ttest_no")],
        ]
        layout.addWidget(make_table(os_rows, os_headers))

        layout.addStretch()
        self.tabs.addTab(self._scroll_area(widget), tr("tab_ttests"))

    # ═══════════════════════════════════════════
    # NORMALITY TAB
    # ═══════════════════════════════════════════
    def _add_normality_tab(self, name1: str, name2: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        n_title = QLabel(tr("norm_title"))
        n_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(n_title)

        n1 = self.results["normality1"]
        n2 = self.results["normality2"]

        n_headers = [tr("norm_col_test"), name1, name2]
        n_rows = [
            [tr("row_n"), str(n1['n']), str(n2['n'])],
            [tr("norm_shapiro_w"),
             f"{n1['shapiro_statistic']:.4f}" if n1['shapiro_statistic'] else tr("norm_na"),
             f"{n2['shapiro_statistic']:.4f}" if n2['shapiro_statistic'] else tr("norm_na")],
            [tr("norm_shapiro_p"),
             format_pvalue(n1['shapiro_pvalue']) if n1['shapiro_pvalue'] else tr("norm_na"),
             format_pvalue(n2['shapiro_pvalue']) if n2['shapiro_pvalue'] else tr("norm_na")],
            [tr("norm_shapiro_normal"),
             (tr("norm_yes") if n1['shapiro_normal'] else tr("norm_no"))
                if n1['shapiro_normal'] is not None else tr("norm_na"),
             (tr("norm_yes") if n2['shapiro_normal'] else tr("norm_no"))
                if n2['shapiro_normal'] is not None else tr("norm_na")],
            ["", "", ""],
            [tr("norm_dagostino_k2"),
             f"{n1['dagostino_statistic']:.4f}", f"{n2['dagostino_statistic']:.4f}"],
            [tr("norm_dagostino_p"),
             format_pvalue(n1['dagostino_pvalue']), format_pvalue(n2['dagostino_pvalue'])],
            [tr("norm_dagostino_normal"),
             tr("norm_yes") if n1['dagostino_normal'] else tr("norm_no"),
             tr("norm_yes") if n2['dagostino_normal'] else tr("norm_no")],
        ]
        layout.addWidget(make_table(n_rows, n_headers))

        # ── Normality commentary ──
        ctitle = QLabel(tr("commentary_title"))
        ctitle.setStyleSheet(COMMENTARY_TITLE_STYLE)
        layout.addWidget(ctitle)

        n1_normal = n1['shapiro_normal'] if n1['shapiro_normal'] is not None else n1['dagostino_normal']
        n2_normal = n2['shapiro_normal'] if n2['shapiro_normal'] is not None else n2['dagostino_normal']

        if n1_normal and n2_normal:
            layout.addWidget(_commentary_label(tr("comment_norm_both")))
        elif n1_normal or n2_normal:
            layout.addWidget(_commentary_label(tr("comment_norm_one")))
        else:
            layout.addWidget(_commentary_label(tr("comment_norm_neither")))

        # Note at bottom
        note = QLabel(tr("comment_norm_note"))
        note.setStyleSheet("color: #888888; font-size: 11px; padding: 8px;")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()
        self.tabs.addTab(self._scroll_area(widget), tr("tab_normality"))

    # ═══════════════════════════════════════════
    # DISTRIBUTION COMPARISON TAB
    # ═══════════════════════════════════════════
    def _add_distribution_comparison_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(8)

        dc = self.results["distribution_comparison"]

        dc_title = QLabel(tr("dist_title"))
        dc_title.setStyleSheet(LABEL_STYLE)
        layout.addWidget(dc_title)

        dc_rows = [
            [tr("dist_ks_d"), f"{dc['ks_statistic']:.4f}"],
            [tr("dist_ks_p"), format_pvalue(dc['ks_pvalue'])],
            [tr("dist_ks_conc"), dc['ks_conclusion']],
            ["", ""],
            [tr("dist_mw_u"), f"{dc['mannwhitney_u']:.4f}"],
            [tr("dist_mw_p"), format_pvalue(dc['mannwhitney_pvalue'])],
            [tr("dist_mw_sig"), tr("ttest_yes") if dc['mannwhitney_significant'] else tr("ttest_no")],
            [tr("dist_rb_r"), f"{dc['rank_biserial_correlation']:.4f}"],
        ]
        layout.addWidget(make_table(dc_rows, [tr("desc_col_stat"), tr("corr_col_value")]))

        # ── Distribution commentary ──
        ctitle = QLabel(tr("commentary_title"))
        ctitle.setStyleSheet(COMMENTARY_TITLE_STYLE)
        layout.addWidget(ctitle)

        ks_word = tr("comment_dist_ks_suggests") if dc['ks_significant'] else tr("comment_dist_ks_not")
        layout.addWidget(_commentary_label(tr("comment_dist_ks", result=ks_word)))

        mw_word = tr("comment_dist_mw_indicates") if dc['mannwhitney_significant'] else tr("comment_dist_mw_not")
        layout.addWidget(_commentary_label(tr("comment_dist_mw", result=mw_word)))

        note = QLabel(tr("comment_dist_ks_note"))
        note.setStyleSheet("color: #888888; font-size: 11px; padding: 8px;")
        note.setWordWrap(True)
        layout.addWidget(note)

        layout.addStretch()
        self.tabs.addTab(self._scroll_area(widget), tr("tab_distributions"))

    # ═══════════════════════════════════════════
    # CHARTS TAB
    # ═══════════════════════════════════════════
    def _add_charts_tab(self, name1: str, name2: str):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(12)

        reg = self.results["regression_2on1"]
        n = min(len(self.d1), len(self.d2))

        def _wrap(chart, title):
            """Wrap a chart with title and double-click hint."""
            container = QWidget()
            cl = QVBoxLayout(container)
            cl.setContentsMargins(0, 2, 0, 2)
            cl.setSpacing(2)

            bar = QHBoxLayout()
            bar.setSpacing(6)
            tl = QLabel(title)
            tl.setStyleSheet(LABEL_STYLE)
            bar.addWidget(tl)
            bar.addStretch()

            hint = QLabel("💡 " + tr("hint_double_click"))
            hint.setStyleSheet("color: #aaaaaa; font-size: 13px; padding: 2px 6px;")
            bar.addWidget(hint)
            cl.addLayout(bar)
            cl.addWidget(chart)
            return container

        # Histograms
        hist_chart = create_histogram_chart(self.d1, self.d2, name1, name2)
        layout.addWidget(_wrap(hist_chart, tr("chart_hist_title")))

        # Box plots
        box_chart = create_boxplot_chart(self.d1, self.d2, name1, name2)
        layout.addWidget(_wrap(box_chart, tr("chart_box_title")))

        # Scatter + regression
        scatter_chart = create_scatter_chart(
            self.d1[:n], self.d2[:n], name1, name2,
            slope=reg['slope'], intercept=reg['intercept'],
            r=self.results['pearson']['r'])
        layout.addWidget(_wrap(scatter_chart, tr("chart_scatter_title")))

        # Q-Q plots side by side
        qq_chart = create_qq_side_by_side(self.d1, self.d2, name1, name2)
        layout.addWidget(_wrap(qq_chart, tr("chart_qq_title")))

        # Residuals
        resid_chart = create_residuals_chart(reg['residuals'], reg['predictions'])
        layout.addWidget(_wrap(resid_chart, tr("chart_resid_title")))

        layout.addStretch()
        self.tabs.addTab(widget, tr("tab_charts"))