"""Deliverable 4: print the headline findings with CIs and sample sizes from the aggregate tables.
Run after pipeline/build_aggregates.py."""
from pathlib import Path
import pandas as pd
A = Path(__file__).resolve().parents[1] / "data" / "aggregates"
an = pd.read_csv(A / "ahs_national.csv").set_index("indicator")
bg = pd.read_csv(A / "ahs_by_group.csv")
seg = pd.read_csv(A / "ahs_segments.csv").set_index("segment")
pur = pd.read_csv(A / "ahs_loan_purpose.csv")
fb = pd.read_csv(A / "fs_by_group.csv")
f = lambda r: f"{r.est:.1f}% (95% CI {r.lo:.1f}–{r.hi:.1f}, n={int(r.n)})"
g = lambda t, ind, gv, grp: t[(t.indicator == ind) & (t.group_var == gv) & (t.group == grp)].iloc[0]
print("F1 Banked but not financed (AHS):", f(an.loc["banked_not_financed"]))
print("F2 Account, borrowed only informally (AHS):", f(seg.loc["Account, borrowed only informally"]))
print("F3 Formal loan, Q1 vs Q5:", f(g(bg, "loan_formal", "quintile", "Q1 (poorest)")), "|", f(g(bg, "loan_formal", "quintile", "Q5 (richest)")))
print("F4 Formal loan, female- vs male-headed:", f(g(bg, "loan_formal", "head_sex", "Female-headed")), "|", f(g(bg, "loan_formal", "head_sex", "Male-headed")))
print("F5 Formal loan, <0.1 ha vs >1 ha:", f(g(bg, "loan_formal", "farm_size", "< 0.1 ha")), "|", f(g(bg, "loan_formal", "farm_size", "> 1 ha")))
agri = pur[pur.agri_purpose]
print("F6 Formal share of loans for inputs/equipment/livestock:", agri[["category", "formal_source_pct"]].to_dict("records"))
print("F7 FinScope formal credit, farming-only vs not farming:", f(g(fb, "formal_credit", "farm_status", "Farming only")), "|", f(g(fb, "formal_credit", "farm_status", "Not farming")))
