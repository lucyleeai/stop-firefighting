#!/usr/bin/env python3
"""Development-only: check stats_tools.py against SciPy / statsmodels.

Not part of the plugin (the plugin stays stdlib-only). Run in an environment
with scipy, numpy and statsmodels:

    python dev/verify_against_scipy.py

Exits non-zero on the first mismatch beyond tolerance.
"""
import math
import os
import random
import sys

import numpy as np
from scipy import stats
from statsmodels.stats.proportion import confint_proportions_2indep, proportion_confint

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "problem-solving", "skills", "problem-solving", "scripts"))
import stats_tools as st  # noqa: E402

rng = random.Random(20260924)
checks = 0


def same(a, b, tol, what):
    global checks
    checks += 1
    if not (abs(a - b) <= tol or (math.isnan(a) and math.isnan(b))):
        sys.exit(f"MISMATCH {what}: ours {a} vs reference {b}")


# distributions, including extreme quantiles
for df in (1, 2, 3, 5, 10, 30, 100, 1000):
    for q in (0.6, 0.9, 0.975, 0.995, 0.9999):
        same(st.t_ppf(q, df), stats.t.ppf(q, df), 1e-6 * max(1, stats.t.ppf(q, df)), f"t_ppf({q},{df})")
    for t in (0.1, 1, 2.5, 10, 50):
        same(st.t_sf2(t, df), 2 * stats.t.sf(t, df), 1e-9, f"t_sf2({t},{df})")
for df in (1, 2, 4, 10, 50, 200):
    for x in (0.01, 1, 5, 20, 100, 400):
        same(st.chi2_sf(x, df), stats.chi2.sf(x, df), 1e-9, f"chi2_sf({x},{df})")
for d1, d2 in ((1, 1), (1, 10), (3, 20), (10, 100), (50, 5)):
    for f in (0.1, 1, 3, 10, 100):
        same(st.f_sf(f, d1, d2), stats.f.sf(f, d1, d2), 1e-9, f"f_sf({f},{d1},{d2})")

for _ in range(300):
    n1, n2 = rng.randint(2, 40), rng.randint(2, 40)
    a = [round(rng.lognormvariate(1, 0.8), 2) for _ in range(n1)]
    b = [round(rng.lognormvariate(1.2, 0.8), 2) for _ in range(n2)]
    if len(set(a)) > 1 and len(set(b)) > 1:
        ours = st.ttest(a, b)
        ref = stats.ttest_ind(a, b, equal_var=False)
        same(ours["p_two_sided"], ref.pvalue, 1e-4, "welch p")
        ci = ref.confidence_interval()
        same(ours["ci_95"][0], ci.low, 1e-3, "welch ci low")
        o1 = st.ttest(a, mu=3.0)
        same(o1["p_two_sided"], stats.ttest_1samp(a, 3.0).pvalue, 1e-4, "one-sample p")
    m = min(n1, n2)
    if len(set(x - y for x, y in zip(a[:m], b[:m]))) > 1:
        same(st.ttest(a[:m], b[:m], paired=True)["p_two_sided"], stats.ttest_rel(a[:m], b[:m]).pvalue, 1e-4, "paired p")
    # rank tests (asymptotic, continuity-corrected, tie-corrected)
    mw = st.mann_whitney(a, b)
    ref = stats.mannwhitneyu(a, b, alternative="two-sided", use_continuity=True, method="asymptotic")
    same(mw["U"], ref.statistic, 1e-6, "MW U")
    same(mw["p_two_sided"], ref.pvalue, 1e-4, "MW p")
    ai = [round(v) for v in a[:m]]
    bi = [round(v) for v in b[:m]]
    if sum(1 for x, y in zip(ai, bi) if x != y) >= 2:
        ws = st.wilcoxon_signed(ai, bi)
        ref = stats.wilcoxon(ai, bi, zero_method="wilcox", correction=True, method="approx")
        same(ws["p_two_sided"], ref.pvalue, 1e-4, "Wilcoxon p")
    # proportions
    N1, N2 = rng.randint(5, 3000), rng.randint(5, 3000)
    x1, x2 = rng.randint(0, N1), rng.randint(0, N2)
    same(st.fisher_2x2(x1, N1 - x1, x2, N2 - x2) if N1 + N2 < 800 else 0,
         stats.fisher_exact([[x1, N1 - x1], [x2, N2 - x2]]).pvalue if N1 + N2 < 800 else 0, 1e-6, "Fisher p")
    lo, hi = st.newcombe(x1, N1, x2, N2)
    rl, rh = confint_proportions_2indep(x1, N1, x2, N2, method="newcomb", compare="diff")
    same(lo, rl, 1e-6, "Newcombe low"); same(hi, rh, 1e-6, "Newcombe high")
    wl, wh = st.wilson(x1, N1)
    sl, sh = proportion_confint(x1, N1, method="wilson")
    same(wl, sl, 1e-6, "Wilson low")
    # chi-square and ANOVA
    nc = rng.randint(2, 4)
    tab = [[rng.randint(1, 60) for _ in range(nc)] for _ in range(rng.randint(2, 4))]
    cq = st.chisq(tab, [str(i) for i in range(len(tab))], [str(j) for j in range(len(tab[0]))])
    ref = stats.chi2_contingency(tab, correction=False)
    same(cq["chi2"], ref.statistic, 1e-3, "chi2 stat"); same(cq["p"], ref.pvalue, 1e-4, "chi2 p")
    g = {k: [rng.gauss(10 + i, 2) for _ in range(rng.randint(3, 15))] for i, k in enumerate("ABC")}
    av = st.anova(g)
    ref = stats.f_oneway(*g.values())
    same(av["F"], ref.statistic, 1e-3, "ANOVA F"); same(av["p"], ref.pvalue, 1e-4, "ANOVA p")

