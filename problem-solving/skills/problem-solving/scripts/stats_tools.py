#!/usr/bin/env python3
"""Statistics for the problem-solving skill. Stdlib only — no numpy/scipy.

Every test statistic, p-value, interval, control limit and sample size the skill
reports comes from here, never from the model's own arithmetic.

  pareto    counts (or a weight such as cost) by category, sorted, with cumulative share
  ranks     rank-based comparison: Mann-Whitney (two independent groups) or,
            with --paired, Wilcoxon signed-rank (same items before/after)
  ttest     one-sample, two-sample (Welch) or paired t-test on measured data
  prop      one-proportion or two-proportion comparison (+ Fisher exact for 2x2)
  chisq     chi-square test of association on a table of counts
  anova     one-way ANOVA on measured data in groups
  chart     control chart: imr (individual values), p (defectives/sample), u (defects/unit);
            --rules picks any of Nelson rules 1-8 (default 1,2)
  capability  process capability against a requirement (refuses an unstable process)
  regress   correlation (Pearson with interval, Spearman) and a least-squares line
  plot      histogram, box plot (by group) or scatter plot, written as SVG
  normality D'Agostino-Pearson test (use with a plot, before choosing a t-test)
  matrix    weighted decision matrix, with a check whether the winner survives weight changes
  agree     do raters agree? Cohen's / Fleiss' kappa, % agreement, and accuracy vs a reference rater
  grr       gauge study for measured values (repeatability, reproducibility, % of study variation)
  doe       two-level full factorial: design a randomised run sheet, or analyse the results
  size      sample size: estimate a mean or proportion, or detect a difference in proportions
  selftest  run the built-in checks

Every output is JSON with "status": "ok" or "error". On error nothing else is
reported — the skill must say the analysis could not be run, never guess.
Decisions in `plain` are made on unrounded values; numbers are rounded for display only.
"""
import argparse
import csv
import html
import json
import math
import statistics
import sys
from statistics import NormalDist

Z = NormalDist()


class InputError(Exception):
    pass


def fail(msg):
    raise InputError(msg)


# ---------- special functions ----------

def _betacf(a, b, x):
    tiny, eps = 1e-300, 3e-16
    qab, qap, qam = a + b, a + 1, a - 1
    c, d = 1.0, 1 - qab * x / qap
    d = 1 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 1000):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c; c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1 + aa * d; d = 1 / (d if abs(d) > tiny else tiny)
        c = 1 + aa / c; c = c if abs(c) > tiny else tiny
        delta = d * c
        h *= delta
        if abs(delta - 1) < eps:
            return h
    raise ArithmeticError("incomplete beta did not converge")


def betainc(a, b, x):
    if x <= 0:
        return 0.0
    if x >= 1:
        return 1.0
    lbt = math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1 - x)
    if x < (a + 1) / (a + b + 2):
        return math.exp(lbt) * _betacf(a, b, x) / a
    return 1 - math.exp(lbt) * _betacf(b, a, 1 - x) / b


def gammainc_upper(s, x):
    if x <= 0:
        return 1.0
    if x < s + 1:
        term = total = 1.0 / s
        n = s
        for _ in range(5000):
            n += 1
            term *= x / n
            total += term
            if abs(term) < abs(total) * 1e-16:
                return 1 - total * math.exp(-x + s * math.log(x) - math.lgamma(s))
        raise ArithmeticError("incomplete gamma series did not converge")
    tiny = 1e-300
    b = x + 1 - s
    c, d = 1 / tiny, 1 / b
    h = d
    for i in range(1, 5000):
        an = -i * (i - s)
        b += 2
        d = an * d + b; d = tiny if abs(d) < tiny else d
        c = b + an / c; c = tiny if abs(c) < tiny else c
        d = 1 / d
        h *= d * c
        if abs(d * c - 1) < 1e-16:
            return math.exp(-x + s * math.log(x) - math.lgamma(s)) * h
    raise ArithmeticError("incomplete gamma fraction did not converge")


def t_sf2(t, df):
    """Two-sided p-value for a t statistic."""
    return betainc(df / 2, 0.5, df / (df + t * t))


def t_ppf(q, df):
    """Quantile of the t distribution for q in (0.5, 1): bracket, then bisect."""
    if not 0.5 < q < 1:
        fail("t quantile needs 0.5 < q < 1")
    hi = 1.0
    while 1 - t_sf2(hi, df) / 2 < q:
        hi *= 2
        if hi > 1e12:
            raise ArithmeticError("t quantile out of range")
    lo = hi / 2 if hi > 1 else 0.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if 1 - t_sf2(mid, df) / 2 < q:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def chi2_sf(x, df):
    return gammainc_upper(df / 2, x / 2)


def f_sf(f, d1, d2):
    return betainc(d2 / 2, d1 / 2, d2 / (d2 + d1 * f))


# ---------- validation ----------

def finite(values, what):
    out = []
    for v in values:
        try:
            x = float(v)
        except (TypeError, ValueError):
            fail(f"{what}: '{v}' is not a number")
        if not math.isfinite(x):
            fail(f"{what}: non-finite value '{v}'")
        out.append(x)
    return out


def count(v, what):
    try:
        x = float(v)
    except (TypeError, ValueError):
        fail(f"{what}: '{v}' is not a count")
    if not math.isfinite(x) or x < 0 or x != int(x):
        fail(f"{what}: '{v}' must be a whole number ≥ 0")
    return int(x)


def need(n, k, what):
    if n < k:
        fail(f"{what}: need at least {k} values, got {n}")


def r(v, k=4):
    return None if v is None else round(v, k)


def skewness(x):
    n, m = len(x), statistics.mean(x)
    s = statistics.pstdev(x)
    return 0.0 if s == 0 or n < 3 else sum((v - m) ** 3 for v in x) / n / s ** 3


# ---------- tests ----------

def ttest(a, b=None, mu=None, paired=False, alpha=0.05):
    """a, b are already filtered (paired: jointly by row, same items in the same order)."""
    level = int(round((1 - alpha) * 100))
    if paired:
        if b is None or len(a) != len(b):
            fail("paired t-test needs two columns with a value for every kept row")
        sample, target, kind = [x - y for x, y in zip(a, b)], 0.0, "paired"
        need(len(sample), 2, "paired t-test")
    elif b is None:
        sample, target, kind = a, (mu or 0.0), "one-sample"
        need(len(sample), 2, "one-sample t-test")
    else:
        need(len(a), 2, "group A"); need(len(b), 2, "group B")
        kind = "two-sample (Welch)"
    if kind != "two-sample (Welch)":
        n, s = len(sample), statistics.stdev(sample)
        if s == 0:
            fail("all values are identical: no variation to test")
        se, df = s / math.sqrt(n), n - 1
        diff = statistics.mean(sample) - target
        groups = [sample]
    else:
        n1, n2 = len(a), len(b)
        v1, v2 = statistics.variance(a) / n1, statistics.variance(b) / n2
        if v1 + v2 == 0:
            fail("all values are identical: no variation to test")
        se = math.sqrt(v1 + v2)
        df = (v1 + v2) ** 2 / (v1 ** 2 / (n1 - 1) + v2 ** 2 / (n2 - 1))
        diff = statistics.mean(a) - statistics.mean(b)
        groups = [a, b]
    t = diff / se
    p = t_sf2(t, df)
    q = t_ppf(1 - alpha / 2, df)
    lo, hi = diff - q * se, diff + q * se
    excl = lo > 0 or hi < 0
    out = {"status": "ok", "test": kind + " t-test", "estimand": "difference in means",
           "n": [len(g) for g in groups] if len(groups) > 1 else len(groups[0]),
           "mean": [r(statistics.mean(g)) for g in groups] if len(groups) > 1 else r(statistics.mean(groups[0])),
           "difference": r(diff), "t": r(t), "df": r(df, 2), "p_two_sided": r(p), f"ci_{level}": [r(lo), r(hi)],
           "plain": (f"Difference in means {r(diff, 3)} ({level}% interval {r(lo, 3)} to {r(hi, 3)}). "
                     + ("The interval excludes 0: chance alone is an unlikely explanation."
                        if excl else "The interval includes 0: the data cannot rule out no difference."))}
    sk = [skewness(g) for g in groups]
    out["skewness"] = [r(v, 2) for v in sk]
    if any(abs(v) > 1 for v in sk) and min(len(g) for g in groups) < 30:
        out["note"] = ("Skewed and small: the t interval may be off. If the question is about the typical value, "
                       "`ranks` answers that (use `ranks --paired` for before/after on the same items); if it is about "
                       "the average or total (e.g. total cost), the mean is still the right target — call it approximate.")
    return out


def pareto(counts):
    if not counts:
        fail("no categories")
    total = sum(counts.values())
    if total <= 0:
        fail("total is zero")
    cum, rows, top = 0.0, [], None
    for i, (k, v) in enumerate(sorted(counts.items(), key=lambda kv: -kv[1])):
        cum += v
        if top is None and cum / total >= 0.8 - 1e-12:
            top = i + 1
        rows.append({"category": k, "value": r(v, 2), "share_pct": r(100 * v / total, 1),
                     "cumulative_pct": r(100 * cum / total, 1)})
    return {"status": "ok", "total": r(total, 2), "rows": rows, "categories_to_80_pct": top,
            "plain": f"{top} of {len(rows)} categories account for at least 80% of the total "
                     f"({', '.join(rw['category'] for rw in rows[:top])})."}


def _ranks(values):
    order = sorted(range(len(values)), key=lambda i: values[i])
    ranks, ties, i = [0.0] * len(values), 0.0, 0
    while i < len(order):
        j = i
        while j + 1 < len(order) and values[order[j + 1]] == values[order[i]]:
            j += 1
        for k in range(i, j + 1):
            ranks[order[k]] = (i + j) / 2 + 1
        t = j - i + 1
        ties += t ** 3 - t
        i = j + 1
    return ranks, ties


