"""Indicator definitions: the single source of truth.

Every definition here is documented in docs/01_dataset_audit.md and in the
app's Methods page. Change a definition here and nowhere else.
"""
from __future__ import annotations
import numpy as np
import pandas as pd
from .load import finscope, ahs, labels

# ----------------------------------------------------------------- FinScope
FS_INDICATORS = {
    "bank_acct": "Bank account in own name",
    "momo_registered": "Registered mobile-money user",
    "formal_saving": "Saves with a formal provider",
    "formal_credit": "Borrowed from a formal provider (past 12 months)",
    "formal_credit_ex_govt": "Formal credit, excluding Government (Ubudehe/VUP) loans",
    "govt_loan": "Got a Government (Ubudehe credit scheme / VUP) loan",
    "informal_credit": "Borrowed from an informal source (past 12 months)",
    "insured": "Holds any insurance (excl. RSSB/pension)",
    "emergency_fund": "Has an emergency fund",
    "own_phone": "Owns a mobile phone",
    "smartphone": "Owns a smartphone",
    "tracks_money": "Always keeps track of money received and spent",
    "budgets": "Always budgets",
}

FS_GROUPS = {
    "farm_status": "Household farming status",
    "sex": "Sex",
    "age_band": "Age group",
    "education": "Education",
    "area": "Urban / rural",
    "ubudehe": "Ubudehe category",
    "vup": "Household got a VUP direct cash transfer",
    "ubudehe_1": "Ubudehe category 1 or not",
    "province": "Province",
    "district": "District",
}

# Farming adults = FinScope m1 in (1, 2). Used for the farmer-focused tables.
FS_FARMER_GROUPS = {
    "sex": "Sex",
    "age_band": "Age group",
    "education": "Education",
    "province": "Province",
    "ubudehe": "Ubudehe category",
}


def _yes(df, cols):
    out = pd.Series(False, index=df.index)
    for c in cols:
        out |= pd.to_numeric(df[c], errors="coerce") == 1
    return out


def build_finscope() -> pd.DataFrame:
    """One row per adult (16+). Weight: pop_wt. No PSU in public file."""
    df, m = finscope()
    h = lambda *n: [f"h3_{i:02d}" for i in n]
    out = pd.DataFrame({
        "weight": df.pop_wt,
        "stratum": df.a2,
        "bank_acct": df.k1 == 1,
        "momo_registered": df.f5.isin([3, 4, 6]),
        # bank, MFI, MoMo, education insurance, Ejo Heza, RNIT, private pension, SACCO, capital market, pension fund
        "formal_saving": _yes(df, [f"g3a_{i:02d}" for i in range(1, 11)]),
        # bank, digital, MFI, NDFI, MoKash, SACCO, government (VUP/Ubudehe), employer, guarantee fund
        "formal_credit": _yes(df, h(1, 2, 3, 4, 5, 6, 7, 8, 16)),
        "formal_credit_ex_govt": _yes(df, h(1, 2, 3, 4, 5, 6, 8, 16)),
        "govt_loan": _yes(df, h(7)),
        # savings group, money lender, agri buyer, church, shop credit, other
        "informal_credit": _yes(df, h(9, 10, 11, 12, 15, 17)),
        "insured": (df.i4a == 1) | _yes(df, [f"i6_{i:02d}" for i in range(1, 13)]),
        "emergency_fund": df.e9b == 1,
        "own_phone": df.f3 == 1,
        "smartphone": df.f4d_1 == 1,
        # e15_* were put to about half of respondents; leave unasked as missing so
        # estimates use only those who answered
        "tracks_money": (df.e15_11 == 1).where(df.e15_11.notna()),
        "budgets": (df.e15_9 == 1).where(df.e15_9.notna()),
    })
    out["track_level"] = df.e15_11.map({1: "Always", 2: "Sometimes", 3: "Never"})
    out["farm_status"] = df.m1.map({1: "Farming only", 2: "Farming + other work", 3: "Not farming"})
    out["sex"] = df.b2.map({1: "Male", 2: "Female"})
    out["age_band"] = pd.cut(df.b1, [15, 17, 30, 45, 60, 200],
                             labels=["16–17", "18–30", "31–45", "46–60", "61+"]).astype(str)
    out["education"] = df.c4a.map({1: "No formal education", 2: "Primary", 3: "Primary",
                                   4: "Secondary", 5: "Secondary", 6: "University / higher",
                                   7: "Vocational"})
    out["area"] = df.a6.map({1: "Urban", 2: "Rural"})
    out["ubudehe"] = df.c13a.map({1: "Category 1", 2: "Category 2", 3: "Category 3",
                                  4: "Category 4", 5: "Not yet classified"})
    out["vup"] = df.c13d.map({1: "Received VUP cash transfer", 2: "Did not receive one"})    # 99 = don't know -> excluded
    out["ubudehe_1"] = df.c13a.map({1: "Ubudehe category 1", 2: "Other categories", 3: "Other categories",
                                    4: "Other categories", 5: "Other categories"})
    out["province"] = df.a1.map(labels(m, "a1"))
    out["district"] = df.a2.map(labels(m, "a2"))
    # raw barrier codes kept for barrier tables
    out["h7"] = pd.to_numeric(df.h7, errors="coerce")
    out["k17"] = pd.to_numeric(df.k17, errors="coerce")
    return out


