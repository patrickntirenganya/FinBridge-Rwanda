"""Deliverable 2: verified variable inventory. Missingness/dtype computed from the files."""
import pandas as pd
from pathlib import Path
import sys; sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from src.load import finscope, ahs
fs = finscope()[0]
A = lambda k: ahs(k)[0]
V = [  # (dataset, file-key, var, meaning, analytical use, limitations)
 ("FinScope","","pop_wt","Person weight, adults 16+ (sums to 8.156M)","All population estimates","No PSU/strata in public file: SEs understated"),
 ("FinScope","","a1","Province","Province comparisons","—"),
 ("FinScope","","a2","District (30)","District estimates with CIs; implicit stratum","~466 resp/district avg; no league tables"),
 ("FinScope","","a6","Urban/rural","Group comparison","—"),
 ("FinScope","","b1","Respondent age","Demographic segmentation","—"),
 ("FinScope","","b2","Respondent sex","Gender gap analysis","—"),
 ("FinScope","","c4a","Respondent highest education","Segmentation / control","—"),
 ("FinScope","","c13a","Ubudehe category","Socio-economic proxy","Self-reported; 'don't know' code 99"),
 ("FinScope","","m1","Household farming status (only farming / farming+other / none)","Defines farmer segment","Household-level, reported by individual"),
 ("FinScope","","m5a_10","Uses formal loans to finance farm inputs","Agri-finance source","Asked of farming households only"),
 ("FinScope","","m9_3","Barrier to commercialising farm: no collateral","Agri barrier","Asked only of those who considered commercialising"),
 ("FinScope","","k1","Has bank account in own name","Banked indicator (20.2% vs published 22%)","Published strand uses wider definition"),
 ("FinScope","","k17","Main reason no bank account","Barrier analysis","Single main reason"),
 ("FinScope","","f5","Mobile-money registration/usage status","Registered MoMo = codes 3,4,6 (76.2%; published 77%)","—"),
 ("FinScope","","h3_01–h3_18","Borrowing sources past 12 months","Formal/informal credit (transparent definition)","Formal credit 13.3% vs published 24%: official strand definition not public"),
 ("FinScope","","h7","Main reason not borrowed","Credit barrier analysis","Non-borrowers only"),
 ("FinScope","","h8a/h8b","Refused a loan; reason","Supply-side barrier","Very small n per institution"),
 ("FinScope","","i4a / i6_12","Micro-insurance; agricultural insurance","Insurance uptake","Rare outcome"),
 ("FinScope","","i7","Main reason no insurance","Barrier","—"),
 ("FinScope","","g11a","Contributes to pension fund","Long-term savings","—"),
 ("FinScope","","e9b / e9c","Emergency fund; ability to raise 56,000 Rwf in a month","Resilience","Self-reported"),
 ("FinScope","","n1a_6 / n1b","Income from farming; main income source","Livelihood segmentation","—"),
 ("FinScope","","cc7_*","Plans to cope with climate shocks","Climate-finance gap","—"),
 ("AHS","Section0","weight","Household weight, Season A (sums to 2.164M ag. households)","All AHS estimates","—"),
 ("AHS","Section0","clust","Cluster / EA (581 PSUs)","Design-based variance; grouped CV","—"),
 ("AHS","Section0","district","District (30)","Implicit stratum; district estimates","~124 HH and ~19 PSUs per district: wide CIs"),
 ("AHS","Section0","s0q14","Main livelihood = agriculture (88.4%)","Segmentation","—"),
 ("AHS","Saving","s10q5","Account institution: bank / MFI / SACCO","Formal account (62.7%, matches report)","Person-account rows; aggregated to household"),
 ("AHS","Saving","s10cq8","Participates in tontine","Informal savings","—"),
 ("AHS","Credits","loan","Any member requested a loan (71.1%, matches report)","Credit demand","Household flag"),
 ("AHS","Credits","s10q6","Source of loan","Formal vs informal credit (loan shares match report)","—"),
 ("AHS","Credits","s10aq7","Main purpose of loan","Agri vs consumption credit","—"),
 ("AHS","Credits","s10aq1 / s10aq2","Loan denial; main denial reason","Supply-side barrier","Label ambiguous; n=295 denial rows: wide CIs"),
 ("AHS","Section2","s2q7","Plot in titled parcel","Collateral potential","19% missing (non-owned plots skip)"),
 ("AHS","Section2","s2q8","Members with right to use land as loan guarantee","Collateral right","Coded member list; '99' = none"),
 ("AHS","Section2","total_agr_land","Agricultural land per household (ha)","Farm size","25% missing at plot level"),
 ("AHS","Section2","quintile","Real consumption quintile per adult equivalent (EICV7)","Welfare gradient","Inherited from EICV7"),
 ("AHS","Section2","pov_jan / epov_jan","Poor / extremely poor","Vulnerability","Inherited from EICV7"),
 ("AHS","Section6","s6q10","Member of agricultural cooperative (11.8%, matches report)","Association with credit","—"),
 ("AHS","Section6","s6q8 / s6q9","Crop / livestock insurance this season","Insurance uptake","Rare (1.7% crop)"),
 ("AHS","Section6","s6q1 = 11","Received financial-literacy extension","Programme exposure","—"),
 ("AHS","Section1_","s1q1 / s1q2","Sex; relation to head","Female-headed household flag","—"),
 ("AHS","Section1_","s4bq4 / s4bq7","Can read; can do written calculation","Capability","24% missing (age-skipped)"),
 ("AHS","Section1_","s4bq23c","Uses mobile financial services","Digital readiness","92% missing (asked of internet/phone users)"),
]
rows = []
for ds, fk, var, mean, use, lim in V:
    d = fs if ds == "FinScope" else A(fk)
    first = var.split(" ")[0].split("/")[0].split("–")[0].strip()
    if first in d.columns:
        miss = f"{100*d[first].isna().mean():.1f}%"; dt = str(d[first].dtype); ok = "yes"
    else:
        miss = dt = "see family"; ok = "family" if any(c.startswith(first.split("_")[0]) for c in d.columns) else "NOT FOUND"
    rows.append(dict(variable=var, meaning=mean, dataset=ds + (f" ({fk.rstrip('_')})" if fk else ""),
                     data_type=dt, missingness=miss, analytical_use=use, limitations=lim, verified_in_file=ok))
out = pd.DataFrame(rows); out.to_csv(Path(__file__).resolve().parents[1] / "docs/variable_inventory.csv", index=False)
print(out[["variable", "dataset", "data_type", "missingness", "verified_in_file"]].to_string(index=False))