def mann_whitney(a, b):
    need(len(a), 2, "group A"); need(len(b), 2, "group B")
    n1, n2 = len(a), len(b)
    ranks, ties = _ranks(a + b)
    u1 = sum(ranks[:n1]) - n1 * (n1 + 1) / 2
    n = n1 + n2
    mu = n1 * n2 / 2
    sigma = math.sqrt(max(0.0, n1 * n2 / 12 * ((n + 1) - ties / (n * (n - 1)))))
    z = 0.0 if sigma == 0 or u1 == mu else (u1 - mu - math.copysign(0.5, u1 - mu)) / sigma
    pv = 2 * (1 - Z.cdf(abs(z)))
    gt = sum(1 for x in a for y in b if x > y) / (n1 * n2)
    eq = sum(1 for x in a for y in b if x == y) / (n1 * n2)
    out = {"status": "ok", "test": "Mann-Whitney rank-sum (independent groups, normal approx.)",
           "estimand": "whether values in A tend to be larger than in B — not a difference in means",
           "n": [n1, n2], "median": [r(statistics.median(a)), r(statistics.median(b))], "U": r(u1, 1), "z": r(z),
           "p_two_sided": r(pv), "share_pairs_a_greater": r(gt, 3), "share_pairs_tied": r(eq, 3),
           "pairs_compared": n1 * n2,
           "interval": "not computed",
           "plain": (f"Medians {r(statistics.median(a), 3)} vs {r(statistics.median(b), 3)}. In {r(gt * 100, 1)}% of "
                     f"all {n1 * n2} combinations of one A value with one B value, the A value is larger "
                     f"({r(eq * 100, 1)}% tied) — every A compared with every B, not A and B matched one-to-one. "
                     + ("A consistent difference." if pv < 0.05 else "Not a consistent difference on this data."))}
    if min(n1, n2) < 8:
        out["warning"] = "Fewer than 8 in a group: the normal approximation is rough."
    return out


def wilcoxon_signed(a, b):
    """Paired rank test on differences (zeros dropped); normal approx. with tie and continuity correction."""
    d = [x - y for x, y in zip(a, b) if x != y]
    need(len(d), 2, "non-zero paired differences")
    ranks, ties = _ranks([abs(v) for v in d])
    wplus = sum(rk for rk, v in zip(ranks, d) if v > 0)
    n = len(d)
    mu = n * (n + 1) / 4
    sigma = math.sqrt(max(0.0, n * (n + 1) * (2 * n + 1) / 24 - ties / 48))
    z = 0.0 if sigma == 0 or wplus == mu else (wplus - mu - math.copysign(0.5, wplus - mu)) / sigma
    pv = 2 * (1 - Z.cdf(abs(z)))
    med = statistics.median([x - y for x, y in zip(a, b)])
    out = {"status": "ok", "test": "Wilcoxon signed-rank (paired, normal approx.)",
           "estimand": "whether paired differences tend to be positive or negative",
           "pairs": len(a), "zero_differences_dropped": len(a) - n, "median_difference": r(med),
           "W_plus": r(wplus, 1), "z": r(z), "p_two_sided": r(pv), "interval": "not computed",
           "plain": f"Median paired difference {r(med, 3)}. "
                    + ("A consistent shift." if pv < 0.05 else "Not a consistent shift on this data.")}
    if n < 10:
        out["warning"] = "Fewer than 10 non-zero differences: the normal approximation is rough."
    return out


def fisher_2x2(a, b, c, d):
    r1, c1, n = a + b, a + c, a + b + c + d

    def lpmf(x):
        return (math.lgamma(r1 + 1) + math.lgamma(n - r1 + 1) + math.lgamma(c1 + 1) + math.lgamma(n - c1 + 1)
                - math.lgamma(n + 1) - math.lgamma(x + 1) - math.lgamma(r1 - x + 1)
                - math.lgamma(c1 - x + 1) - math.lgamma(n - r1 - c1 + x + 1))
    lo, hi = max(0, r1 + c1 - n), min(r1, c1)
    l0 = lpmf(a)
    return min(1.0, sum(math.exp(lpmf(x)) for x in range(lo, hi + 1) if lpmf(x) <= l0 + 1e-7))


def wilson(x, n, z=1.959964):
    p = x / n
    den = 1 + z * z / n
    centre = (p + z * z / (2 * n)) / den
    half = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return centre - half, centre + half


def newcombe(x1, n1, x2, n2):
    """Newcombe (1998) hybrid score interval for p1 - p2, built from Wilson intervals."""
    p1, p2 = x1 / n1, x2 / n2
    l1, u1 = wilson(x1, n1)
    l2, u2 = wilson(x2, n2)
    d = p1 - p2
    return d - math.sqrt((p1 - l1) ** 2 + (u2 - p2) ** 2), d + math.sqrt((u1 - p1) ** 2 + (p2 - l2) ** 2)


def prop_test(x1, n1, x2=None, n2=None, p0=None):
    x1, n1 = count(x1, "x1"), count(n1, "n1")
    if n1 == 0 or x1 > n1:
        fail("need 0 ≤ x1 ≤ n1 and n1 > 0")
    if x2 is None:
        if p0 is None or not 0 < p0 < 1:
            fail("one-proportion test needs 0 < p0 < 1")
        p = x1 / n1
        z = (p - p0) / math.sqrt(p0 * (1 - p0) / n1)
        pv = 2 * (1 - Z.cdf(abs(z)))
        lo, hi = wilson(x1, n1)
        out = {"status": "ok", "test": "one-proportion z-test", "p_hat": r(p), "p0": p0, "z": r(z), "p_two_sided": r(pv),
               "ci_95_wilson": [r(lo), r(hi)],
               "plain": f"Observed {r(p * 100, 2)}% (95% interval {r(lo * 100, 2)}% to {r(hi * 100, 2)}%) against {p0 * 100}%."}
        if n1 * p0 < 5 or n1 * (1 - p0) < 5:
            out["warning"] = "Expected counts below 5: the z-test is unreliable; rely on the Wilson interval."
        return out
    x2, n2 = count(x2, "x2"), count(n2, "n2")
    if n2 == 0 or x2 > n2:
        fail("need 0 ≤ x2 ≤ n2 and n2 > 0")
    p1, p2 = x1 / n1, x2 / n2
    pp = (x1 + x2) / (n1 + n2)
    se0 = math.sqrt(pp * (1 - pp) * (1 / n1 + 1 / n2))
    z = (p1 - p2) / se0 if se0 else 0.0
    pz = 2 * (1 - Z.cdf(abs(z))) if se0 else 1.0
    pf = fisher_2x2(x1, n1 - x1, x2, n2 - x2)
    lo, hi = newcombe(x1, n1, x2, n2)
    sparse = min(x1, x2, n1 - x1, n2 - x2) < 5
    decide_p = pf if sparse else pz
    out = {"status": "ok", "test": "two-proportion comparison", "p1": r(p1), "p2": r(p2), "difference": r(p1 - p2),
           "ci_95_difference_newcombe": [r(lo), r(hi)], "z": r(z), "p_two_sided_z": r(pz), "fisher_exact_p": r(pf),
           "decision_based_on": "fisher_exact_p" if sparse else "p_two_sided_z", "n": [n1, n2]}
    if x1 == x2 == 0 or (x1 == n1 and x2 == n2):
        out["warning"] = "No events (or all events) in both groups: the data say little about a difference yet."
    elif sparse:
        out["warning"] = "Some counts below 5: the conclusion uses Fisher's exact test, not the z-test."
    out["plain"] = (f"{r(p1 * 100, 2)}% vs {r(p2 * 100, 2)}%, difference {r((p1 - p2) * 100, 2)} points "
                    f"(95% interval {r(lo * 100, 2)} to {r(hi * 100, 2)}). "
                    + ("The difference is unlikely to be chance alone." if decide_p < 0.05
                       else "The data cannot rule out no difference."))
    return out


def chisq(table, row_labels, col_labels):
    table = [[count(v, "table cell") for v in rw] for rw in table]
    keep_r = [i for i, rw in enumerate(table) if sum(rw) > 0]
    keep_c = [j for j in range(len(table[0])) if sum(rw[j] for rw in table) > 0]
    dropped = {"rows": [row_labels[i] for i in range(len(table)) if i not in keep_r],
               "columns": [col_labels[j] for j in range(len(table[0])) if j not in keep_c]}
    t = [[table[i][j] for j in keep_c] for i in keep_r]
    if len(t) < 2 or len(keep_c) < 2:
        fail("need at least 2 non-empty rows and 2 non-empty columns")
    rows, cols = len(t), len(keep_c)
    rt = [sum(rw) for rw in t]
    ct = [sum(t[i][j] for i in range(rows)) for j in range(cols)]
    n = sum(rt)
    exp = [[rt[i] * ct[j] / n for j in range(cols)] for i in range(rows)]
    x2 = sum((t[i][j] - exp[i][j]) ** 2 / exp[i][j] for i in range(rows) for j in range(cols))
    df = (rows - 1) * (cols - 1)
    p = chi2_sf(x2, df)
    out = {"status": "ok", "test": "chi-square test of association", "chi2": r(x2), "df": df, "p": r(p), "n": n,
           "expected": [[r(v, 2) for v in rw] for rw in exp], "dropped_empty": dropped,
           "plain": ("The pattern of counts differs between groups more than chance would usually produce."
                     if p < 0.05 else "The counts are consistent with no association between the two classifications.")}
    small = sum(1 for rw in exp for v in rw if v < 5)
    if small:
        out["warning"] = f"{small} expected counts below 5: unreliable; combine categories or collect more data."
    return out


