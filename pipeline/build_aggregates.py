"""Build every table the app needs from the raw microdata.

Run:  python pipeline/build_aggregates.py
Out:  data/aggregates/*.csv  (aggregates only, safe to commit)

Disclosure and reliability rules
  * n < MIN_N  -> estimate suppressed (blank), flagged "suppressed"
  * CV > 0.30  -> flagged "caution"
"""
from __future__ import annotations
import json, sys
from datetime import date
from pathlib import Path
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.survey import wprop, wprop_by
from src.indicators import (build_finscope, build_ahs, FS_INDICATORS, FS_GROUPS,
                            AHS_INDICATORS, AHS_GROUPS, FORMAL_LOAN_SOURCES, AGRI_PURPOSES, TONTINE_BRIDGE,
                            FS_FARMER_GROUPS)
from src.models import ahs_model, fs_records_model
from src.load import finscope, ahs, labels

OUT = ROOT / "data" / "aggregates"
OUT.mkdir(parents=True, exist_ok=True)
MIN_N = 30


def flag(df):
    df = df.copy()
    df["reliability"] = "ok"
    cv = df.se / df.est.where(df.est > 0)
    df.loc[cv > 0.30, "reliability"] = "caution"
    small = df.n < MIN_N
    df.loc[small, ["est", "lo", "hi", "se"]] = None
    df.loc[small, "reliability"] = "suppressed"
    return df.round({"est": 1, "lo": 1, "hi": 1, "se": 2})


def national(data, inds, w, psu, strata):
    rows = []
    for k, lab in inds.items():
        r = wprop(data[k], data[w], None if psu is None else data[psu], data[strata])
        rows.append(dict(indicator=k, label=lab, **r))
    return flag(pd.DataFrame(rows))


def by_group(data, inds, groups, w, psu, strata):
    frames = []
    for g, glab in groups.items():
        for k, lab in inds.items():
            t = wprop_by(data, k, w, g, psu=psu, strata=strata).rename(columns={g: "group"})
            t.insert(0, "group_var", g); t.insert(1, "group_label", glab)
            t.insert(0, "indicator", k); t.insert(1, "label", lab)
            frames.append(t)
    return flag(pd.concat(frames, ignore_index=True))


def shares(data, col, codes: dict, w="weight", psu="clust", strata="district", **extra):
    rows = []
    for code, lab in codes.items():
        r = wprop(data[col] == code, data[w], data[psu], data[strata])
        rows.append(dict(code=code, category=lab, **extra, **r))
    return flag(pd.DataFrame(rows))


CROPS = {101: "Maize", 102: "Paddy rice", 106: "Bush bean", 107: "Climbing bean"}
SEASONS = {1: "A", 2: "B", 3: "C"}
SLOTS = range(1, 8)          # the file carries 7 crop slots per plot
MIN_PLOTS = 100
TRIM = 0.01


def wquantiles(x, w, qs):
    o = np.argsort(x)
    x, w = x[o], w[o]
    c = np.cumsum(w) / w.sum()
    return [float(x[min(np.searchsorted(c, q), len(x) - 1)]) for q in qs]