# ---------------------------------------------------------------------- AHS
AHS_INDICATORS = {
    "acct_formal": "Has a bank, SACCO or MFI account",
    "acct_sacco": "Has a SACCO account",
    "loan_any": "Requested any loan",
    "loan_tontine": "Has a tontine loan",
    "loan_formal": "Has a formal loan (bank, SACCO, MFI)",
    "banked_not_financed": "Formal account but no formal loan",
    "denied": "Reported a loan denial",
    "coop": "Member of an agricultural cooperative",
    "crop_ins": "Took crop insurance this season",
    "land_title": "Owns titled land",
    "tontine_member": "Any household member takes part in a tontine",
}

# F2 tontine bridge: (indicator column, label, base column that defines who is counted, base label)
TONTINE_BRIDGE = [
    ("tontine_member", "Household has a tontine member", None, "All agricultural households"),
    ("acct_sacco", "Holds a SACCO account", "loan_tontine", "Households that borrowed from a tontine"),
    ("farm_loan", "Borrowed for a farm purpose (inputs, equipment or livestock)", "informal_only_saver",
     "Households with an account that borrowed only informally"),
]

AHS_GROUPS = {
    "quintile": "Consumption quintile (EICV7)",
    "poverty": "Poverty status (EICV7)",
    "head_sex": "Sex of household head",
    "coop_member": "Cooperative membership",
    "titled": "Land title",
    "farm_size": "Farm size",
    "province": "Province",
    "district": "District",
}

FORMAL_LOAN_SOURCES = [2, 4, 6]       # commercial bank, SACCO, microfinance
AGRI_PURPOSES = [1, 2, 9]             # equipment, inputs, livestock


def build_ahs():
    """Return (households, loans, denials). Weight: weight; PSU: clust; stratum: district."""
    h0, m0 = ahs("Section0")
    sv, _ = ahs("Saving")
    cr, _ = ahs("Credits")
    s1, _ = ahs("Section1_")
    s2, _ = ahs("Section2")
    s6, _ = ahs("Section6")

    H = h0[["hhid", "clust", "district", "province", "weight"]].copy()
    inst = sv[sv.s10q5.isin([1, 2, 3])]
    H["acct_formal"] = H.hhid.isin(inst.hhid)
    H["acct_sacco"] = H.hhid.isin(inst.loc[inst.s10q5 == 3, "hhid"])

    loans = cr[cr.s10q6.notna()].drop(columns="clust")
    H["loan_any"] = H.hhid.isin(cr.loc[cr.loan == 1, "hhid"])
    H["loan_formal"] = H.hhid.isin(loans.loc[loans.s10q6.isin(FORMAL_LOAN_SOURCES), "hhid"])
    H["loan_tontine"] = H.hhid.isin(loans.loc[loans.s10q6 == 5, "hhid"])
    H["banked_not_financed"] = H.acct_formal & ~H.loan_formal
    H["tontine_member"] = H.hhid.isin(sv.loc[sv.s10cq8 == 1, "hhid"])
    H["informal_only_saver"] = H.acct_formal & H.loan_any & ~H.loan_formal
    H["farm_loan"] = H.hhid.isin(loans.loc[loans.s10aq7.isin(AGRI_PURPOSES), "hhid"])
    # s10aq1 is labelled "tried to obtain a loan" but every "yes" carries a denial reason
    H["denied"] = H.hhid.isin(cr.loc[cr.s10aq1 == 1, "hhid"])

    own = s2[s2.s2q4.isin([1, 2, 3])]
    H["land_title"] = H.hhid.isin(own.loc[own.s2q7 == 1, "hhid"])
    hh2 = s2.groupby("hhid").agg(q=("quintile", "first"), poor=("pov_jan", "first"),
                                 land_ha=("total_agr_land", "first"))
    H = H.merge(hh2, on="hhid", how="left")
    p6 = s6.groupby("hhid").agg(c=("s6q10", "first"), ci=("s6q8", "first"))
    H = H.merge(p6, on="hhid", how="left")
    H["coop"] = H.pop("c") == 1
    H["crop_ins"] = H.pop("ci") == 1
    head = s1[s1.s1q2 == 1].groupby("hhid").s1q1.first().rename("head_sex_code")
    H = H.merge(head, on="hhid", how="left")

    # grouping columns (readable labels)
    H["quintile"] = H.q.map({1: "Q1 (poorest)", 2: "Q2", 3: "Q3", 4: "Q4", 5: "Q5 (richest)"})
    H["poverty"] = H.poor.map({0: "Not poor", 1: "Poor"})
    H["head_sex"] = H.head_sex_code.map({1: "Male-headed", 2: "Female-headed"})
    H["coop_member"] = np.where(H.coop, "Cooperative member", "Not a member")
    H["titled"] = np.where(H.land_title, "Has titled land", "No titled land")
    H["farm_size"] = pd.cut(H.land_ha, [-0.001, 0.1, 0.3, 1.0, 1e9],
                            labels=["< 0.1 ha", "0.1–0.3 ha", "0.3–1 ha", "> 1 ha"]).astype(str)
    H.loc[H.land_ha.isna(), "farm_size"] = np.nan
    H["province"] = H.province.map(labels(m0, "province"))
    H["district_name"] = H.district.map(labels(m0, "district"))

    L = loans.merge(H[["hhid", "weight", "clust", "district"]], on="hhid")
    D = cr[cr.s10aq1 == 1].drop(columns="clust").merge(H[["hhid", "weight", "clust", "district"]], on="hhid")
    return H, L, D