def anova(groups):
    names = [g for g in groups if groups[g]]
    if len(names) < 2:
        fail("need at least 2 groups")
    for g in names:
        need(len(groups[g]), 2, f"group {g}")
    allv = [v for g in names for v in groups[g]]
    grand = statistics.mean(allv)
    ssb = sum(len(groups[g]) * (statistics.mean(groups[g]) - grand) ** 2 for g in names)
    ssw = sum((v - statistics.mean(groups[g])) ** 2 for g in names for v in groups[g])
    if ssw == 0:
        fail("no variation within groups")
    d1, d2 = len(names) - 1, len(allv) - len(names)
    f = (ssb / d1) / (ssw / d2)
    p = f_sf(f, d1, d2)
    return {"status": "ok", "test": "one-way ANOVA",
            "groups": {g: {"n": len(groups[g]), "mean": r(statistics.mean(groups[g])),
                           "sd": r(statistics.stdev(groups[g]))} for g in names},
            "F": r(f), "df": [d1, d2], "p": r(p),
            "note": "Assumes independent observations and similar spread per group; says only that some mean "
                    "differs, not which.",
            "plain": ("At least one group mean differs." if p < 0.05 else "The data are consistent with equal group means.")}


# ---------- control charts ----------

def run_rules(values, centre, sigma, rules):
    """Nelson rules 1-8; each hit is reported at the point that completes the pattern."""
    hits, n = {}, len(values)
    if 1 in rules:
        hits["1_beyond_3_sigma"] = [i for i, v in enumerate(values) if sigma[i] and abs(v - centre[i]) > 3 * sigma[i]]
    if 2 in rules:
        side = [0 if v == c else (1 if v > c else -1) for v, c in zip(values, centre)]
        hits["2_nine_same_side"] = [i for i in range(8, n) if abs(sum(side[i - 8:i + 1])) == 9]
    if 3 in rules:
        hits["3_six_trending"] = [i for i in range(5, n)
                                  if all(values[k] < values[k + 1] for k in range(i - 5, i))
                                  or all(values[k] > values[k + 1] for k in range(i - 5, i))]
    if 4 in rules:
        idx = []
        for i in range(13, n):
            dd = [values[k + 1] - values[k] for k in range(i - 13, i)]
            if all(dd[k] * dd[k + 1] < 0 for k in range(12)):
                idx.append(i)
        hits["4_fourteen_alternating"] = idx
    z = [((v - c) / sg) if sg else 0.0 for v, c, sg in zip(values, centre, sigma)]
    if 5 in rules:
        hits["5_two_of_three_beyond_2_sigma"] = [
            i for i in range(2, n)
            if sum(1 for k in range(i - 2, i + 1) if z[k] > 2) >= 2 and z[i] > 2
            or sum(1 for k in range(i - 2, i + 1) if z[k] < -2) >= 2 and z[i] < -2]
    if 6 in rules:
        hits["6_four_of_five_beyond_1_sigma"] = [
            i for i in range(4, n)
            if sum(1 for k in range(i - 4, i + 1) if z[k] > 1) >= 4 and z[i] > 1
            or sum(1 for k in range(i - 4, i + 1) if z[k] < -1) >= 4 and z[i] < -1]
    if 7 in rules:
        hits["7_fifteen_within_1_sigma"] = [i for i in range(14, n) if all(abs(z[k]) < 1 for k in range(i - 14, i + 1))]
    if 8 in rules:
        hits["8_eight_outside_1_sigma"] = [i for i in range(7, n) if all(abs(z[k]) > 1 for k in range(i - 7, i + 1))]
    return hits


def chart(kind, rows, rules=(1, 2)):
    if not rows:
        fail("no data rows")
    if any((rw.get("phase") or "").strip() for rw in rows):
        return chart_phased(kind, rows, rules)
    labels = [rw.get("label") or str(i + 1) for i, rw in enumerate(rows)]
    extra = {}
    if kind == "imr":
        x = finite([rw.get("value") for rw in rows], "value")
        need(len(x), 3, "individuals chart")
        mr = [abs(b - a) for a, b in zip(x, x[1:])]
        mrbar = statistics.mean(mr)
        if mrbar == 0:
            fail("no point-to-point variation: limits cannot be set")
        sigma = mrbar / 1.128
        c = statistics.mean(x)
        pts, cl, sg = x, [c] * len(x), [sigma] * len(x)
        ucl, lcl = [c + 3 * sigma] * len(x), [c - 3 * sigma] * len(x)
        mr_ucl = 3.267 * mrbar
        limits = {"centre": r(c), "ucl": r(ucl[0]), "lcl": r(lcl[0]), "mr_bar": r(mrbar), "mr_ucl": r(mr_ucl)}
        extra["mr_beyond_ucl"] = [labels[i + 1] for i, v in enumerate(mr) if v > mr_ucl]
        basis = "Individuals chart: sigma = average moving range / 1.128; moving-range chart UCL = 3.267 × average MR."
    elif kind in ("p", "u"):
        cnt = [count(rw.get("count"), "count") for rw in rows]
        n = finite([rw.get("n") for rw in rows], "n")
        if any(m <= 0 for m in n):
            fail("every n must be > 0")
        if kind == "p" and any(c > m for c, m in zip(cnt, n)):
            fail("p chart: count cannot exceed n (defective items out of items inspected)")
        pbar = sum(cnt) / sum(n)
        if pbar == 0:
            fail("no defects at all: limits cannot be set")
        pts = [c / m for c, m in zip(cnt, n)]
        cl = [pbar] * len(pts)
        sg = [math.sqrt(pbar * (1 - pbar) / m) if kind == "p" else math.sqrt(pbar / m) for m in n]
        ucl = [pbar + 3 * s for s in sg]
        if kind == "p":
            ucl = [min(1.0, u) for u in ucl]
        lcl = [max(0.0, pbar - 3 * s) for s in sg]
        limits = {"centre": r(pbar), "ucl_by_point": [r(u) for u in ucl], "lcl_by_point": [r(v) for v in lcl]}
        basis = ("p chart: proportion defective per sample; limits vary with sample size, clipped to [0, 1]."
                 if kind == "p" else "u chart: defects per unit; limits vary with units, clipped at 0.")
    else:
        fail("chart kind must be imr, p or u")
    hits = run_rules(pts, cl, sg, set(rules))
    signals = {k: [labels[i] for i in v] for k, v in hits.items()}
    signals.update(extra)
    flagged = sorted({lab for v in signals.values() for lab in v}, key=labels.index)
    out = {"status": "ok", "chart": kind, "points": len(pts), "limits": limits, "rules_checked": sorted(rules),
           "signals": signals, "basis": basis,
           "limits_are": "exploratory — computed from these same data; freeze a baseline before monitoring new data",
           "not_a_spec": "Control limits describe what the process does, not what the customer needs. A stable "
                         "process can still miss the requirement — compare the level with the target or SLA."}
    if len(pts) < 20:
        out["warning"] = f"Only {len(pts)} points: limits are rough; 20-25 points is the usual minimum."
    out["plain"] = (f"Signal at: {', '.join(flagged)}." if flagged
                    else "No signal on the rules checked: the variation looks routine for this process. "
                         "That says nothing about whether the level is acceptable.")
    return out, pts, cl, ucl, lcl, labels


# ---------- process capability ----------

def capability(values, lsl=None, usl=None):
    x = finite(values, "value")
    need(len(x), 20, "capability (at least 20 values in time order)")
    if lsl is None and usl is None:
        fail("give --lsl and/or --usl (the customer's requirement, not control limits)")
    if lsl is not None and usl is not None and lsl >= usl:
        fail("--lsl must be below --usl")
    stab = chart("imr", [{"value": v} for v in x], rules=(1, 2))[0]
    flagged = [k for k, v in stab["signals"].items() if v]
    if flagged:
        fail("the process is not stable (signals: " + ", ".join(flagged) + "); a capability index would be "
             "misleading — find and remove the special causes first, then measure again")
    mu = statistics.mean(x)
    mr = [abs(b - a) for a, b in zip(x, x[1:])]
    s_within = statistics.mean(mr) / 1.128
    s_overall = statistics.stdev(x)
    def idx(s):
        parts = []
        if usl is not None:
            parts.append((usl - mu) / (3 * s))
        if lsl is not None:
            parts.append((mu - lsl) / (3 * s))
        both = (usl - lsl) / (6 * s) if (usl is not None and lsl is not None) else None
        return both, min(parts)
    cp, cpk = idx(s_within)
    pp, ppk = idx(s_overall)
    outside = sum(1 for v in x if (usl is not None and v > usl) or (lsl is not None and v < lsl))
    out = {"status": "ok", "n": len(x), "mean": r(mu), "sigma_within": r(s_within), "sigma_overall": r(s_overall),
           "Cp": r(cp) if cp is not None else None, "Cpk": r(cpk), "Pp": r(pp) if pp is not None else None,
           "Ppk": r(ppk), "observed_outside_spec": outside, "skewness": r(skewness(x)),
           "basis": "Stable on individuals-chart rules 1-2. Cp/Cpk use within sigma (average moving range / 1.128); "
                    "Pp/Ppk use the overall standard deviation. Indices assume roughly normal data.",
           "plain": (f"Of {len(x)} values, {outside} fell outside the requirement. "
                     f"Cpk {r(cpk, 2)}: " + ("the process fits inside the requirement with room to spare."
                                             if cpk >= 1.33 else "the process fits but with little room."
                                             if cpk >= 1.0 else "the process spread does not fit inside the requirement."))}
    if abs(skewness(x)) > 1:
        out["warning"] = "Data are clearly skewed: normal-based indices mislead. Report the share outside spec instead."
    elif len(x) < 50:
        out["warning"] = f"Only {len(x)} values: indices are rough (they can move by 0.2 or more with new data)."
    return out


# ---------- correlation and simple regression ----------