def yield_benchmarks():
    """Weighted yield quartiles (kg per effective ha) by crop x season, from AHS Section 3.

    effective area = plot area x crop share of plot; top and bottom 1% trimmed per crop x season.
    """
    d, _ = ahs("Section3_4")
    parts = []
    for k in SLOTS:
        t = d[[f"s3_q4_{k}", f"s3_q4_{k}a", f"s3_q20_{k}", "s2q2", "Season", "weight"]].copy()
        t.columns = ["crop", "share", "kg", "area_m2", "season", "w"]
        parts.append(t)
    a = pd.concat(parts)
    a = a[a.crop.isin(CROPS) & (a.kg > 0) & (a.area_m2 > 0)].copy()
    a["ha"] = a.area_m2 / 1e4 * a.share.clip(1, 100) / 100
    a["y"] = a.kg / a.ha
    rows = []
    for (crop, season), g in a.groupby(["crop", "season"]):
        lo, hi = g.y.quantile([TRIM, 1 - TRIM])
        g = g[(g.y >= lo) & (g.y <= hi)]
        if len(g) < MIN_PLOTS:
            continue
        p25, p50, p75 = wquantiles(g.y.values, g.w.values, [.25, .5, .75])
        rows.append(dict(crop=CROPS[int(crop)], season=SEASONS[int(season)], n=int(len(g)),
                         p25=round(p25), p50=round(p50), p75=round(p75),
                         intercropped_pct=round(100 * float(np.average(g.share < 100, weights=g.w)), 1)))
    return dict(
        source="AHS 2024 Section 3, plot x crop slots 1-7, weighted by 'weight'",
        unit="kg per hectare of the crop's own share of the plot",
        method=f"top and bottom {int(TRIM * 100)}% of yields trimmed per crop x season; "
               f"groups with fewer than {MIN_PLOTS} plots omitted; national only",
        benchmarks=rows)


def input_use():
    """Plot-level weighted shares of input use, national and by district (n < 30 suppressed)."""
    d, _ = ahs("Section3_4")
    m0, meta0 = ahs("Section0")
    names = labels(meta0, "district")
    d = d.assign(
        organic=d.s4_q1 == 1, inorganic=d.s4_q4 == 1, pesticide=d.s4_q12 == 1,
        improved_seed=d.s3_q9_1.isin([2, 3]).where(d.s3_q9_1.notna()),
        irrigated=d.s4_q22 == 1, cant_afford_irrigation=(d.s4_q22 == 3).where(d.s4_q22.notna()))
    inds = ["organic", "inorganic", "pesticide", "improved_seed", "irrigated", "cant_afford_irrigation"]

    def block(sub):
        out = {}
        for k in inds:
            r = wprop(sub[k], sub.weight, sub.clust, sub.district)
            out[k] = None if r["n"] < MIN_N else dict(est=round(r["est"], 1), lo=round(r["lo"], 1),
                                                       hi=round(r["hi"], 1), n=int(r["n"]))
        return out

    return dict(
        source="AHS 2024 Section 3-4, plot level, weight=weight, PSU=clust, stratum=district",
        indicators=dict(organic="Organic fertilizer used", inorganic="Inorganic fertilizer used",
                        pesticide="Pesticide used", improved_seed="Improved seed used (main crop)",
                        irrigated="Plot irrigated", cant_afford_irrigation="Could not afford irrigation"),
        national=block(d),
        districts={names.get(int(c), str(int(c))): block(g) for c, g in d.groupby("district")})


