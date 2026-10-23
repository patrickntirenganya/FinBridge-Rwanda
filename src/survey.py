"""Survey-weighted estimation helpers for FinBridge Insights.

Proportions use the ratio estimator with Taylor-linearized variance.
When a cluster (PSU) variable is supplied, variance is computed from
PSU totals within strata (with-replacement approximation). When no PSU
is available (FinScope public file), each respondent is treated as its
own PSU, which UNDERSTATES uncertainty; callers must disclose this.
"""
from __future__ import annotations
import numpy as np
import pandas as pd

Z95 = 1.959964


def wprop(y, w, psu=None, strata=None):
    """Weighted proportion of a 0/1 (or boolean) series with 95% CI.

    Returns dict(est, se, lo, hi, n) with est/lo/hi in percent.
    Rows where y is missing are dropped.
    """
    d = pd.DataFrame({"y": pd.Series(y).astype(float), "w": pd.Series(w).astype(float)})
    d["psu"] = np.arange(len(d)) if psu is None else pd.Series(psu).values
    d["str"] = 0 if strata is None else pd.Series(strata).values
    d = d.dropna(subset=["y", "w"])
    n = len(d)
    if n == 0 or d.w.sum() == 0:
        return dict(est=np.nan, se=np.nan, lo=np.nan, hi=np.nan, n=0)
    p = (d.w * d.y).sum() / d.w.sum()
    d["z"] = d.w * (d.y - p) / d.w.sum()          # linearized score
    t = d.groupby(["str", "psu"]).z.sum().reset_index()
    var = 0.0
    for _, g in t.groupby("str"):
        k = len(g)
        if k > 1:
            var += k / (k - 1) * ((g.z - g.z.mean()) ** 2).sum()
    se = np.sqrt(var)
    return dict(est=100 * p, se=100 * se,
                lo=100 * max(0.0, p - Z95 * se), hi=100 * min(1.0, p + Z95 * se), n=n)


def wprop_by(df, ycol, wcol, bycol, psu=None, strata=None, labels=None):
    """Weighted proportion of ycol within each level of bycol."""
    rows = []
    for lev, g in df.groupby(bycol, dropna=True):
        r = wprop(g[ycol], g[wcol],
                  None if psu is None else g[psu],
                  None if strata is None else g[strata])
        r[bycol] = labels.get(lev, lev) if labels else lev
        rows.append(r)
    out = pd.DataFrame(rows)
    return out[[bycol, "est", "lo", "hi", "se", "n"]] if len(out) else out


def fmt(r):
    return f"{r['est']:.1f}% (95% CI {r['lo']:.1f}–{r['hi']:.1f}, n={r['n']})"