def regress(xs, ys):
    if len(xs) != len(ys):
        fail("x and y need the same number of rows")
    x, y = finite(xs, "x"), finite(ys, "y")
    n = len(x)
    need(n, 5, "regression")
    mx, my = statistics.mean(x), statistics.mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        fail("x or y does not vary: no relationship can be measured")
    sxy = sum((a - mx) * (b - my) for a, b in zip(x, y))
    slope = sxy / sxx
    icpt = my - slope * mx
    rr = sxy / math.sqrt(sxx * syy)
    df = n - 2
    resid = [b - (icpt + slope * a) for a, b in zip(x, y)]
    s2 = sum(e * e for e in resid) / df
    se_slope = math.sqrt(s2 / sxx)
    tq = t_ppf(0.975, df)
    if abs(rr) >= 1:
        p, ci_r = 0.0, [r(rr), r(rr)]
    else:
        tstat = rr * math.sqrt(df / (1 - rr * rr))
        p = t_sf2(tstat, df)
        zr, se_z = math.atanh(rr), 1 / math.sqrt(n - 3) if n > 3 else float("inf")
        ci_r = [r(math.tanh(zr - 1.959964 * se_z)), r(math.tanh(zr + 1.959964 * se_z))] if n > 3 else None
    rx, _ = _ranks(x)
    ry, _ = _ranks(y)
    mrx, mry = statistics.mean(rx), statistics.mean(ry)
    rho = (sum((a - mrx) * (b - mry) for a, b in zip(rx, ry))
           / math.sqrt(sum((a - mrx) ** 2 for a in rx) * sum((b - mry) ** 2 for b in ry)))
    out = {"status": "ok", "n": n, "pearson_r": r(rr), "ci_95_r": ci_r, "r_squared": r(rr * rr),
           "spearman_rho": r(rho), "slope": r(slope),
           "ci_95_slope": [r(slope - tq * se_slope), r(slope + tq * se_slope)], "intercept": r(icpt),
           "p_two_sided": r(p),
           "basis": "Least squares line; Pearson r with Fisher-z interval; Spearman rho on ranks (robust to outliers).",
           "not_a_cause": "A relationship in data is an association. It becomes a cause only when other explanations "
                          "are ruled out, e.g. by a trial that changes x on purpose.",
           "plain": (f"y changes by about {r(slope, 3)} per unit of x (95% range {r(slope - tq * se_slope, 3)} "
                     f"to {r(slope + tq * se_slope, 3)}); x explains {round(rr * rr * 100)}% of the variation in y.")}
    if abs(rr - rho) > 0.3:
        out["warning"] = "Pearson and Spearman disagree: a few extreme points or a curve drive the result — plot it."
    if n < 10:
        out.setdefault("warning", f"Only {n} pairs: the line is rough.")
    return out


# ---------- normality (D'Agostino-Pearson) ----------

def normality(values):
    x = finite(values, "value")
    n = len(x)
    need(n, 20, "normality test (fewer than 20 values: plot instead)")
    m = statistics.mean(x)
    m2 = sum((v - m) ** 2 for v in x) / n
    if m2 == 0:
        fail("all values are equal")
    m3 = sum((v - m) ** 3 for v in x) / n
    m4 = sum((v - m) ** 4 for v in x) / n
    g1, b2 = m3 / m2 ** 1.5, m4 / m2 ** 2
    y = g1 * math.sqrt((n + 1) * (n + 3) / (6.0 * (n - 2)))
    beta2 = 3.0 * (n * n + 27 * n - 70) * (n + 1) * (n + 3) / ((n - 2.0) * (n + 5) * (n + 7) * (n + 9))
    W2 = -1 + math.sqrt(2 * (beta2 - 1))
    delta = 1 / math.sqrt(0.5 * math.log(W2))
    alpha = math.sqrt(2.0 / (W2 - 1))
    y = y if y != 0 else 1
    zs = delta * math.log(y / alpha + math.sqrt((y / alpha) ** 2 + 1))
    E = 3.0 * (n - 1) / (n + 1)
    varb2 = 24.0 * n * (n - 2) * (n - 3) / ((n + 1) ** 2 * (n + 3) * (n + 5))
    xk = (b2 - E) / math.sqrt(varb2)
    sb1 = 6.0 * (n * n - 5 * n + 2) / ((n + 7) * (n + 9)) * math.sqrt(6.0 * (n + 3) * (n + 5) / (n * (n - 2) * (n - 3)))
    A = 6.0 + 8.0 / sb1 * (2.0 / sb1 + math.sqrt(1 + 4.0 / sb1 ** 2))
    t1 = 1 - 2 / (9.0 * A)
    den = 1 + xk * math.sqrt(2 / (A - 4.0))
    t2 = math.copysign(abs((1 - 2.0 / A) / den) ** (1 / 3.0), den) if den != 0 else float("nan")
    zk = (t1 - t2) / math.sqrt(2 / (9.0 * A))
    k2 = zs * zs + zk * zk
    p = chi2_sf(k2, 2)
    return {"status": "ok", "n": n, "skewness": r(g1), "excess_kurtosis": r(b2 - 3), "K2": r(k2), "p": r(p),
            "basis": "D'Agostino-Pearson test on skewness and kurtosis.",
            "plain": ("The data look clearly non-normal: use the rank-based comparison or a transformation."
                      if p < 0.05 else "No clear departure from normal shape — but always look at the plot; "
                      "a test cannot show a normal shape, only fail to find a departure."),
            "warning": "Large samples flag tiny, harmless departures; small samples miss big ones. Plot first."}


# ---------- decision matrix with weight sensitivity ----------

def decision_matrix(scores, weights):
    """scores: {option: {criterion: score}}; weights: {criterion: weight > 0}."""
    opts = list(scores)
    if len(opts) < 2:
        fail("need at least 2 options")
    crit = list(weights)
    if not crit or any(w <= 0 for w in weights.values()):
        fail("every criterion needs a positive weight")
    for o in opts:
        miss = [c for c in crit if c not in scores[o]]
        if miss:
            fail(f"option {o} has no score for: {', '.join(miss)}")
    def totals(w):
        return {o: sum(w[c] * scores[o][c] for c in crit) / sum(w.values()) for o in opts}
    base = totals(weights)
    rank = sorted(opts, key=lambda o: -base[o])
    flips = []
    for c in crit:
        for f in (0.5, 1.5):
            w = dict(weights); w[c] = weights[c] * f
            t = totals(w)
            top = max(opts, key=lambda o: t[o])
            if top != rank[0]:
                flips.append({"criterion": c, "weight_x": f, "new_winner": top})
    tie = len(rank) > 1 and abs(base[rank[0]] - base[rank[1]]) < 1e-9
    return {"status": "ok", "weighted_score": {o: r(base[o]) for o in rank}, "ranking": rank,
            "winner_changes_when": flips,
            "plain": ("Tie at the top: the scores do not decide this." if tie else
                      f"{rank[0]} comes first" + (" and stays first when any one weight is halved or raised by half."
                                                 if not flips else ", but the winner changes when some weights move — "
                                                 "the choice depends on those weights, so agree them first.")),
            "basis": "Weighted average of the scores; sensitivity: each weight halved and raised by 50%, one at a time.",
            "note": "Scores are judgements: write next to each one the evidence it rests on."}


# ---------- plots (SVG) ----------

def _svg_frame(title, w=700, h=360):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="sans-serif" font-size="11">',
            '<rect width="100%" height="100%" fill="white"/>',
            f'<text x="50" y="22" font-size="14">{html.escape(title)}</text>']


def plot(kind, rows, x=None, y=None, group=None, title="Plot"):
    w, h, L, R, T, B = 700, 360, 60, 20, 40, 50
    pw, ph = w - L - R, h - T - B
    parts = _svg_frame(title, w, h)
    if kind == "hist":
        v = finite([rw.get(x) for rw in rows if rw.get(x, "") != ""], x)
        need(len(v), 10, "histogram (fewer than 10 values: list them instead)")
        lo, hi = min(v), max(v)
        if lo == hi:
            fail("all values are equal")
        k = max(5, min(30, int(math.ceil(math.log2(len(v)) + 1))))
        width = (hi - lo) / k
        counts = [0] * k
        for t in v:
            counts[min(k - 1, int((t - lo) / width))] += 1
        mx = max(counts)
        for i, c in enumerate(counts):
            bh = ph * c / mx
            parts.append(f'<rect x="{L + i * pw / k:.1f}" y="{T + ph - bh:.1f}" width="{pw / k - 1:.1f}" height="{bh:.1f}" fill="#1f6feb"/>')
        parts.append(f'<text x="{L}" y="{h - 15}">{r(lo, 3)}</text><text x="{w - R - 40}" y="{h - 15}">{r(hi, 3)}</text>')
        info = {"bins": k, "counts": counts, "bin_width": r(width)}
    elif kind == "box":
        groups = {}
        for rw in rows:
            if rw.get(y, "") != "":
                groups.setdefault(rw.get(group, "") if group else "all", []).append(finite([rw[y]], y)[0])
        if not groups or any(len(g_) < 5 for g_ in groups.values()):
            fail("box plot needs at least 5 values per group")
        allv = [t for g_ in groups.values() for t in g_]
        lo, hi = min(allv), max(allv)
        sc = lambda t: T + ph - (t - lo) / ((hi - lo) or 1) * ph
        info = {}
        for i, (g_, v) in enumerate(groups.items()):
            q = statistics.quantiles(v, n=4, method="inclusive")
            cx = L + (i + 0.5) * pw / len(groups)
            parts.append(f'<line x1="{cx:.1f}" x2="{cx:.1f}" y1="{sc(max(v)):.1f}" y2="{sc(min(v)):.1f}" stroke="#555"/>')
            parts.append(f'<rect x="{cx - 20:.1f}" y="{sc(q[2]):.1f}" width="40" height="{sc(q[0]) - sc(q[2]):.1f}" fill="#cfe2ff" stroke="#1f6feb"/>')
            parts.append(f'<line x1="{cx - 20:.1f}" x2="{cx + 20:.1f}" y1="{sc(q[1]):.1f}" y2="{sc(q[1]):.1f}" stroke="#d1242f" stroke-width="2"/>')
            parts.append(f'<text x="{cx - 20:.1f}" y="{h - 15}">{html.escape(str(g_))[:12]}</text>')
            info[g_] = {"n": len(v), "q1": r(q[0]), "median": r(q[1]), "q3": r(q[2]), "min": r(min(v)), "max": r(max(v))}
    elif kind == "scatter":
        pts = [(finite([rw.get(x)], x)[0], finite([rw.get(y)], y)[0]) for rw in rows
               if rw.get(x, "") != "" and rw.get(y, "") != ""]
        need(len(pts), 5, "scatter plot")
        xs, ys = [a for a, _ in pts], [b for _, b in pts]
        sx = lambda t: L + (t - min(xs)) / ((max(xs) - min(xs)) or 1) * pw
        sy = lambda t: T + ph - (t - min(ys)) / ((max(ys) - min(ys)) or 1) * ph
        for a, b in pts:
            parts.append(f'<circle cx="{sx(a):.1f}" cy="{sy(b):.1f}" r="3.5" fill="#1f6feb" opacity="0.7"/>')
        parts.append(f'<text x="{w / 2:.0f}" y="{h - 10}">{html.escape(x)}</text><text x="8" y="{T + ph / 2:.0f}">{html.escape(y)}</text>')
        info = {"n": len(pts)}
    else:
        fail("plot kind must be hist, box or scatter")
    parts.append("</svg>")
    return {"status": "ok", "plot": kind, **({"summary": info} if info else {})}, "\n".join(parts)


