"""Adjusted associations (not causal effects).

Both models are survey-weighted logistic regressions. Weights are normalised
to mean 1 so that sandwich standard errors are on the person/household scale.
  AHS: cluster-robust SEs, groups = clust (primary sampling unit).
  FinScope: public file has no PSU, so HC1 robust SEs are used and understate
  uncertainty. Say so wherever the output is shown.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf


class _Fit:
    """Coefficients from a weighted GLM with a survey sandwich covariance."""
    def __init__(self, names, params, cov):
        self.params = pd.Series(params, index=names)
        se = pd.Series(np.sqrt(np.diag(cov)), index=names)
        self.bse = se
        z = self.params / se
        from scipy.stats import norm
        self.pvalues = pd.Series(2 * norm.sf(np.abs(z)), index=names)
        self._ci = pd.DataFrame({0: self.params - 1.959964 * se, 1: self.params + 1.959964 * se})

    def conf_int(self):
        return self._ci


def _fit(d: pd.DataFrame, formula: str, weight: str, cluster: str | None):
    """Point estimates from a weighted binomial GLM; covariance from the design-based
    sandwich  B^-1 (sum over clusters of summed weighted scores) B^-1.
    Without a cluster variable each respondent is its own cluster (HC1-style)."""
    d = d.copy()
    d["_w"] = d[weight] / d[weight].mean()
    glm = smf.glm(formula, data=d, family=sm.families.Binomial(), freq_weights=d["_w"]).fit()
    X = glm.model.exog
    mu = glm.fittedvalues.values
    w = d["_w"].values
    y = glm.model.endog
    bread = np.linalg.inv((X * (w * mu * (1 - mu))[:, None]).T @ X)
    scores = X * (w * (y - mu))[:, None]
    g = d[cluster].values if cluster else np.arange(len(d))
    cs = pd.DataFrame(scores).groupby(g).sum().values
    k, n = X.shape[1], len(d)
    c = len(cs)
    meat = cs.T @ cs * (c / (c - 1)) * ((n - 1) / (n - k))
    return _Fit(glm.model.exog_names, glm.params.values, bread @ meat @ bread)


def odds_table(res, labels: dict[str, tuple[str, str, str]], model: str, n: int) -> pd.DataFrame:
    """labels: term -> (variable label, level label, reference label)."""
    ci = res.conf_int()
    rows = []
    for term, (var, lev, ref) in labels.items():
        rows.append(dict(model=model, variable=var, level=lev, reference=ref,
                         odds_ratio=float(np.exp(res.params[term])),
                         lo=float(np.exp(ci.loc[term, 0])), hi=float(np.exp(ci.loc[term, 1])),
                         p=float(res.pvalues[term]), n=n))
    return pd.DataFrame(rows).round({"odds_ratio": 2, "lo": 2, "hi": 2, "p": 4})


def ahs_model(H: pd.DataFrame) -> pd.DataFrame:
    """Formal loan among agricultural households."""
    d = H.dropna(subset=["quintile", "head_sex", "farm_size", "province"]).copy()
    d["y"] = d.loan_formal.astype(int)
    d["coop_member"] = d.coop.astype(int)
    d["titled"] = d.land_title.astype(int)
    d["female_head"] = (d.head_sex == "Female-headed").astype(int)
    d["q"] = pd.Categorical(d.quintile, ["Q1 (poorest)", "Q2", "Q3", "Q4", "Q5 (richest)"])
    d["fs"] = pd.Categorical(d.farm_size, ["< 0.1 ha", "0.1–0.3 ha", "0.3–1 ha", "> 1 ha"])
    d["prov"] = pd.Categorical(d.province)
    ref_prov = d.prov.cat.categories[0]
    f = ("y ~ female_head + C(q, Treatment('Q1 (poorest)')) + C(fs, Treatment('< 0.1 ha')) "
         f"+ titled + coop_member + C(prov, Treatment('{ref_prov}'))")
    res = _fit(d, f, "weight", "clust")
    lab = {"female_head": ("Head's sex", "Female-headed", "Male-headed"),
           "titled": ("Land title", "Has titled land", "No titled land"),
           "coop_member": ("Cooperative", "Member", "Not a member")}
    for q in ["Q2", "Q3", "Q4", "Q5 (richest)"]:
        lab[f"C(q, Treatment('Q1 (poorest)'))[T.{q}]"] = ("Consumption quintile", q, "Q1 (poorest)")
    for s in ["0.1–0.3 ha", "0.3–1 ha", "> 1 ha"]:
        lab[f"C(fs, Treatment('< 0.1 ha'))[T.{s}]"] = ("Farm size", s, "< 0.1 ha")
    for p in d.prov.cat.categories[1:]:
        lab[f"C(prov, Treatment('{ref_prov}'))[T.{p}]"] = ("Province", p, ref_prov)
    return odds_table(res, lab, "ahs_formal_loan", len(d))


def fs_records_model(F: pd.DataFrame) -> pd.DataFrame:
    """Formal credit among farming adults who were asked about tracking money."""
    d = F[F.farm_status.isin(["Farming only", "Farming + other work"]) & F.tracks_money.notna()].copy()
    d = d.dropna(subset=["sex", "age_band", "education", "area", "ubudehe", "province"])
    d["y"] = d.formal_credit.astype(int)
    d["tracks"] = d.tracks_money.astype(int)
    d["female"] = (d.sex == "Female").astype(int)
    d["rural"] = (d.area == "Rural").astype(int)
    d["smart"] = d.smartphone.astype(int)
    d["momo"] = d.momo_registered.astype(int)
    f = ("y ~ tracks + female + rural + smart + momo + C(age_band, Treatment('18–30')) "
         "+ C(education, Treatment('Primary')) + C(ubudehe, Treatment('Category 3')) "
         "+ C(province, Treatment('South'))")
    d = d[d.age_band != "16–17"]
    res = _fit(d, f, "weight", None)
    lab = {"tracks": ("Always tracks money", "Yes", "No"),
           "female": ("Sex", "Female", "Male"),
           "rural": ("Area", "Rural", "Urban"),
           "smart": ("Smartphone", "Owns one", "Does not"),
           "momo": ("Mobile money", "Registered", "Not registered")}
    for a in ["31–45", "46–60", "61+"]:
        lab[f"C(age_band, Treatment('18–30'))[T.{a}]"] = ("Age", a, "18–30")
    for e in ["No formal education", "Secondary", "Vocational", "University / higher"]:
        lab[f"C(education, Treatment('Primary'))[T.{e}]"] = ("Education", e, "Primary")
    for u in ["Category 1", "Category 2", "Category 4", "Not yet classified"]:
        lab[f"C(ubudehe, Treatment('Category 3'))[T.{u}]"] = ("Ubudehe", u, "Category 3")
    for p in ["East", "Kigali", "North", "West"]:
        k = f"C(province, Treatment('South'))[T.{p}]"
        if k in res.params.index:
            lab[k] = ("Province", p, "South")
    return odds_table(res, lab, "fs_formal_credit", len(d))
