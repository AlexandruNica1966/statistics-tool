"""
Statistical analysis engine for dual-dataset comparison.
Uses scipy, statsmodels, numpy for all computations.
"""

import numpy as np
from scipy import stats
from scipy.stats import (
    pearsonr, spearmanr, ttest_ind, ttest_rel, ttest_1samp,
    shapiro, kstest, mannwhitneyu, normaltest, levene
)
import statsmodels.api as sm
from typing import Dict, Any, Optional, Tuple
import warnings
warnings.filterwarnings('ignore')


def descriptive_stats(data: np.ndarray, name: str = "Dataset") -> Dict[str, Any]:
    """Compute full descriptive statistics for a dataset."""
    n = len(data)
    mean = float(np.mean(data))
    median = float(np.median(data))
    
    # Mode
    mode_result = stats.mode(data, keepdims=False)
    mode_val = float(mode_result.mode) if hasattr(mode_result, 'mode') else float(mode_result[0])
    
    std = float(np.std(data, ddof=1))  # sample std
    var = float(np.var(data, ddof=1))
    sem = std / np.sqrt(n)
    
    min_val = float(np.min(data))
    max_val = float(np.max(data))
    range_val = max_val - min_val
    
    q1 = float(np.percentile(data, 25))
    q3 = float(np.percentile(data, 75))
    iqr = q3 - q1
    
    skewness = float(stats.skew(data))
    kurtosis = float(stats.kurtosis(data, fisher=True))  # excess kurtosis
    
    # Confidence interval for mean (95%)
    ci = stats.t.interval(0.95, df=n-1, loc=mean, scale=sem)
    
    return {
        "name": name,
        "n": n,
        "mean": mean,
        "median": median,
        "mode": mode_val,
        "std": std,
        "variance": var,
        "sem": sem,
        "min": min_val,
        "max": max_val,
        "range": range_val,
        "q1": q1,
        "q3": q3,
        "iqr": iqr,
        "skewness": skewness,
        "kurtosis": kurtosis,
        "ci_95_lower": float(ci[0]),
        "ci_95_upper": float(ci[1]),
        "sum": float(np.sum(data)),
    }