# ---------- agreement between raters (attribute measurement check) ----------

def agreement(table, standard=None):
    """table: {item: {rater: category}}; standard: {item: category} or None."""
    items = [i for i in table if len(table[i]) >= 2]
    if len(items) < 5:
        fail("need at least 5 items rated by 2 or more raters")
    raters = sorted({rt for i in items for rt in table[i]})
    cats = sorted({c for i in items for c in table[i].values()} | (set(standard.values()) if standard else set()))
    out = {"status": "ok", "items": len(items), "raters": raters, "categories": cats}
    if len(raters) == 2 and all(len(table[i]) == 2 for i in items):
        a, b = raters
        agree = sum(1 for i in items if table[i][a] == table[i][b])
        po = agree / len(items)
        pe = sum((sum(1 for i in items if table[i][a] == c) / len(items)) *
                 (sum(1 for i in items if table[i][b] == c) / len(items)) for c in cats)
        kappa = (po - pe) / (1 - pe) if pe < 1 else 1.0
        lo, hi = wilson(agree, len(items))
        out.update({"method": "Cohen's kappa (2 raters)", "percent_agreement": r(po * 100, 1),
                    "ci_95_agreement_pct": [r(lo * 100, 1), r(hi * 100, 1)], "kappa": r(kappa)})
    else:
        m = {i: len(table[i]) for i in items}
        if len(set(m.values())) != 1:
            fail("with more than 2 raters, every item needs the same number of ratings")
        n = list(m.values())[0]
        N = len(items)
        nij = [[sum(1 for v in table[i].values() if v == c) for c in cats] for i in items]
        pj = [sum(row[j] for row in nij) / (N * n) for j in range(len(cats))]
        Pi = [(sum(x * x for x in row) - n) / (n * (n - 1)) for row in nij]
        Pbar, Pe = sum(Pi) / N, sum(p * p for p in pj)
        kappa = (Pbar - Pe) / (1 - Pe) if Pe < 1 else 1.0
        allsame = sum(1 for row in nij if max(row) == n)
        lo, hi = wilson(allsame, N)
        out.update({"method": f"Fleiss' kappa ({n} ratings per item)", "kappa": r(kappa),
                    "items_all_raters_agree_pct": r(allsame / N * 100, 1),
                    "ci_95_all_agree_pct": [r(lo * 100, 1), r(hi * 100, 1)]})
    if standard:
        per = {}
        for rt in raters:
            judged = [i for i in items if rt in table[i] and i in standard]
            ok = sum(1 for i in judged if table[i][rt] == standard[i])
            if judged:
                lo, hi = wilson(ok, len(judged))
                per[rt] = {"correct_pct": r(ok / len(judged) * 100, 1), "n": len(judged),
                           "ci_95_pct": [r(lo * 100, 1), r(hi * 100, 1)]}
        out["vs_standard"] = per
    k = out["kappa"]
    out["plain"] = ("Raters agree well beyond chance." if k >= 0.75 else
                    "Raters agree only moderately: the definition or training needs work before these ratings decide anything."
                    if k >= 0.4 else "Raters often disagree: these ratings cannot be trusted yet — fix the definition first.")
    out["basis"] = ("Kappa = agreement beyond what chance would give. Bands used for the plain sentence (0.75 / 0.40) "
                    "are a common rule of thumb, not a law; look at which categories are confused.")
    if len(items) < 30:
        out["warning"] = f"Only {len(items)} items: agreement figures are rough; 30-50 items is more usual."
    return out


# ---------- gauge study for measured values (crossed, ANOVA method) ----------

def gauge_rr(rows, tol=None):
    data = {}
    for rw in rows:
        v = finite([rw.get("value")], "value")[0]
        data.setdefault((rw.get("part", ""), rw.get("operator", "")), []).append(v)
    parts = sorted({k[0] for k in data}); ops = sorted({k[1] for k in data})
    if len(parts) < 2 or len(ops) < 2:
        fail("need at least 2 parts and 2 operators")
    reps = {len(v) for v in data.values()}
    if len(reps) != 1 or len(data) != len(parts) * len(ops) or min(reps) < 2:
        fail("every part x operator cell needs the same number (2 or more) of repeat measurements")
    rr_, p, o = reps.pop(), len(parts), len(ops)
    allv = [v for vs in data.values() for v in vs]
    g = statistics.mean(allv)
    mp = {pt: statistics.mean([v for (a, b), vs in data.items() if a == pt for v in vs]) for pt in parts}
    mo = {op: statistics.mean([v for (a, b), vs in data.items() if b == op for v in vs]) for op in ops}
    mc = {k: statistics.mean(vs) for k, vs in data.items()}
    ssp = o * rr_ * sum((mp[x] - g) ** 2 for x in parts)
    sso = p * rr_ * sum((mo[x] - g) ** 2 for x in ops)
    ssi = rr_ * sum((mc[(a, b)] - mp[a] - mo[b] + g) ** 2 for a in parts for b in ops)
    sse = sum((v - mc[k]) ** 2 for k, vs in data.items() for v in vs)
    dfp, dfo, dfi, dfe = p - 1, o - 1, (p - 1) * (o - 1), p * o * (rr_ - 1)
    msp, mso, msi, mse = ssp / dfp, sso / dfo, ssi / dfi, sse / dfe
    p_int = f_sf(msi / mse, dfi, dfe) if mse > 0 else 0.0
    if p_int > 0.25:  # interaction negligible: pool it into repeatability
        mse = (ssi + sse) / (dfi + dfe)
        v_int, msden = 0.0, mse
    else:
        v_int, msden = max(0.0, (msi - mse) / rr_), msi
    v_rep = mse
    v_op = max(0.0, (mso - msden) / (p * rr_))
    v_part = max(0.0, (msp - msden) / (o * rr_))
    v_grr = v_rep + v_op + v_int
    v_tot = v_grr + v_part
    if v_tot == 0:
        fail("no variation at all")
    pct = lambda v: r(math.sqrt(v / v_tot) * 100, 1)
    ndc = int(1.41 * math.sqrt(v_part / v_grr)) if v_grr > 0 else None
    out = {"status": "ok", "parts": p, "operators": o, "repeats": rr_,
           "interaction_p": r(p_int), "interaction_pooled": p_int > 0.25,
           "pct_study_var": {"repeatability": pct(v_rep), "reproducibility": pct(v_op + v_int),
                             "total_gauge": pct(v_grr), "part_to_part": pct(v_part)},
           "distinct_categories": ndc,
           "basis": "Crossed gauge study, two-way ANOVA; interaction pooled when p > 0.25; % of study variation uses "
                    "standard deviations."}
    if tol:
        out["pct_tolerance_total_gauge"] = r(6 * math.sqrt(v_grr) / tol * 100, 1)
    gpct = math.sqrt(v_grr / v_tot) * 100
    out["plain"] = ("The measurement is good enough to tell parts apart." if gpct < 10 else
                    "The measurement may be acceptable, depending on the use — check against the tolerance." if gpct < 30
                    else "The measurement system adds too much variation: fix it before trusting differences between items.")
    if p < 10:
        out["warning"] = f"Only {p} parts: the usual study uses about 10 parts covering the real range."
    return out


# ---------- two-level factorial experiments ----------

def doe_design(k, reps=1, seed=1):
    if not 2 <= k <= 5:
        fail("k must be 2 to 5 factors (more factors: use a screening design with a specialist)")
    if reps < 1:
        fail("replicates must be at least 1")
    import random as _r
    runs = []
    for rep in range(reps):
        for i in range(2 ** k):
            runs.append({"std_order": i + 1, "replicate": rep + 1,
                         **{f"F{j + 1}": (1 if (i >> j) & 1 else -1) for j in range(k)}})
    order = list(range(len(runs)))
    _r.Random(seed).shuffle(order)
    for pos, i in enumerate(order):
        runs[i]["run_order"] = pos + 1
    return {"status": "ok", "factors": k, "runs": len(runs), "replicates": reps,
            "design": sorted(runs, key=lambda x: x["run_order"]),
            "how": "Run in run_order (randomised). -1/+1 = the low/high setting you chose for each factor. "
                   "Hold everything else as steady as you can and record anything unusual.",
            "plain": f"{len(runs)} runs: every combination of {k} factors at two settings"
                     + (f", repeated {reps} times." if reps > 1 else ", once each (no repeats).")}


