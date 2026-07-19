"""
Internationalization module — Romanian (ro) and English (en) strings.
Usage: tr("key") returns the current language string.
Call set_language("ro") or set_language("en") to switch.
"""

_current_lang = "en"
_observers = []


def set_language(lang: str):
    global _current_lang
    if lang in ("en", "ro"):
        _current_lang = lang
        for cb in _observers:
            cb(lang)


def get_language() -> str:
    return _current_lang


def on_language_change(callback):
    """Register a callback(lang) for language changes."""
    _observers.append(callback)


def tr(key: str, **kwargs) -> str:
    """Return the string for `key` in the current language, with optional format kwargs."""
    s = STRINGS.get(key, {}).get(_current_lang, key)
    if kwargs:
        s = s.format(**kwargs)
    return s


# ───────────────────────────────────────────────────────────
# All translatable strings: { "key": { "en": "...", "ro": "..." } }
# ───────────────────────────────────────────────────────────

STRINGS = {
    # ── App branding ──
    "app_title": {
        "en": "Statistical Analysis Tool — Two-Dataset Comparison",
        "ro": "Instrument de Analiză Statistică — Comparație Două Seturi de Date",
    },
    "app_credit": {
        "en": "Made with ❤️ by Alex Nica — for friends, students & researchers. Vibe code with agent Gogu",
        "ro": "Creat cu ❤️ de Alex Nica — pentru prieteni, studenți și cercetători. Vibe code cu agentul Gogu",
    },
    "app_org": {
        "en": "AlexTools",
        "ro": "AlexTools",
    },

    # ── Toolbar ──
    "btn_analyze": {"en": "▶ Run Analysis", "ro": "▶ Rulează Analiza"},
    "btn_hyp_mean": {"en": "🎯 Set H₀ Means", "ro": "🎯 Setează H₀ Medii"},
    "btn_lang_en": {"en": "EN", "ro": "EN"},
    "btn_lang_ro": {"en": "RO", "ro": "RO"},
    "status_ready": {
        "en": "Ready — Alex's Statistical Analysis Tool",
        "ro": "Gata — Instrumentul de Analiză Statistică al lui Alex",
    },
    "status_enter_data": {
        "en": "Enter data in both datasets, then click Analyze",
        "ro": "Introdu date în ambele seturi, apoi apasă Rulează Analiza",
    },
    "status_running": {"en": "Running analysis...", "ro": "Rulez analiza..."},
    "status_done": {
        "en": "✓ Analysis complete ({n1} + {n2} values)",
        "ro": "✓ Analiză completă ({n1} + {n2} valori)",
    },
    "statusbar_done": {
        "en": "Analysis complete — Dataset 1: {n1} values, Dataset 2: {n2} values",
        "ro": "Analiză completă — Setul 1: {n1} valori, Setul 2: {n2} valori",
    },
    "status_failed": {"en": "Analysis failed", "ro": "Analiza a eșuat"},

    # ── Dialogs ──
    "dlg_hyp_title": {
        "en": "One-Sample t-Test Parameters",
        "ro": "Parametrii testului t pentru un eșantion",
    },
    "dlg_hyp_mean1": {"en": "H₀ mean for Dataset 1:", "ro": "Media H₀ pentru Setul 1:"},
    "dlg_hyp_mean2": {"en": "H₀ mean for Dataset 2:", "ro": "Media H₀ pentru Setul 2:"},
    "dlg_paste_title": {"en": "Paste Data", "ro": "Lipește Date"},
    "dlg_paste_label": {
        "en": "Paste data from spreadsheet (tab/comma/space separated, one row per line):",
        "ro": "Lipește date din foaie de calcul (separate prin tab/virgulă/spațiu, un rând pe linie):",
    },

    # ── Data panel ──
    "ds1_title": {"en": "Dataset 1 (X)", "ro": "Setul 1 (X)"},
    "ds2_title": {"en": "Dataset 2 (Y)", "ro": "Setul 2 (Y)"},
    "ds1_tab": {"en": "Dataset 1", "ro": "Setul 1"},
    "ds2_tab": {"en": "Dataset 2", "ro": "Setul 2"},
    "table_header": {"en": "Value", "ro": "Valoare"},
    "btn_import": {"en": "📂 Import", "ro": "📂 Importă"},
    "btn_paste": {"en": "📋 Paste", "ro": "📋 Lipește"},
    "btn_clear": {"en": "🗑 Clear", "ro": "🗑 Șterge"},
    "lbl_count": {"en": "{n} values", "ro": "{n} valori"},
    "dlg_import_title": {
        "en": "Import {name}",
        "ro": "Importă {name}",
    },
    "dlg_import_filter": {
        "en": "Data Files (*.csv *.xlsx *.xls *.txt);;CSV (*.csv);;Excel (*.xlsx *.xls);;Text (*.txt);;All Files (*)",
        "ro": "Fișiere de date (*.csv *.xlsx *.xls *.txt);;CSV (*.csv);;Excel (*.xlsx *.xls);;Text (*.txt);;Toate fișierele (*)",
    },

    # ── Error messages ──
    "err_insufficient_1": {
        "en": "Dataset 1 must have at least 2 numeric values.",
        "ro": "Setul 1 trebuie să aibă cel puțin 2 valori numerice.",
    },
    "err_insufficient_2": {
        "en": "Dataset 2 must have at least 2 numeric values.",
        "ro": "Setul 2 trebuie să aibă cel puțin 2 valori numerice.",
    },
    "err_import_no_numeric": {
        "en": "No numeric column found in Excel file.",
        "ro": "Nicio coloană numerică găsită în fișierul Excel.",
    },
    "err_import_no_values": {
        "en": "No numeric values found in file.",
        "ro": "Nicio valoare numerică găsită în fișier.",
    },
    "err_paste_no_values": {
        "en": "No numeric values found.",
        "ro": "Nicio valoare numerică găsită.",
    },
    "err_import_error": {"en": "Import Error", "ro": "Eroare la import"},
    "err_paste_error": {"en": "Paste Error", "ro": "Eroare la lipire"},
    "err_analysis_error": {"en": "Analysis Error", "ro": "Eroare de analiză"},

    # ── Result tabs ──
    "tab_descriptive": {"en": "📊 Descriptive", "ro": "📊 Statistică Descriptivă"},
    "tab_correlations": {"en": "🔗 Correlations", "ro": "🔗 Corelații"},
    "tab_regression": {"en": "📈 Regression", "ro": "📈 Regresie"},
    "tab_ttests": {"en": "🔬 t-Tests", "ro": "🔬 Teste t"},
    "tab_normality": {"en": "📐 Normality", "ro": "📐 Normalitate"},
    "tab_distributions": {"en": "📊 Distributions", "ro": "📊 Distribuții"},
    "tab_charts": {"en": "📉 Charts", "ro": "📉 Grafice"},

    # ── Descriptive headers ──
    "desc_title": {"en": "Descriptive Statistics", "ro": "Statistică Descriptivă"},
    "desc_col_stat": {"en": "Statistic", "ro": "Statistică"},
    "row_n": {"en": "N", "ro": "N"},
    "row_mean": {"en": "Mean", "ro": "Medie"},
    "row_median": {"en": "Median", "ro": "Mediană"},
    "row_mode": {"en": "Mode", "ro": "Mod"},
    "row_std": {"en": "Std Dev", "ro": "Dev. Std"},
    "row_variance": {"en": "Variance", "ro": "Varianță"},
    "row_sem": {"en": "SEM", "ro": "ESM"},
    "row_min": {"en": "Min", "ro": "Min"},
    "row_q1": {"en": "Q1 (25%)", "ro": "Q1 (25%)"},
    "row_q3": {"en": "Q3 (75%)", "ro": "Q3 (75%)"},
    "row_iqr": {"en": "IQR", "ro": "IIQ"},
    "row_max": {"en": "Max", "ro": "Max"},
    "row_range": {"en": "Range", "ro": "Amplitudine"},
    "row_skewness": {"en": "Skewness", "ro": "Asimetrie"},
    "row_kurtosis": {"en": "Kurtosis", "ro": "Curtosis"},
    "row_ci_mean": {"en": "95% CI Mean", "ro": "IC 95% Medie"},
    "row_sum": {"en": "Sum", "ro": "Sumă"},

    # ── Correlation ──
    "corr_pearson_title": {"en": "Pearson Correlation (r)", "ro": "Corelația Pearson (r)"},
    "corr_spearman_title": {
        "en": "Spearman Rank Correlation (ρ)",
        "ro": "Corelația Spearman (ρ)",
    },
    "corr_col_measure": {"en": "Measure", "ro": "Măsură"},
    "corr_col_value": {"en": "Value", "ro": "Valoare"},
    "corr_r": {"en": "r (correlation coefficient)", "ro": "r (coeficient de corelație)"},
    "corr_r2": {
        "en": "r² (coefficient of determination)",
        "ro": "r² (coeficient de determinare)",
    },
    "corr_pvalue": {"en": "p-value", "ro": "valoarea p"},
    "corr_ci": {"en": "95% CI for r", "ro": "IC 95% pentru r"},
    "corr_strength": {"en": "Strength", "ro": "Forța"},
    "corr_conclusion": {"en": "Conclusion", "ro": "Concluzie"},
    "corr_rho": {
        "en": "ρ (rho — population coefficient)",
        "ro": "ρ (rho — coeficient populațional)",
    },
    "corr_n_pairs": {"en": "N (pairs)", "ro": "N (perechi)"},
    "corr_significant": {"en": "✓ Significant", "ro": "✓ Semnificativ"},
    "corr_not_significant": {"en": "✗ Not significant", "ro": "✗ Nesemnificativ"},

    # ── Regression ──
    "reg_title": {
        "en": "Linear Regression: {y} ~ {x}",
        "ro": "Regresie Liniară: {y} ~ {x}",
    },
    "reg_eq": {"en": "Equation: {eq}", "ro": "Ecuația: {eq}"},
    "reg_r2": {"en": "R²", "ro": "R²"},
    "reg_r2_adj": {"en": "Adjusted R²", "ro": "R² Ajustat"},
    "reg_f": {"en": "F-statistic", "ro": "Statistică F"},
    "reg_f_pval": {"en": "F p-value", "ro": "Valoarea p F"},
    "reg_intercept": {"en": "Intercept", "ro": "Intercept"},
    "reg_intercept_se": {"en": "Intercept SE", "ro": "ES Intercept"},
    "reg_intercept_t": {"en": "Intercept t", "ro": "t Intercept"},
    "reg_intercept_p": {"en": "Intercept p", "ro": "p Intercept"},
    "reg_intercept_ci": {"en": "Intercept 95% CI", "ro": "IC 95% Intercept"},
    "reg_slope": {"en": "Slope", "ro": "Pantă"},
    "reg_slope_se": {"en": "Slope SE", "ro": "ES Pantă"},
    "reg_slope_t": {"en": "Slope t", "ro": "t Pantă"},
    "reg_slope_p": {"en": "Slope p", "ro": "p Pantă"},
    "reg_slope_ci": {"en": "Slope 95% CI", "ro": "IC 95% Pantă"},
    "reg_mse": {"en": "MSE", "ro": "EMC"},
    "reg_n": {"en": "N", "ro": "N"},
    "reg_model_sig": {"en": "Model significant", "ro": "Model semnificativ"},
    "reg_yes": {"en": "✓ Yes", "ro": "✓ Da"},
    "reg_no": {"en": "✗ No", "ro": "✗ Nu"},

    # ── t-Tests ──
    "ttest_ind_title": {
        "en": "Independent Samples t-Tests",
        "ro": "Teste t pentru Eșantioane Independente",
    },
    "ttest_col_stat": {"en": "Statistic", "ro": "Statistică"},
    "ttest_col_student": {
        "en": "Student's t (equal var)",
        "ro": "t Student (varianțe egale)",
    },
    "ttest_col_welch": {
        "en": "Welch's t (unequal var)",
        "ro": "t Welch (varianțe inegale)",
    },
    "ttest_t": {"en": "t statistic", "ro": "Statistica t"},
    "ttest_df": {"en": "df", "ro": "gl"},
    "ttest_pvalue": {"en": "p-value", "ro": "valoarea p"},
    "ttest_significant": {"en": "Significant?", "ro": "Semnificativ?"},
    "ttest_yes": {"en": "✓ Yes", "ro": "✓ Da"},
    "ttest_no": {"en": "✗ No", "ro": "✗ Nu"},
    "ttest_paired_title": {
        "en": "Paired Samples t-Test",
        "ro": "Testul t pentru Eșantioane Pereche",
    },
    "ttest_paired_n": {"en": "N (pairs)", "ro": "N (perechi)"},
    "ttest_paired_mean_diff": {"en": "Mean difference", "ro": "Diferența mediilor"},
    "ttest_paired_std_diff": {
        "en": "Std of differences",
        "ro": "Dev. std a diferențelor",
    },
    "ttest_paired_t": {"en": "t-statistic", "ro": "Statistica t"},
    "ttest_paired_p": {"en": "p-value", "ro": "valoarea p"},
    "ttest_paired_ci": {"en": "95% CI", "ro": "IC 95%"},
    "ttest_paired_d": {"en": "Cohen's d", "ro": "d Cohen"},
    "ttest_paired_conclusion": {
        "en": "Conclusion",
        "ro": "Concluzie",
    },
    "ttest_paired_sig": {
        "en": "✓ Significant difference",
        "ro": "✓ Diferență semnificativă",
    },
    "ttest_paired_not_sig": {
        "en": "✗ No significant difference",
        "ro": "✗ Nicio diferență semnificativă",
    },
    "ttest_one_title": {"en": "One-Sample t-Tests", "ro": "Teste t pentru un Eșantion"},
    "ttest_one_h0": {"en": "H₀: μ =", "ro": "H₀: μ ="},
    "ttest_one_mean": {"en": "Sample Mean", "ro": "Media Eșantionului"},
    "ttest_one_t": {"en": "t-statistic", "ro": "Statistica t"},
    "ttest_one_p": {"en": "p-value", "ro": "valoarea p"},
    "ttest_one_ci": {"en": "95% CI Mean", "ro": "IC 95% Medie"},
    "ttest_one_d": {"en": "Cohen's d", "ro": "d Cohen"},
    "ttest_one_sig": {"en": "Significant?", "ro": "Semnificativ?"},

    # ── Levene ──
    "levene_equal": {
        "en": "Levene's test: F = {f:.4f}, p = {p} → Variances equal ✓ — use Student",
        "ro": "Testul Levene: F = {f:.4f}, p = {p} → Varianțe egale ✓ — folosește Student",
    },
    "levene_unequal": {
        "en": "Levene's test: F = {f:.4f}, p = {p} → Variances differ ✗ — use Welch",
        "ro": "Testul Levene: F = {f:.4f}, p = {p} → Varianțe diferite ✗ — folosește Welch",
    },

    # ── Normality ──
    "norm_title": {"en": "Normality Tests", "ro": "Teste de Normalitate"},
    "norm_col_test": {"en": "Test", "ro": "Test"},
    "norm_shapiro_w": {"en": "Shapiro-Wilk W", "ro": "Shapiro-Wilk W"},
    "norm_shapiro_p": {"en": "Shapiro-Wilk p", "ro": "Shapiro-Wilk p"},
    "norm_shapiro_normal": {"en": "Shapiro normal?", "ro": "Shapiro normal?"},
    "norm_dagostino_k2": {"en": "D'Agostino K²", "ro": "D'Agostino K²"},
    "norm_dagostino_p": {"en": "D'Agostino p", "ro": "D'Agostino p"},
    "norm_dagostino_normal": {
        "en": "D'Agostino normal?",
        "ro": "D'Agostino normal?",
    },
    "norm_yes": {"en": "✓ Yes", "ro": "✓ Da"},
    "norm_no": {"en": "✗ No", "ro": "✗ Nu"},
    "norm_na": {"en": "N/A", "ro": "N/A"},

    # ── Distribution comparison ──
    "dist_title": {"en": "Distribution Comparison", "ro": "Comparația Distribuțiilor"},
    "dist_ks_d": {"en": "Kolmogorov-Smirnov D", "ro": "Kolmogorov-Smirnov D"},
    "dist_ks_p": {"en": "KS p-value", "ro": "Valoarea p KS"},
    "dist_ks_conc": {"en": "KS conclusion", "ro": "Concluzia KS"},
    "dist_mw_u": {"en": "Mann-Whitney U", "ro": "Mann-Whitney U"},
    "dist_mw_p": {"en": "MW p-value", "ro": "Valoarea p MW"},
    "dist_mw_sig": {"en": "MW significant?", "ro": "MW semnificativ?"},
    "dist_rb_r": {"en": "Rank-biserial r", "ro": "Corelația rank-biserială"},

    # ── Charts ──
    "chart_hist_title": {
        "en": "Histograms with Density Curves",
        "ro": "Histograme cu Curbe de Densitate",
    },
    "chart_box_title": {"en": "Box Plots", "ro": "Diagrame Box Plot"},
    "chart_scatter_title": {
        "en": "Scatter Plot with Regression Line",
        "ro": "Grafic de Dispersie cu Linie de Regresie",
    },
    "chart_qq_title": {
        "en": "Q-Q Plots (Normality)",
        "ro": "Grafice Q-Q (Normalitate)",
    },
    "chart_resid_title": {
        "en": "Residuals vs Fitted",
        "ro": "Reziduuri vs Valori Ajustate",
    },
    "chart_hist_inner": {
        "en": "Histograms with Density Curves",
        "ro": "Histograme cu Curbe de Densitate",
    },
    "chart_box_inner": {"en": "Box Plots", "ro": "Diagrame Box Plot"},
    "chart_scatter_inner": {"en": "Scatter Plot", "ro": "Grafic de Dispersie"},
    "chart_qq_inner": {
        "en": "Q-Q Plot — {name}",
        "ro": "Grafic Q-Q — {name}",
    },
    "chart_resid_inner": {
        "en": "Residuals vs Fitted Values",
        "ro": "Reziduuri vs Valori Ajustate",
    },
    "chart_axis_value": {"en": "Value", "ro": "Valoare"},
    "chart_axis_density": {"en": "Density", "ro": "Densitate"},
    "chart_axis_theoretical": {"en": "Theoretical Quantiles", "ro": "Cuantile Teoretice"},
    "chart_axis_sample": {"en": "Sample Quantiles", "ro": "Cuantile Eșantion"},
    "chart_axis_theoretical_short": {"en": "Theoretical", "ro": "Teoretice"},
    "chart_axis_sample_short": {"en": "Sample", "ro": "Eșantion"},
    "chart_axis_fitted": {"en": "Fitted Values", "ro": "Valori Ajustate"},
    "chart_axis_residuals": {"en": "Residuals", "ro": "Reziduuri"},

    # ── Commentary / Interpretations ──
    "commentary_title": {"en": "📝 Interpretation", "ro": "📝 Interpretare"},

    # Descriptive commentary
    "comment_desc_intro": {
        "en": "Dataset 1 contains {n1} observations (M = {m1:.3f}, SD = {s1:.3f}) and Dataset 2 contains {n2} observations (M = {m2:.3f}, SD = {s2:.3f}).",
        "ro": "Setul 1 conține {n1} observații (M = {m1:.3f}, SD = {s1:.3f}) iar Setul 2 conține {n2} observații (M = {m2:.3f}, SD = {s2:.3f}).",
    },
    "comment_skew_sym": {
        "en": "Both datasets are approximately symmetric (skewness near 0).",
        "ro": "Ambele seturi sunt aproximativ simetrice (asimetria aproape de 0).",
    },
    "comment_skew_mild": {
        "en": "Mild skewness detected — the distribution may benefit from transformation for parametric tests.",
        "ro": "Asimetrie ușoară detectată — distribuția ar putea beneficia de transformare pentru testele parametrice.",
    },
    "comment_skew_strong": {
        "en": "Strong skewness detected — consider non-parametric alternatives or data transformation.",
        "ro": "Asimetrie puternică detectată — ia în considerare alternative non-parametrice sau transformarea datelor.",
    },
    "comment_kurt_meso": {
        "en": "Kurtosis near 0 indicates mesokurtic (normal-like) tails.",
        "ro": "Curtosis aproape de 0 indică cozi mezokurtice (asemănătoare normalei).",
    },
    "comment_kurt_heavy": {
        "en": "Positive kurtosis indicates heavier tails than normal — possible outliers.",
        "ro": "Curtosis pozitiv indică cozi mai groase decât normala — posibile valori aberante.",
    },
    "comment_kurt_light": {
        "en": "Negative kurtosis indicates lighter tails than normal — distribution is more concentrated around the mean.",
        "ro": "Curtosis negativ indică cozi mai subțiri decât normala — distribuția este mai concentrată în jurul mediei.",
    },

    # Correlation commentary
    "comment_corr_pearson": {
        "en": "Pearson r = {r:.3f} ({strength} {direction} correlation). The variables share {pct:.1f}% of their variance (r² = {r2:.3f}).",
        "ro": "Pearson r = {r:.3f} (corelație {strength} {direction}). Variabilele împart {pct:.1f}% din varianță (r² = {r2:.3f}).",
    },
    "comment_corr_significant": {
        "en": "The correlation is statistically significant (p = {p}), meaning the relationship is unlikely due to chance.",
        "ro": "Corelația este semnificativă statistic (p = {p}), ceea ce înseamnă că relația nu este probabil întâmplătoare.",
    },
    "comment_corr_not_significant": {
        "en": "The correlation is not statistically significant (p = {p}), so we cannot rule out chance as an explanation.",
        "ro": "Corelația nu este semnificativă statistic (p = {p}), deci nu putem exclude întâmplarea ca explicație.",
    },
    "comment_corr_spearman": {
        "en": "Spearman ρ = {rho:.3f} ({strength} {direction} rank correlation). This is a non-parametric alternative that uses ranks rather than raw values.",
        "ro": "Spearman ρ = {rho:.3f} (corelație de rang {strength} {direction}). Aceasta este o alternativă non-parametrică care folosește ranguri în loc de valorile brute.",
    },

    # Regression commentary
    "comment_reg_intro": {
        "en": "The model explains {pct:.1f}% of the variance in {y} (R² = {r2:.3f}).",
        "ro": "Modelul explică {pct:.1f}% din varianța variabilei {y} (R² = {r2:.3f}).",
    },
    "comment_reg_slope": {
        "en": "For each 1-unit increase in {x}, {y} changes by {slope:.4f} on average.",
        "ro": "Pentru fiecare creștere cu 1 unitate a variabilei {x}, {y} se modifică în medie cu {slope:.4f}.",
    },
    "comment_reg_sig": {
        "en": "The model is statistically significant — the slope is unlikely to be zero.",
        "ro": "Modelul este semnificativ statistic — panta nu este probabil zero.",
    },
    "comment_reg_not_sig": {
        "en": "The model is not statistically significant — the slope may be zero.",
        "ro": "Modelul nu este semnificativ statistic — panta ar putea fi zero.",
    },

    # t-Test commentary
    "comment_ttest_intro": {
        "en": "Mean difference: {diff:.4f} (95% CI: [{cil:.4f}, {ciu:.4f}]), Cohen's d = {d:.3f} ({d_strength} effect).",
        "ro": "Diferența mediilor: {diff:.4f} (IC 95%: [{cil:.4f}, {ciu:.4f}]), d Cohen = {d:.3f} (efect {d_strength}).",
    },
    "comment_ttest_which": {
        "en": "Levene's test indicates {var_status}. Use {which} t-test.",
        "ro": "Testul Levene indică {var_status}. Folosește testul t {which}.",
    },
    "comment_ttest_sig": {
        "en": "The difference between groups is statistically significant — the groups likely come from different populations.",
        "ro": "Diferența dintre grupuri este semnificativă statistic — grupurile provin probabil din populații diferite.",
    },
    "comment_ttest_not_sig": {
        "en": "The difference between groups is not statistically significant — we cannot reject the null hypothesis of equal means.",
        "ro": "Diferența dintre grupuri nu este semnificativă statistic — nu putem respinge ipoteza nulă a mediilor egale.",
    },
    "comment_ttest_paired": {
        "en": "The paired design accounts for within-subject variability. Mean paired difference: {diff:.4f} (Cohen's d = {d:.3f}).",
        "ro": "Designul pereche ține cont de variabilitatea intra-subiect. Diferența medie pereche: {diff:.4f} (d Cohen = {d:.3f}).",
    },

    # Normality commentary
    "comment_norm_both": {
        "en": "Both datasets appear normally distributed (Shapiro-Wilk p > 0.05). Parametric tests are appropriate.",
        "ro": "Ambele seturi par normal distribuite (Shapiro-Wilk p > 0.05). Testele parametrice sunt adecvate.",
    },
    "comment_norm_one": {
        "en": "One dataset deviates from normality. Consider non-parametric alternatives (Spearman ρ, Mann-Whitney U) for comparisons involving that dataset.",
        "ro": "Un set de date se abate de la normalitate. Ia în considerare alternative non-parametrice (Spearman ρ, Mann-Whitney U) pentru comparațiile care implică acel set.",
    },
    "comment_norm_neither": {
        "en": "Both datasets deviate from normality. Non-parametric tests (Spearman ρ, Mann-Whitney U) are recommended over parametric alternatives.",
        "ro": "Ambele seturi se abat de la normalitate. Testele non-parametrice (Spearman ρ, Mann-Whitney U) sunt recomandate în locul celor parametrice.",
    },
    "comment_norm_note": {
        "en": "H₀: Data are normally distributed. p < 0.05 → reject normality. If data are not normal, consider non-parametric tests (Spearman ρ, Mann-Whitney U).",
        "ro": "H₀: Datele sunt normal distribuite. p < 0.05 → respinge normalitatea. Dacă datele nu sunt normale, ia în considerare teste non-parametrice (Spearman ρ, Mann-Whitney U).",
    },

    # Distribution commentary
    "comment_dist_ks": {
        "en": "The Kolmogorov-Smirnov test {result} that the two datasets come from different distributions.",
        "ro": "Testul Kolmogorov-Smirnov {result} că cele două seturi provin din distribuții diferite.",
    },
    "comment_dist_ks_suggests": {
        "en": "suggests",
        "ro": "sugerează",
    },
    "comment_dist_ks_not": {
        "en": "does not suggest",
        "ro": "nu sugerează",
    },
    "comment_dist_mw": {
        "en": "The Mann-Whitney U test {result} a significant difference in medians/ranks. This is the non-parametric alternative to the independent t-test.",
        "ro": "Testul Mann-Whitney U {result} o diferență semnificativă a medianelor/rangurilor. Aceasta este alternativa non-parametrică la testul t independent.",
    },
    "comment_dist_mw_indicates": {
        "en": "indicates",
        "ro": "indică",
    },
    "comment_dist_mw_not": {
        "en": "does not indicate",
        "ro": "nu indică",
    },
    "comment_dist_ks_note": {
        "en": "Kolmogorov-Smirnov: H₀ = distributions are identical. Mann-Whitney U: non-parametric alternative to independent t-test.",
        "ro": "Kolmogorov-Smirnov: H₀ = distribuțiile sunt identice. Mann-Whitney U: alternativă non-parametrică la testul t independent.",
    },

    # ── Strength labels (used in commentary) ──
    "strength_negligible": {"en": "negligible", "ro": "neglijabilă"},
    "strength_small": {"en": "small", "ro": "mică"},
    "strength_medium": {"en": "medium", "ro": "medie"},
    "strength_large": {"en": "large", "ro": "mare"},
    "strength_very_large": {"en": "very large", "ro": "foarte mare"},
    "direction_positive": {"en": "positive", "ro": "pozitivă"},
    "direction_negative": {"en": "negative", "ro": "negativă"},
    "var_equal": {"en": "equal variances", "ro": "varianțe egale"},
    "var_unequal": {"en": "unequal variances", "ro": "varianțe inegale"},
    "hint_double_click": {
        "en": "double-click to detach",
        "ro": "dublu-click pentru detașare",
    },
}