def pearson_correlation(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Pearson r correlation with significance test."""
    r, p_value = pearsonr(x, y)
    r2 = r ** 2
    
    # Fisher z-transformation for CI
    n = len(x)
    z = np.arctanh(r)
    se = 1.0 / np.sqrt(n - 3)
    z_ci = stats.norm.ppf(0.975) * se
    ci_lower = np.tanh(z - z_ci)
    ci_upper = np.tanh(z + z_ci)
    
    # Effect size interpretation
    r_abs = abs(r)
    if r_abs < 0.1:
        strength = "negligible"
    elif r_abs < 0.3:
        strength = "small"
    elif r_abs < 0.5:
        strength = "medium"
    elif r_abs < 0.7:
        strength = "large"
    else:
        strength = "very large"
    
    significance = "significant" if p_value < 0.05 else "not significant"
    
    return {
        "r": float(r),
        "r2": float(r2),
        "p_value": float(p_value),
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "n": n,
        "strength": strength,
        "significance": significance,
        "significant": p_value < 0.05,
    }


def spearman_rho(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Spearman rank correlation ρ (rho) - population correlation."""
    rho, p_value = spearmanr(x, y)
    
    rho_abs = abs(rho)
    if rho_abs < 0.1:
        strength = "negligible"
    elif rho_abs < 0.3:
        strength = "small"
    elif rho_abs < 0.5:
        strength = "medium"
    elif rho_abs < 0.7:
        strength = "large"
    else:
        strength = "very large"
    
    return {
        "rho": float(rho),
        "p_value": float(p_value),
        "n": len(x),
        "strength": strength,
        "significance": "significant" if p_value < 0.05 else "not significant",
        "significant": p_value < 0.05,
    }


def linear_regression(x: np.ndarray, y: np.ndarray, x_name: str = "X", y_name: str = "Y") -> Dict[str, Any]:
    """Linear regression Y ~ X using statsmodels OLS."""
    x_with_const = sm.add_constant(x)
    model = sm.OLS(y, x_with_const).fit()
    
    predictions = model.predict(x_with_const)
    residuals = y - predictions
    
    return {
        "x_name": x_name,
        "y_name": y_name,
        "intercept": float(model.params[0]),
        "slope": float(model.params[1]),
        "r2": float(model.rsquared),
        "r2_adj": float(model.rsquared_adj),
        "f_statistic": float(model.fvalue),
        "f_pvalue": float(model.f_pvalue),
        "slope_se": float(model.bse[1]),
        "intercept_se": float(model.bse[0]),
        "slope_t": float(model.tvalues[1]),
        "intercept_t": float(model.tvalues[0]),
        "slope_p": float(model.pvalues[1]),
        "intercept_p": float(model.pvalues[0]),
        "slope_ci_lower": float(model.conf_int()[1, 0]),
        "slope_ci_upper": float(model.conf_int()[1, 1]),
        "intercept_ci_lower": float(model.conf_int()[0, 0]),
        "intercept_ci_upper": float(model.conf_int()[0, 1]),
        "n": len(x),
        "df_residual": int(model.df_resid),
        "mse": float(model.mse_resid),
        "equation": f"{y_name} = {model.params[0]:.4f} + {model.params[1]:.4f} * {x_name}",
        "predictions": predictions.tolist(),
        "residuals": residuals.tolist(),
        "significant": float(model.f_pvalue) < 0.05,
    }


def independent_t_tests(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Student's t-test (equal var) and Welch's t-test (unequal var)."""
    n1, n2 = len(x), len(y)
    mean_diff = float(np.mean(x) - np.mean(y))
    
    # Levene's test for equality of variances
    levene_stat, levene_p = levene(x, y)
    
    # Student's t-test (equal variance assumed)
    t_student, p_student = ttest_ind(x, y, equal_var=True)
    
    # Welch's t-test (unequal variance)
    t_welch, p_welch = ttest_ind(x, y, equal_var=False)
    
    # Cohen's d
    pooled_std = np.sqrt((np.var(x, ddof=1) + np.var(y, ddof=1)) / 2)
    cohens_d = mean_diff / pooled_std if pooled_std != 0 else 0.0
    
    d_abs = abs(cohens_d)
    if d_abs < 0.2:
        d_strength = "negligible"
    elif d_abs < 0.5:
        d_strength = "small"
    elif d_abs < 0.8:
        d_strength = "medium"
    else:
        d_strength = "large"
    
    # 95% CI for mean difference
    se_diff = np.sqrt(np.var(x, ddof=1)/n1 + np.var(y, ddof=1)/n2)
    df_correction = (np.var(x, ddof=1)/n1 + np.var(y, ddof=1)/n2)**2 / (
        (np.var(x, ddof=1)/n1)**2/(n1-1) + (np.var(y, ddof=1)/n2)**2/(n2-1)
    )
    t_crit = stats.t.ppf(0.975, df_correction)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff
    
    return {
        "n1": n1,
        "n2": n2,
        "mean1": float(np.mean(x)),
        "mean2": float(np.mean(y)),
        "std1": float(np.std(x, ddof=1)),
        "std2": float(np.std(y, ddof=1)),
        "mean_difference": mean_diff,
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "levene_statistic": float(levene_stat),
        "levene_pvalue": float(levene_p),
        "variances_equal": levene_p >= 0.05,
        "student_t": float(t_student),
        "student_pvalue": float(p_student),
        "student_df": n1 + n2 - 2,
        "student_significant": p_student < 0.05,
        "welch_t": float(t_welch),
        "welch_pvalue": float(p_welch),
        "welch_significant": p_welch < 0.05,
        "cohens_d": float(cohens_d),
        "cohens_d_strength": d_strength,
    }


def paired_t_test(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Paired samples t-test (requires equal length)."""
    if len(x) != len(y):
        # Truncate to shorter
        min_len = min(len(x), len(y))
        x = x[:min_len]
        y = y[:min_len]
    
    differences = x - y
    t_stat, p_value = ttest_rel(x, y)
    
    mean_diff = float(np.mean(differences))
    std_diff = float(np.std(differences, ddof=1))
    n = len(differences)
    
    # Cohen's d for paired
    cohens_d = mean_diff / std_diff if std_diff != 0 else 0.0
    
    d_abs = abs(cohens_d)
    if d_abs < 0.2:
        d_strength = "negligible"
    elif d_abs < 0.5:
        d_strength = "small"
    elif d_abs < 0.8:
        d_strength = "medium"
    else:
        d_strength = "large"
    
    # 95% CI for mean difference
    se_diff = std_diff / np.sqrt(n)
    t_crit = stats.t.ppf(0.975, n - 1)
    ci_lower = mean_diff - t_crit * se_diff
    ci_upper = mean_diff + t_crit * se_diff
    
    return {
        "n_pairs": n,
        "mean_difference": mean_diff,
        "std_difference": std_diff,
        "se_difference": se_diff,
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "df": n - 1,
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "cohens_d": float(cohens_d),
        "cohens_d_strength": d_strength,
        "significant": p_value < 0.05,
    }


def one_sample_t_test(data: np.ndarray, hypothesized_mean: float) -> Dict[str, Any]:
    """One-sample t-test against a hypothesized population mean."""
    t_stat, p_value = ttest_1samp(data, hypothesized_mean)
    
    mean_val = float(np.mean(data))
    std_val = float(np.std(data, ddof=1))
    n = len(data)
    sem = std_val / np.sqrt(n)
    
    # 95% CI
    t_crit = stats.t.ppf(0.975, n - 1)
    ci_lower = mean_val - t_crit * sem
    ci_upper = mean_val + t_crit * sem
    
    # Cohen's d for one-sample
    cohens_d = (mean_val - hypothesized_mean) / std_val if std_val != 0 else 0.0
    
    return {
        "n": n,
        "mean": mean_val,
        "std": std_val,
        "sem": sem,
        "hypothesized_mean": hypothesized_mean,
        "t_statistic": float(t_stat),
        "p_value": float(p_value),
        "df": n - 1,
        "ci_95_lower": float(ci_lower),
        "ci_95_upper": float(ci_upper),
        "cohens_d": float(cohens_d),
        "significant": p_value < 0.05,
    }


def normality_tests(data: np.ndarray) -> Dict[str, Any]:
    """Shapiro-Wilk and D'Agostino-Pearson normality tests."""
    # Shapiro-Wilk
    if len(data) >= 3 and len(data) <= 5000:
        shapiro_stat, shapiro_p = shapiro(data)
    else:
        shapiro_stat, shapiro_p = None, None
    
    # D'Agostino-Pearson omnibus test
    dagostino_stat, dagostino_p = normaltest(data)
    
    return {
        "shapiro_statistic": float(shapiro_stat) if shapiro_stat is not None else None,
        "shapiro_pvalue": float(shapiro_p) if shapiro_p is not None else None,
        "shapiro_normal": shapiro_p >= 0.05 if shapiro_p is not None else None,
        "dagostino_statistic": float(dagostino_stat),
        "dagostino_pvalue": float(dagostino_p),
        "dagostino_normal": dagostino_p >= 0.05,
        "n": len(data),
    }


def distribution_comparison(x: np.ndarray, y: np.ndarray) -> Dict[str, Any]:
    """Kolmogorov-Smirnov two-sample test + Mann-Whitney U test."""
    # KS test
    ks_stat, ks_p = kstest(x, y)
    
    # Mann-Whitney U (non-parametric)
    mw_stat, mw_p = mannwhitneyu(x, y, alternative='two-sided')
    
    # Effect size for Mann-Whitney: rank-biserial correlation
    n1, n2 = len(x), len(y)
    rank_biserial = 1 - (2 * mw_stat) / (n1 * n2)
    
    return {
        "ks_statistic": float(ks_stat),
        "ks_pvalue": float(ks_p),
        "ks_significant": ks_p < 0.05,
        "ks_conclusion": "Distributions differ significantly" if ks_p < 0.05 else "Distributions do not differ significantly",
        "mannwhitney_u": float(mw_stat),
        "mannwhitney_pvalue": float(mw_p),
        "mannwhitney_significant": mw_p < 0.05,
        "rank_biserial_correlation": float(rank_biserial),
    }


def run_all_analyses(data1: np.ndarray, data2: np.ndarray,
                     name1: str = "Dataset 1", name2: str = "Dataset 2",
                     hypothesized_mean1: float = 0.0,
                     hypothesized_mean2: float = 0.0) -> Dict[str, Any]:
    """Run all statistical analyses for two datasets."""
    
    # Ensure data are 1D float arrays, drop NaN
    d1 = data1[~np.isnan(data1)].astype(float)
    d2 = data2[~np.isnan(data2)].astype(float)
    
    if len(d1) < 2 or len(d2) < 2:
        return {"error": "Each dataset must have at least 2 valid numeric values."}
    
    n = min(len(d1), len(d2))
    
    results = {}
    
    # 1. Descriptive statistics
    results["descriptive1"] = descriptive_stats(d1, name1)
    results["descriptive2"] = descriptive_stats(d2, name2)
    
    # 2. Pearson correlation (on paired observations — use first n of each)
    results["pearson"] = pearson_correlation(d1[:n], d2[:n])
    
    # 3. Spearman rank correlation ρ
    results["spearman"] = spearman_rho(d1[:n], d2[:n])
    
    # 4. Linear regressions (both directions)
    results["regression_1on2"] = linear_regression(d2[:n], d1[:n], x_name=name2, y_name=name1)
    results["regression_2on1"] = linear_regression(d1[:n], d2[:n], x_name=name1, y_name=name2)
    
    # 5. Independent t-tests (Student + Welch)
    results["independent_ttest"] = independent_t_tests(d1, d2)
    
    # 6. Paired t-test
    results["paired_ttest"] = paired_t_test(d1, d2)
    
    # 7. One-sample t-tests
    results["onesample_ttest1"] = one_sample_t_test(d1, hypothesized_mean1)
    results["onesample_ttest2"] = one_sample_t_test(d2, hypothesized_mean2)
    
    # 8. Normality tests
    results["normality1"] = normality_tests(d1)
    results["normality2"] = normality_tests(d2)
    
    # 9. Distribution comparison
    results["distribution_comparison"] = distribution_comparison(d1, d2)
    
    return results