def doe_analyze(rows, factors, response):
    import itertools
    k = len(factors)
    if not 2 <= k <= 5:
        fail("give 2 to 5 factor columns")
    X, y = [], []
    for rw in rows:
        lv = []
        for f_ in factors:
            v = (rw.get(f_) or "").strip()
            if v not in ("-1", "1", "+1"):
                fail(f"factor {f_} must be coded -1 or +1 (got '{v}')")
            lv.append(1 if v in ("1", "+1") else -1)
        X.append(lv); y.append(finite([rw.get(response)], response)[0])
    cells = {}
    for lv, v in zip(X, y):
        cells.setdefault(tuple(lv), []).append(v)
    if len(cells) != 2 ** k:
        fail(f"a full factorial needs all {2 ** k} combinations; found {len(cells)}")
    reps = {len(v) for v in cells.values()}
    if len(reps) != 1:
        fail("every combination needs the same number of runs")
    n = len(y)
    terms = [c for m in range(1, k + 1) for c in itertools.combinations(range(k), m)]
    eff = {}
    for t in terms:
        sgn = [math.prod(lv[j] for j in t) for lv in X]
        eff[":".join(factors[j] for j in t)] = sum(s_ * v for s_, v in zip(sgn, y)) / (n / 2)
    out = {"status": "ok", "runs": n, "mean": r(statistics.mean(y)),
           "effects": {t: r(e) for t, e in sorted(eff.items(), key=lambda kv: -abs(kv[1]))}}
    rep = reps.pop()
    if rep > 1:
        sse = sum((v - statistics.mean(vs)) ** 2 for vs in cells.values() for v in vs)
        dfe = n - 2 ** k
        se = 2 * math.sqrt(sse / dfe / n)
        tq = t_ppf(0.975, dfe)
        out["significance"] = {t: {"p": r(t_sf2(abs(e) / se, dfe)), "ci_95": [r(e - tq * se), r(e + tq * se)]}
                               for t, e in eff.items()}
        real = [t for t, e in eff.items() if t_sf2(abs(e) / se, dfe) < 0.05]
        out["basis"] = "Replicated full factorial: effects tested against the pure-error variance (t test)."
    else:
        a = [abs(e) for e in eff.values()]
        s0 = 1.5 * statistics.median(a)
        pse = 1.5 * statistics.median([v for v in a if v < 2.5 * s0]) if any(v < 2.5 * s0 for v in a) else s0
        me = t_ppf(0.975, len(a) / 3) * pse
        out["lenth"] = {"pse": r(pse), "margin_of_error": r(me)}
        real = [t for t, e in eff.items() if abs(e) > me]
        out["basis"] = ("Unreplicated full factorial: effects judged with Lenth's pseudo standard error "
                        "(effects larger than the margin of error stand out from noise).")
    out["active"] = real
    out["plain"] = ("Effects that stand out from noise: " + ", ".join(real) + ". Confirm the best setting with a "
                    "few extra runs before adopting it." if real else
                    "No effect stands out from noise at these settings and this number of runs.")
    out["note"] = "Effect = change in the average response from low (-1) to high (+1). An interaction (A:B) means " \
                  "the effect of A depends on the setting of B — never change one factor at a time when that happens."
    return out


def chart_phased(kind, rows, rules):
    """Separate limits per phase (e.g. before / trial / after); phases are contiguous runs of the phase column."""
    segs = []
    for i, rw in enumerate(rows):
        ph_ = (rw.get("phase") or "").strip()
        if not ph_:
            fail(f"row {i + 2}: phase is blank — give every row a phase, or none")
        if not segs or segs[-1][0] != ph_:
            segs.append((ph_, []))
        segs[-1][1].append({k: v for k, v in rw.items() if k != "phase"})
    if len(segs) < 2:
        fail("only one phase: drop the phase column")
    names = [n for n, _ in segs]
    if len(set(names)) != len(names):
        fail("each phase must be one block of consecutive rows")
    P, PTS, CL, UCL, LCL, LAB = {}, [], [], [], [], []
    for n, seg in segs:
        o, pts, cl, ucl, lcl, lab = chart(kind, seg, rules)
        P[n] = {k: o[k] for k in ("points", "limits", "signals", "plain") if k in o}
        PTS += pts; CL += cl; UCL += ucl; LCL += lcl; LAB += [f"{n}:{l_}" for l_ in lab]
    shifts = []
    for (a, sa), (b, sb) in zip(segs, segs[1:]):
        va = [float(rw.get("value") if kind == "imr" else float(rw["count"]) / float(rw["n"])) for rw in sa]
        vb = [float(rw.get("value") if kind == "imr" else float(rw["count"]) / float(rw["n"])) for rw in sb]
        mw = mann_whitney(va, vb)
        shifts.append({"from": a, "to": b, "median_from": r(statistics.median(va)), "median_to": r(statistics.median(vb)),
                       "p_two_sided": mw["p_two_sided"]})
    out = {"status": "ok", "chart": kind, "phased": True, "phases": P, "level_change": shifts,
           "basis": "Limits computed separately inside each phase; level change between neighbouring phases by a "
                    "rank comparison of their values.",
           "not_a_spec": "A changed level is associated with the phase change; other changes in the same period "
                         "(volume, staff, season) must be ruled out before calling it the effect of the change.",
           "plain": "; ".join(f"{s_['from']} → {s_['to']}: median {s_['median_from']} → {s_['median_to']}"
                              + (" (unlikely to be chance)" if s_["p_two_sided"] < 0.05 else " (could be chance)")
                              for s_ in shifts)}
    return out, PTS, CL, UCL, LCL, LAB