# correlation and regression
for _ in range(300):
    n = rng.randint(5, 60)
    xs = [rng.uniform(0, 100) for _ in range(n)]
    ys = [3 + 0.5 * v + rng.gauss(0, rng.choice([1, 10, 40])) for v in xs]
    rg = st.regress(xs, ys)
    lr = stats.linregress(xs, ys)
    same(rg["slope"], lr.slope, 1e-3 * max(1, abs(lr.slope)), "slope")
    same(rg["intercept"], lr.intercept, 1e-3 * max(1, abs(lr.intercept)), "intercept")
    same(rg["pearson_r"], lr.rvalue, 1e-4, "pearson r")
    same(rg["p_two_sided"], lr.pvalue, 1e-4, "regression p")
    ci = stats.pearsonr(xs, ys).confidence_interval()
    same(rg["ci_95_r"][0], ci.low, 1e-3, "r ci low"); same(rg["ci_95_r"][1], ci.high, 1e-3, "r ci high")
    same(rg["spearman_rho"], stats.spearmanr(xs, ys).statistic, 1e-4, "spearman")
    tq = stats.t.ppf(0.975, n - 2)
    same(rg["ci_95_slope"][0], lr.slope - tq * lr.stderr, 1e-3 * max(1, abs(lr.slope)), "slope ci")

# capability against direct numpy formulas (stable synthetic processes)
for _ in range(200):
    n = rng.randint(20, 80)
    xs = [rng.gauss(50, 2) for _ in range(n)]
    lsl, usl = 50 - rng.uniform(4, 12), 50 + rng.uniform(4, 12)
    try:
        cap = st.capability(xs, lsl, usl)
    except st.InputError:
        continue  # an unstable-looking sample is refused, by design
    arr = np.array(xs)
    sw = np.mean(np.abs(np.diff(arr))) / 1.128
    so = np.std(arr, ddof=1)
    mu = arr.mean()
    same(cap["Cp"], (usl - lsl) / (6 * sw), 1e-3, "Cp")
    same(cap["Cpk"], min(usl - mu, mu - lsl) / (3 * sw), 1e-3, "Cpk")
    same(cap["Ppk"], min(usl - mu, mu - lsl) / (3 * so), 1e-3, "Ppk")

# control-chart constants against first principles
d2 = 2 / math.sqrt(math.pi)  # expected range of 2 normal values in sd units = 1.128
same(1.128, d2, 5e-4, "d2 constant")
print(f"all {checks} checks passed")
