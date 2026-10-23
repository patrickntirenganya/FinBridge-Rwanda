# FinBridge Insights: project memory for Claude Code

NISR 2026 Big Data Hackathon entry. **Deadline: 30 October 2026.** Submission = public GitHub repo + deployed app link + README + demo video (≤ 3 min, screen-recorded, .webm/.gif) + data file or link.

Judging: problem relevance (NST2 / Vision 2050), data use and methodology, tangible impact, tech innovation, usability.

## The story (verified, do not change numbers by hand)

**"Banked but not financed."** Among Rwanda's 2.16 M agricultural households (AHS 2024):
- 62.7% have a bank/SACCO/MFI account, but only 14.1% have a formal loan.
- 50.2% (CI 48.1–52.4) have an account but no formal loan; 35.1% (≈759k households) have an account yet borrowed **only** informally (mostly tontines).
- Formal loans: Q1 10.8% vs Q5 23.9%; female-headed 7.8% vs male-headed 16.3%; < 0.1 ha 9.8% vs > 1 ha 25.3%.
- Only 10.8% of loans for farm inputs come from formal lenders; 29.4% of all loans are for food.
- FinScope (adults): formal credit 8.5% in farming-only households vs 19.8% in non-farming.

Regenerate with `python analysis/key_findings.py`. Never type a statistic into the UI; read it from `data/aggregates/`.

## Product (updated 23 Oct 2026)

Two layers, one app. **For farmers:** `My farm records` (record harvests, sales, expenses, savings; seasonal
summary with visible formulas; downloadable report; JSON backup, nothing stored server-side) and a
USSD simulator for basic phones. **Evidence for lenders and policy:** the dashboard, `Why a record tool`,
`Adjusted associations`, `What to do`.
Data-driven design facts (read from `data/aggregates/`, never typed): only 13.5% of farming adults own a
smartphone vs 64.2% any phone and 73.8% mobile money, so USSD is first-class; 55% of farming adults asked
say they always track money (question put to ~half of respondents; estimates use answerers only).
Rules for the record tool: entries are self-reported unless the farmer says a receipt is held; `confirmed`
evidence is reserved for a future verifier and import files can never grant it; **no score, no lending
decision, ever**; claim no impact on loan approval without a pilot.

## Architecture

```
data/raw/             NISR microdata (GITIGNORED, never commit)
src/load.py           portable loaders (Latin-1 fallback, auto-unzips AHS)
src/indicators.py     ALL indicator definitions: single source of truth
src/survey.py         weighted proportions with Taylor-linearised CIs
src/models.py         weighted logistic models, design-based sandwich SEs (associations only)
src/records.py        farmer record engine (channel-agnostic, tested)
src/ussd.py           USSD menu state machine (screens <= 160 chars)
pipeline/build_aggregates.py   microdata -> data/aggregates/*.csv (safe to commit)
ui/theme.py           palette, CSS, chart helpers (ci_bars)
ui/data.py            cached readers for aggregates
ui/pages.py           one function per evidence page
ui/farmer.py          farmer tool, USSD preview, why-records and adjusted-association pages
app.py                thin entry point (st.navigation)
tests/test_app.py     renders every page and every selector option
analysis/             inventory + key findings scripts
docs/                 audit report, variable inventory
```

Commands:
```
pip install -r requirements.txt
python pipeline/build_aggregates.py      # needs data/raw/
python tests/test_app.py                 # must print "0 failures"
streamlit run app.py
```

## Non-negotiable rules

1. **Never commit microdata** (`.dta`, `.zip`, `data/raw/`, `*.pkl`). The app reads only `data/aggregates/`.
2. **Every estimate is weighted.** AHS: weight=`weight`, PSU=`clust`, stratum=`district`. FinScope: weight=`pop_wt`, no PSU in public file, so CIs are understated; always say so.
3. Cells with n < 30 are suppressed; CV > 0.30 is flagged "caution" (ochre bars).
4. **No record linkage** between AHS and FinScope. Compare aggregates side by side only.
5. **No individual credit scores, default predictions or lending decisions.** Associations are not causes; say so on any regression output.
6. Change an indicator only in `src/indicators.py`, then rebuild aggregates and rerun tests.
7. Run `python tests/test_app.py` after every UI change.

## Data facts and known issues

- AHS reproduces NISR published tables exactly (see `data/aggregates/validation.csv`).
- FinScope: mobile money (76.2 vs 77) and bank account (20.2 vs 22) reconcile. Our formal saving (42.9 vs 59), credit (13.3 vs 24) and insurance (17.4 vs 27) are lower because the official strand code is not public. Use FinScope for **group comparisons**, not national totals.
- AHS `s10aq1` is labelled "tried to obtain a loan" but every yes has a denial reason, so it is treated as "reported a denial" (n = 295, wide CIs).
- AHS milk/egg/honey files contain thousands of exact duplicate rows; investigate before use.
- AHS Section 1 needs `encoding="latin1"` (handled in `src/load.py`).
- AHS Section 2 carries EICV7 `quintile`, `pov_jan`, `epov_jan`, `total_agr_land` (household-constant).
- FinScope barriers: `h7` (why not borrow), `k17` (why no bank account), `i7` (why no insurance), `g9` (why not save), `m9_*` (farm commercialisation barriers), `m5a_*` (how farm inputs are financed).

## Design system (ui/theme.py)

Tea green `#2F6B4F` = formal finance; sorghum ochre `#C2922A` = informal; soil red `#8E3B2E` = the gap; mist `#EEF2EC` background; grey `#9AA8A0` = government/other. Font: Atkinson Hyperlegible. Sentence case, plain verbs, no all-caps labels. Every chart shows CIs and n, and every page ends with a source note.

## Backlog (priority order)

1. DONE (models.csv). Original spec: **Adjusted associations page**: survey-weighted logistic regression for `loan_formal` on quintile, head sex, farm size, land title, cooperative, province. Use `statsmodels` GLM Binomial with `freq_weights`/`var_weights` = weight and `cov_type="cluster"`, groups = `clust`. Export odds ratios + CIs to `data/aggregates/ahs_model.csv` in the pipeline; render as a forest plot. Label clearly as association. Optionally compare with an interpretable tree model using cluster-grouped CV (GroupKFold on `clust`) and report AUC by sex and quintile.
2. **District map**: Rwanda ADM2 boundaries from geoBoundaries (raw.githubusercontent.com, CC-BY; attribute in Methods). Simplify, commit as `data/geo/rwanda_districts.geojson`, choropleth beside the CI chart, hatched/greyed where reliability is "caution".
3. DONE. Original spec: **Recommendations page**: each recommendation tied to one finding (e.g. SACCO credit products for existing savers; women-headed household targeting; input-finance products; cooperative channel). Mark which are evidence-backed vs hypotheses.
4. Full **README** (problem, data links, methods, setup, limitations), **references**, **demo script ≤ 3 min**.
5. **Deploy** on Streamlit Community Cloud from the public repo (`app.py`, Python 3.11+).
6. Polish: on the Districts page the value label sits at the upper CI limit; consider placing it at the bar end with an offset. Check mobile width.
7. Optional: attempt closer reconciliation of FinScope saving/insurance strands (pension `g11a`, `qf` product use).

## Next (after 23 Oct)
Record-tool pilot plan with a SACCO and a cooperative; buyer/cooperative verification; consent-based sharing;
Kinyarwanda menus (native-speaker review required); real USSD gateway. Not in the hackathon build.