def chart_svg(pts, cl, ucl, lcl, labels, title):
    w, h, pad = 700, 320, 50
    lo, hi = min(pts + lcl), max(pts + ucl)
    span = (hi - lo) or 1
    X = lambda i: pad + i * (w - 2 * pad) / max(1, len(pts) - 1)
    Y = lambda v: h - pad - (v - lo) * (h - 2 * pad) / span
    line = lambda vals, col, dash="": ('<polyline fill="none" stroke="%s" stroke-width="1.5" %s points="%s"/>'
                                       % (col, f'stroke-dasharray="{dash}"' if dash else "",
                                          " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))))
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" font-family="sans-serif" font-size="11">',
             '<rect width="100%" height="100%" fill="white"/>',
             f'<text x="{pad}" y="20" font-size="13">{html.escape(title)}</text>',
             line(ucl, "#d1242f", "5,4"), line(lcl, "#d1242f", "5,4"), line(cl, "#1a7f37", "2,3"), line(pts, "#1f6feb")]
    for i, v in enumerate(pts):
        out = v > ucl[i] or v < lcl[i]
        parts.append(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="3.5" fill="{"#d1242f" if out else "#1f6feb"}">'
                     f'<title>{html.escape(labels[i])}</title></circle>')
    parts.append("</svg>")
    return "\n".join(parts)


# ---------- sample size ----------

def size(kind, margin=None, sd=None, p=None, p1=None, p2=None, alpha=0.05, power=0.8):
    za = Z.inv_cdf(1 - alpha / 2)
    if kind == "mean":
        if not (sd and sd > 0 and margin and margin > 0):
            fail("mean: need sd > 0 (from past data or a pilot) and margin > 0")
        n = math.ceil((za * sd / margin) ** 2)
        basis = "n = (z × sd / margin)^2 (NIST e-Handbook 7.2.2.2); only as good as the sd estimate."
    elif kind == "proportion":
        if p is None or not 0 < p < 1 or not (margin and 0 < margin < 1):
            fail("proportion: need 0 < p < 1 (use 0.5 if unknown; a pilot with 0 events does not mean p = 0) "
                 "and 0 < margin < 1")
        n = math.ceil(za ** 2 * p * (1 - p) / margin ** 2)
        basis = "n = z^2 p(1-p) / margin^2 — a planning approximation."
    elif kind == "two-proportions":
        if p1 is None or p2 is None or not (0 < p1 < 1 and 0 < p2 < 1) or p1 == p2:
            fail("two-proportions: need 0 < p1, p2 < 1 and p1 ≠ p2")
        zb = Z.inv_cdf(power)
        pbar = (p1 + p2) / 2
        n = math.ceil((za * math.sqrt(2 * pbar * (1 - pbar)) + zb * math.sqrt(p1 * (1 - p1) + p2 * (1 - p2))) ** 2
                      / (p1 - p2) ** 2)
        basis = f"Per group, equal sizes, independent samples: {p1} vs {p2}, alpha {alpha} two-sided, power {power}."
    else:
        fail("kind must be mean, proportion or two-proportions")
    return {"status": "ok", "sample_size": n, "per_group": kind == "two-proportions", "basis": basis}


# ---------- cli ----------

def read_csv(path):
    try:
        with open(path, newline="", encoding="utf-8-sig") as f:
            rows = [{(k or "").strip().lower(): (v or "").strip() for k, v in rw.items()} for rw in csv.DictReader(f)]
    except OSError as e:
        fail(f"cannot read {path}: {e}")
    if not rows:
        fail("CSV has no data rows")
    return rows


def paired_columns(rows, a, b, id_col=None):
    """Keep only rows where BOTH values exist; report what was dropped. Never pair across rows."""
    keep, dropped = [], []
    for i, rw in enumerate(rows):
        rid = rw.get(id_col) if id_col else f"row {i + 2}"
        if rw.get(a, "") == "" or rw.get(b, "") == "":
            dropped.append(rid)
        else:
            keep.append((rid, rw[a], rw[b]))
    return finite([k[1] for k in keep], a), finite([k[2] for k in keep], b), [k[0] for k in keep], dropped


def selftest():
    close = lambda a, b, tol=1e-3: abs(a - b) < tol
    assert close(t_sf2(2.228139, 10), 0.05) and close(t_ppf(0.975, 10), 2.228139)
    assert close(t_ppf(0.9999, 1), 3183.0988, 0.01), t_ppf(0.9999, 1)
    assert close(chi2_sf(3.841459, 1), 0.05) and close(chi2_sf(18.307038, 10), 0.05)
    assert close(f_sf(4.964603, 1, 10), 0.05)
    assert close(fisher_2x2(3, 1, 1, 3), 0.485714)
    # paired: never pair across rows (review counter-example: true answer 3 pairs, mean diff +2)
    rows = [{"a": "10", "b": "9"}, {"a": "20", "b": ""}, {"a": "", "b": "90"}, {"a": "40", "b": "38"}, {"a": "50", "b": "47"}]
    xa, xb, kept, dropped = paired_columns(rows, "a", "b")
    pt = ttest(xa, xb, paired=True)
    assert pt["n"] == 3 and close(pt["difference"], 2.0) and dropped == ["row 3", "row 4"], (pt, dropped)
    # rounding must not flip the decision when units change
    big, tiny = ttest([1.0, 2.0, 3.0], [4.0, 5.0, 6.0]), ttest([1e-6, 2e-6, 3e-6], [4e-6, 5e-6, 6e-6])
    assert ("excludes" in big["plain"]) == ("excludes" in tiny["plain"]), (big["plain"], tiny["plain"])
    # sparse proportions: conclusion follows Fisher; zero events give a real interval
    sp = prop_test(0, 10, 4, 10)
    assert sp["decision_based_on"] == "fisher_exact_p" and "cannot rule out" in sp["plain"], sp
    zz = prop_test(0, 10, 0, 10)
    lo, hi = zz["ci_95_difference_newcombe"]
    assert lo < 0 < hi and "warning" in zz, zz
    nl, nh = newcombe(56, 70, 48, 80)  # Newcombe (1998) worked example: 0.0524 to 0.3339
    assert close(nl, 0.0524, 2e-3) and close(nh, 0.3339, 2e-3), (nl, nh)
    # I-MR: a moving-range jump must signal even when every point is inside the I limits
    series = [10, 10.5] * 4 + [13, 10.5] + [10, 10.5] * 4
    o = chart("imr", [{"value": v} for v in series])[0]
    assert o["signals"]["mr_beyond_ucl"] and o["plain"].startswith("Signal"), o
    o = chart("imr", [{"value": v} for v in [10, 11, 10, 11, 10, 11, 10, 11, 10, 11, 10, 25]])[0]
    assert o["signals"]["1_beyond_3_sigma"] == ["12"], o
    assert chart("imr", [{"value": v} for v in [1, 0] * 6 + [5] * 9], rules=(2,))[0]["signals"]["2_nine_same_side"]
    # impossible inputs must fail, never succeed
    for bad in (lambda: chart("imr", [{"value": "1"}, {"value": "nan"}, {"value": "2"}]),
                lambda: chisq([[1, -2], [3, 4]], ["r1", "r2"], ["c1", "c2"]),
                lambda: size("proportion", p=0.0, margin=0.05),
                lambda: prop_test(5, 4, 1, 10),
                lambda: chart("p", [{"count": 5, "n": 3}])):
        try:
            bad()
            raise AssertionError("bad input accepted")
        except InputError:
            pass
    # chi-square: an empty column is dropped, not counted in df
    cq = chisq([[10, 0, 20], [20, 0, 10]], ["a", "b"], ["x", "empty", "y"])
    assert cq["df"] == 1 and cq["dropped_empty"]["columns"] == ["empty"] and close(cq["chi2"], 6.6667), cq
    # Pareto threshold on the raw cumulative share (79.96% is not 80%)
    assert pareto({"a": 7996, "b": 3, "c": 2001})["categories_to_80_pct"] == 2
    # Mann-Whitney: all tied -> 0% strictly greater, 100% tied, p = 1
    mw = mann_whitney([1, 1, 1], [1, 1, 1])
    assert mw["share_pairs_a_greater"] == 0 and mw["share_pairs_tied"] == 1 and mw["p_two_sided"] == 1.0
    mw = mann_whitney([6, 7, 8, 9, 10], [1, 2, 3, 4, 5])
    assert mw["U"] == 25 and close(mw["p_two_sided"], 0.0122, 2e-3)
    ws = wilcoxon_signed([5, 6, 7, 8, 9, 10, 11, 12], [1, 2, 3, 4, 5, 6, 7, 8])
    assert ws["median_difference"] == 4 and ws["W_plus"] == 36, ws
    assert size("mean", margin=2, sd=10)["sample_size"] == 97
    # Nelson 5-8 on hand-built z-patterns (centre 0, sigma 1)
    c1, s1 = [0.0] * 20, [1.0] * 20
    assert run_rules([0, 0, 2.5, 0, 2.5] + [0] * 15, c1, s1, {5})["5_two_of_three_beyond_2_sigma"] == [4]
    assert run_rules([1.5, 1.5, 0, 1.5, 1.5] + [0] * 15, c1, s1, {6})["6_four_of_five_beyond_1_sigma"] == [4]
    assert run_rules([0.1] * 15 + [3] * 5, c1, s1, {7})["7_fifteen_within_1_sigma"] == [14]
    assert run_rules([1.5, -1.5] * 4 + [0] * 12, c1, s1, {8})["8_eight_outside_1_sigma"] == [7]
    # capability: refuses an unstable process; textbook arithmetic on a stable one
    try:
        capability([10] * 10 + [10.2] * 5 + [30] + [10.1] * 6, lsl=0, usl=40)
        raise AssertionError("unstable process accepted")
    except InputError:
        pass
    cap = capability([10, 11, 10, 11] * 6, lsl=4, usl=17)
    assert close(cap["Cp"], (17 - 4) / (6 * (1 / 1.128))) and cap["observed_outside_spec"] == 0, cap
    # regression: exact line, and a known correlation
    rg = regress([1, 2, 3, 4, 5], [3, 5, 7, 9, 11])
    assert close(rg["slope"], 2) and close(rg["intercept"], 1) and rg["pearson_r"] == 1, rg
    rg = regress([1, 2, 3, 4, 5, 6], [2, 1, 4, 3, 6, 5])
    assert close(rg["pearson_r"], 0.8286, 1e-3) and close(rg["spearman_rho"], 0.8286, 1e-3), rg
    # agreement: perfect and chance-level
    perfect = {str(i): {"a": c, "b": c} for i, c in enumerate("xyxyxyxyxy")}
    assert agreement(perfect)["kappa"] == 1.0
    ag = agreement({str(i): {"a": c1, "b": c2} for i, (c1, c2) in enumerate(zip("xxxxxyyyyy", "xxyyyxxxyy"))})
    assert close(ag["kappa"], -0.2, 1e-6) and ag["percent_agreement"] == 40.0, ag
    # gauge study: identical repeats, no operator effect -> gauge share 0, parts carry all variation
    rows_g = [{"part": str(pp), "operator": op, "value": pp * 1.0} for pp in range(10) for op in "AB" for _ in range(2)]
    rows_g[0]["value"] = 0.01
    g_ = gauge_rr(rows_g)
    assert g_["pct_study_var"]["part_to_part"] > 99, g_
    # factorial: y = 10 + 3A - 2B + 1.5AB exactly -> effects 6, -4, 3
    des = doe_design(2, reps=2)["design"]
    rows_d = [{"A": str(d["F1"]), "B": str(d["F2"]), "y": str(10 + 3 * d["F1"] - 2 * d["F2"] + 1.5 * d["F1"] * d["F2"]
                                                          + (0.1 if d["replicate"] == 1 else -0.1))} for d in des]
    da = doe_analyze(rows_d, ["A", "B"], "y")
    assert close(da["effects"]["A"], 6) and close(da["effects"]["B"], -4) and close(da["effects"]["A:B"], 3), da
    assert set(da["active"]) == {"A", "B", "A:B"}, da
    # phased chart: level shift between phases is detected; limits per phase
    rowsp = [{"phase": "before", "value": v} for v in [10, 11, 10, 12, 11, 10, 11, 12, 10, 11]] + \
            [{"phase": "after", "value": v} for v in [6, 7, 6, 5, 7, 6, 6, 7, 5, 6]]
    ph = chart("imr", rowsp)[0]
    assert ph["phased"] and ph["level_change"][0]["p_two_sided"] < 0.01 and set(ph["phases"]) == {"before", "after"}, ph
    # decision matrix: clear winner stable; close call flips
    dm = decision_matrix({"A": {"cost": 9, "speed": 9}, "B": {"cost": 2, "speed": 3}}, {"cost": 1, "speed": 1})
    assert dm["ranking"][0] == "A" and not dm["winner_changes_when"], dm
    dm = decision_matrix({"A": {"cost": 9, "speed": 2}, "B": {"cost": 2, "speed": 8}}, {"cost": 1, "speed": 1})
    assert dm["winner_changes_when"], dm
    # plots produce SVG and refuse tiny inputs
    o_, svg = plot("hist", [{"v": str(i % 7)} for i in range(30)], x="v")
    assert svg.startswith("<svg") and sum(o_["summary"]["counts"]) == 30
    try:
        plot("box", [{"y": "1"}], y="y"); raise AssertionError("tiny box accepted")
    except InputError:
        pass
    print("selftest ok")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    pa = sub.add_parser("pareto", help="CSV: category[,<weight>] — one row per occurrence, or a count/cost column")
    pa.add_argument("csv"); pa.add_argument("--weight", default="count", help="numeric column to sum, e.g. count or cost")
    rk = sub.add_parser("ranks", help="independent: CSV group,value (two groups) · paired: --paired --a COL --b COL")
    rk.add_argument("csv"); rk.add_argument("--paired", action="store_true")
    rk.add_argument("--a"); rk.add_argument("--b"); rk.add_argument("--id")
    t = sub.add_parser("ttest", help="CSV with one or two numeric columns")
    t.add_argument("csv"); t.add_argument("--a", required=True); t.add_argument("--b")
    t.add_argument("--mu", type=float); t.add_argument("--paired", action="store_true"); t.add_argument("--id")
    pr = sub.add_parser("prop", help="counts: --x1 --n1 [--x2 --n2 | --p0]")
    for k in ("x1", "n1", "x2", "n2"):
        pr.add_argument(f"--{k}")
    pr.add_argument("--p0", type=float)
    c = sub.add_parser("chisq", help="CSV table: first column = row label, other columns = category counts")
    c.add_argument("csv")
    a = sub.add_parser("anova", help="CSV with columns group,value")
    a.add_argument("csv")
    ch = sub.add_parser("chart", help="imr: label,value · p: label,count,n · u: label,count,n")
    ch.add_argument("kind", choices=["imr", "p", "u"]); ch.add_argument("csv")
    ch.add_argument("--rules", default="1,2"); ch.add_argument("--svg"); ch.add_argument("--title", default="Control chart")
    cp_ = sub.add_parser("capability", help="CSV label,value in time order; --lsl and/or --usl (the requirement)")
    cp_.add_argument("csv"); cp_.add_argument("--lsl", type=float); cp_.add_argument("--usl", type=float)
    rg_ = sub.add_parser("regress", help="CSV with two numeric columns; --x COL --y COL")
    rg_.add_argument("csv"); rg_.add_argument("--x", required=True); rg_.add_argument("--y", required=True)
    pl_ = sub.add_parser("plot", help="hist --x COL · box --y COL [--group COL] · scatter --x COL --y COL; --svg FILE")
    pl_.add_argument("kind", choices=["hist", "box", "scatter"]); pl_.add_argument("csv")
    pl_.add_argument("--x"); pl_.add_argument("--y"); pl_.add_argument("--group")
    pl_.add_argument("--svg", required=True); pl_.add_argument("--title", default="Plot")
    no_ = sub.add_parser("normality", help="CSV; --col COL (20+ values)")
    no_.add_argument("csv"); no_.add_argument("--col", default="value")
    mx_ = sub.add_parser("matrix", help="CSV option,criterion,score; --weights crit=w,crit=w")
    mx_.add_argument("csv"); mx_.add_argument("--weights", required=True)
    ag_ = sub.add_parser("agree", help="CSV item,rater,rating (one row per rating); --standard NAME marks the reference rater")
    ag_.add_argument("csv"); ag_.add_argument("--standard")
    gr_ = sub.add_parser("grr", help="CSV part,operator,value with 2+ repeats per cell; --tol optional")
    gr_.add_argument("csv"); gr_.add_argument("--tol", type=float)
    de_ = sub.add_parser("doe", help="design K [--reps R --seed S] · analyze CSV --factors A,B,.. --response Y")
    de_.add_argument("action", choices=["design", "analyze"]); de_.add_argument("arg")
    de_.add_argument("--reps", type=int, default=1); de_.add_argument("--seed", type=int, default=1)
    de_.add_argument("--factors"); de_.add_argument("--response")
    s = sub.add_parser("size")
    s.add_argument("kind", choices=["mean", "proportion", "two-proportions"])
    for k in ("margin", "sd", "p", "p1", "p2"):
        s.add_argument(f"--{k}", type=float)
    s.add_argument("--power", type=float, default=0.8)
    sub.add_parser("selftest")
    x = ap.parse_args()
    if x.cmd == "selftest":
        return selftest()
    try:
        if x.cmd == "pareto":
            counts = {}
            for rw in read_csv(x.csv):
                cat = rw.get("category", "")
                if cat == "":
                    fail("every row needs a category")
                w = finite([rw[x.weight]], x.weight)[0] if rw.get(x.weight, "") != "" else 1.0
                if w < 0:
                    fail(f"{x.weight} must not be negative")
                counts[cat] = counts.get(cat, 0) + w
            res = pareto(counts)
            res["measure"] = x.weight
        elif x.cmd == "ranks":
            rows = read_csv(x.csv)
            if x.paired:
                if not (x.a and x.b):
                    fail("--paired needs --a and --b columns")
                xa, xb, kept, dropped = paired_columns(rows, x.a, x.b, x.id)
                res = wilcoxon_signed(xa, xb)
                res["rows_dropped_incomplete"] = dropped
            else:
                groups = {}
                for rw in rows:
                    if rw.get("value", "") != "":
                        groups.setdefault(rw.get("group", ""), []).append(finite([rw["value"]], "value")[0])
                if rows and not {"group", "value"} <= set(rows[0]):
                    fail(f"independent ranks needs columns group,value; got {','.join(rows[0])}")
                if len(groups) != 2:
                    fail(f"independent ranks needs exactly two groups, got {len(groups)}")
                (ga, a_), (gb, b_) = groups.items()
                res = mann_whitney(a_, b_)
                res["groups"] = [ga, gb]
        elif x.cmd == "ttest":
            rows = read_csv(x.csv)
            if x.paired:
                if not x.b:
                    fail("--paired needs --b")
                xa, xb, kept, dropped = paired_columns(rows, x.a, x.b, x.id)
                res = ttest(xa, xb, paired=True)
                res["rows_dropped_incomplete"] = dropped
            else:
                xa = finite([rw[x.a] for rw in rows if rw.get(x.a, "") != ""], x.a)
                xb = finite([rw[x.b] for rw in rows if rw.get(x.b, "") != ""], x.b) if x.b else None
                res = ttest(xa, xb, x.mu)
        elif x.cmd == "prop":
            if x.x1 is None or x.n1 is None:
                fail("give --x1 and --n1")
            if x.x2 is None and x.p0 is None:
                fail("give --x2 --n2 for two proportions, or --p0 for one")
            res = prop_test(x.x1, x.n1, x.x2, x.n2, x.p0)
        elif x.cmd == "chisq":
            rows = read_csv(x.csv)
            keys = list(rows[0])[1:]
            res = chisq([[rw[k] for k in keys] for rw in rows], [list(rw.values())[0] for rw in rows], keys)
        elif x.cmd == "anova":
            groups = {}
            for rw in read_csv(x.csv):
                if rw.get("value", "") != "":
                    groups.setdefault(rw.get("group", ""), []).append(finite([rw["value"]], "value")[0])
            res = anova(groups)
        elif x.cmd == "chart":
            try:
                rules = tuple(int(v) for v in x.rules.split(","))
            except ValueError:
                fail("--rules like 1,2")
            res, pts, cl, ucl, lcl, labels = chart(x.kind, read_csv(x.csv), rules)
            if x.svg:
                with open(x.svg, "w", encoding="utf-8") as f:
                    f.write(chart_svg(pts, cl, ucl, lcl, labels, x.title))
                res["svg"] = x.svg
        elif x.cmd == "plot":
            need_cols = {"hist": ["x"], "box": ["y"], "scatter": ["x", "y"]}[x.kind]
            if any(getattr(x, c) is None for c in need_cols):
                fail(f"plot {x.kind} needs --" + " --".join(need_cols))
            res, svg = plot(x.kind, read_csv(x.csv), x.x, x.y, x.group, x.title)
            with open(x.svg, "w", encoding="utf-8") as f:
                f.write(svg)
            res["svg"] = x.svg
        elif x.cmd == "normality":
            res = normality([rw.get(x.col) for rw in read_csv(x.csv) if rw.get(x.col, "") != ""])
        elif x.cmd == "matrix":
            try:
                wts = {k.strip(): float(v) for k, v in (kv.split("=") for kv in x.weights.split(","))}
            except ValueError:
                fail("--weights like cost=3,speed=1")
            sc_ = {}
            for rw in read_csv(x.csv):
                sc_.setdefault(rw.get("option", ""), {})[rw.get("criterion", "")] = finite([rw.get("score")], "score")[0]
            res = decision_matrix(sc_, wts)
        elif x.cmd == "agree":
            table, std = {}, {}
            for rw in read_csv(x.csv):
                it, rt, rating = rw.get("item", ""), rw.get("rater", ""), (rw.get("rating") or "").strip()
                if not it or not rt or rating == "":
                    fail("every row needs item, rater and rating")
                if x.standard and rt == x.standard:
                    std[it] = rating
                else:
                    table.setdefault(it, {})[rt] = rating
            res = agreement(table, std or None)
        elif x.cmd == "grr":
            res = gauge_rr(read_csv(x.csv), x.tol)
        elif x.cmd == "doe":
            if x.action == "design":
                try:
                    k = int(x.arg)
                except ValueError:
                    fail("doe design needs the number of factors, e.g. doe design 3")
                res = doe_design(k, x.reps, x.seed)
            else:
                if not (x.factors and x.response):
                    fail("doe analyze needs --factors A,B,.. and --response COL")
                res = doe_analyze(read_csv(x.arg), [f.strip() for f in x.factors.split(",")], x.response)
        elif x.cmd == "capability":
            res = capability([rw.get("value") for rw in read_csv(x.csv) if rw.get("value", "") != ""], x.lsl, x.usl)
        elif x.cmd == "regress":
            rows = [rw for rw in read_csv(x.csv) if rw.get(x.x, "") != "" and rw.get(x.y, "") != ""]
            res = regress([rw[x.x] for rw in rows], [rw[x.y] for rw in rows])
        else:
            res = size(x.kind, x.margin, x.sd, x.p, x.p1, x.p2, power=x.power)
    except (InputError, ArithmeticError) as e:
        print(json.dumps({"status": "error", "error": str(e)}, ensure_ascii=False))
        sys.exit(2)
    print(json.dumps(res, indent=2, ensure_ascii=False, allow_nan=False))


if __name__ == "__main__":
    main()