def main():
    (OUT / "yield_benchmarks.json").write_text(json.dumps(yield_benchmarks(), indent=1))
    (OUT / "input_use.json").write_text(json.dumps(input_use(), indent=1))
    # ------------------------------------------------------------- AHS
    H, L, D = build_ahs()
    groups = {k: v for k, v in AHS_GROUPS.items() if k != "district"}
    national(H, AHS_INDICATORS, "weight", "clust", "district").to_csv(OUT / "ahs_national.csv", index=False)
    bg = by_group(H, AHS_INDICATORS, groups, "weight", "clust", "district")
    dist = by_group(H.assign(district_grp=H.district_name), AHS_INDICATORS,
                    {"district_grp": "District"}, "weight", "clust", "district")
    dist["group_var"] = "district"
    pd.concat([bg, dist]).to_csv(OUT / "ahs_by_group.csv", index=False)

    # mutually exclusive segments for the headline chart
    seg = pd.Series("No formal account", index=H.index)
    seg[H.acct_formal & ~H.loan_any] = "Account, did not borrow"
    seg[H.acct_formal & H.loan_any & ~H.loan_formal] = "Account, borrowed only informally"
    seg[H.acct_formal & H.loan_formal] = "Account and formal loan"
    H["segment"] = seg
    rows = []
    for s in ["Account and formal loan", "Account, borrowed only informally",
              "Account, did not borrow", "No formal account"]:
        rows.append(dict(segment=s, **wprop(H.segment == s, H.weight, H.clust, H.district)))
    flag(pd.DataFrame(rows)).to_csv(OUT / "ahs_segments.csv", index=False)

    # F1: where the "account, borrowed only informally" households are, by district
    rows = []
    for name, g in H.groupby("district_name"):
        r = wprop(g.segment == "Account, borrowed only informally", g.weight, g.clust, g.district)
        hh = float(g.weight.sum())
        rows.append(dict(district=name, province=g.province.mode().iat[0], est=r["est"], lo=r["lo"], hi=r["hi"],
                         se=r["se"], district_households=round(hh), households=r["est"] / 100 * hh,
                         hh_lo=r["lo"] / 100 * hh, hh_hi=r["hi"] / 100 * hh, n=r["n"]))
    opp = flag(pd.DataFrame(rows)).rename(columns={"est": "pct"})
    opp[["district_households", "households", "hh_lo", "hh_hi"]] = opp[["district_households", "households", "hh_lo", "hh_hi"]].round(0)
    opp.loc[opp.reliability == "suppressed", ["households", "hh_lo", "hh_hi"]] = None
    opp.sort_values("households", ascending=False).to_csv(OUT / "ahs_district_opportunity.csv", index=False)

    # F2: tontine -> SACCO bridge
    rows = []
    for col, lab, base, base_lab in TONTINE_BRIDGE:
        sub = H if base is None else H[H[base]]
        rows.append(dict(indicator=col, label=lab, base=base_lab, **wprop(sub[col], sub.weight, sub.clust, sub.district)))
    flag(pd.DataFrame(rows)).to_csv(OUT / "ahs_tontine_bridge.csv", index=False)

    _, cm = ahs("Credits")
    src = shares(L, "s10q6", labels(cm, "s10q6"))
    src["formal"] = src.code.isin(FORMAL_LOAN_SOURCES)
    src["kind"] = src.code.map({2: "formal", 4: "formal", 6: "formal", 3: "informal", 5: "informal",
                                1: "other", 7: "other"}).fillna("other")
    src.to_csv(OUT / "ahs_loan_sources.csv", index=False)

    purp = shares(L, "s10aq7", labels(cm, "s10aq7"))
    formal_share = []
    for code in purp.code:
        sub = L[L.s10aq7 == code]
        r = wprop(sub.s10q6.isin(FORMAL_LOAN_SOURCES), sub.weight, sub.clust, sub.district)
        formal_share.append(r["est"] if r["n"] >= MIN_N else None)
    purp["formal_source_pct"] = pd.Series(formal_share).round(1)
    purp["agri_purpose"] = purp.code.isin(AGRI_PURPOSES)
    purp.to_csv(OUT / "ahs_loan_purpose.csv", index=False)

    shares(D, "s10aq2", labels(cm, "s10aq2")).to_csv(OUT / "ahs_denial_reasons.csv", index=False)

    # -------------------------------------------------------- FinScope
    F = build_finscope()
    national(F, FS_INDICATORS, "weight", None, "stratum").to_csv(OUT / "fs_national.csv", index=False)
    by_group(F, FS_INDICATORS, FS_GROUPS, "weight", None, "stratum").to_csv(OUT / "fs_by_group.csv", index=False)

    # farming adults only (m1 = 1 or 2): digital readiness and record-keeping
    FF = F[F.farm_status.isin(["Farming only", "Farming + other work"])]
    fdig = {k: FS_INDICATORS[k] for k in ["own_phone", "smartphone", "momo_registered",
                                          "tracks_money", "budgets", "formal_credit"]}
    pd.concat([national(FF.assign(all_farmers="All farming adults"), fdig, "weight", None, "stratum")
               .assign(group_var="all", group_label="All", group="All farming adults"),
               by_group(FF, fdig, FS_FARMER_GROUPS, "weight", None, "stratum")]
              ).to_csv(OUT / "fs_farmer_digital.csv", index=False)
    link = []
    for lev, sub in list(FF[FF.track_level.notna()].groupby("track_level")):
        r = wprop(sub.formal_credit, sub.weight, None, sub.stratum)
        link.append(dict(track_level=lev, **r))
    flag(pd.DataFrame(link)).to_csv(OUT / "fs_records_link.csv", index=False)

    # adjusted associations (odds ratios), not causal effects
    pd.concat([ahs_model(H), fs_records_model(F)]).to_csv(OUT / "models.csv", index=False)

    _, fm = finscope()
    frames = []
    for q, title in [("h7", "Main reason for not borrowing"), ("k17", "Main reason for not having a bank account")]:
        base = F[F[q].notna()]
        for seg, sub in [("All adults", base)] + list(base.groupby("farm_status")):
            rows = []
            for code, lab in labels(fm, q).items():
                r = wprop(sub[q] == code, sub.weight, None, sub.stratum)
                rows.append(dict(question=q, question_label=title, segment=seg, code=code,
                                 category=lab.replace("?", "'"), **r))
            frames.append(pd.DataFrame(rows))
    flag(pd.concat(frames, ignore_index=True)).to_csv(OUT / "fs_barriers.csv", index=False)

    # ------------------------------------------------------ validation
    an = pd.read_csv(OUT / "ahs_national.csv").set_index("indicator").est
    fn = pd.read_csv(OUT / "fs_national.csv").set_index("indicator").est
    sl = src.set_index("code").est
    val = pd.DataFrame([
        ("AHS", "Household has bank/SACCO/MFI account", an.acct_formal, 62.7, "AHS 2024 Main Report, Table 32"),
        ("AHS", "Household requested a loan", an.loan_any, 71.1, "AHS 2024 Main Report, Table 34"),
        ("AHS", "Loans from tontines (share of loans)", sl[5], 58.1, "AHS 2024 Main Report, Table 35"),
        ("AHS", "Loans from relatives/friends", sl[3], 25.1, "AHS 2024 Main Report, Table 35"),
        ("AHS", "Loans from commercial banks", sl[2], 6.4, "AHS 2024 Main Report, Table 35"),
        ("AHS", "Loans from SACCOs", sl[4], 6.0, "AHS 2024 Main Report, Table 35"),
        ("AHS", "Cooperative membership", an.coop, 11.8, "AHS 2024 Main Report, Table 30"),
        ("FinScope", "Registered mobile-money users", fn.momo_registered, 77.0, "FinScope 2024 Report"),
        ("FinScope", "Bank account in own name", fn.bank_acct, 22.0, "FinScope 2024 (banked strand)"),
        ("FinScope", "Formal saving", fn.formal_saving, 59.0, "FinScope 2024 savings strand"),
        ("FinScope", "Formal credit", fn.formal_credit, 24.0, "FinScope 2024 credit strand"),
        ("FinScope", "Insured", fn.insured, 27.0, "FinScope 2024 insurance strand"),
    ], columns=["dataset", "indicator", "ours", "published", "source"])
    val["difference"] = (val.ours - val.published).round(1)
    val["status"] = pd.cut(val.difference.abs(), [-1, 1, 3, 100], labels=["match", "close", "definition differs"])
    val.to_csv(OUT / "validation.csv", index=False)

    meta = dict(built=str(date.today()), ahs_households=int(len(H)), ahs_psu=int(H.clust.nunique()),
                ahs_weighted_households=round(float(H.weight.sum())),
                finscope_adults=int(len(F)), finscope_weighted_adults=round(float(F.weight.sum())),
                min_n=MIN_N)
    (OUT / "meta.json").write_text(json.dumps(meta, indent=2))
    print(val.to_string(index=False))
    print("\nWrote:", sorted(p.name for p in OUT.iterdir()))


if __name__ == "__main__":
    main()
