# FinBridge Insights

**Banked but not financed.** Half of Rwanda's farm households have a formal account but no formal loan.
FinBridge Insights combines NISR's Agricultural Household Survey 2024 (AHS) and FinScope Rwanda 2024 to show
where agricultural households are banked but not financed, who is left out, and why. It also gives farmers a
record-keeping tool (web and USSD) that builds the paper trail lenders say they lack.

Entry for the NISR 2026 Big Data Hackathon. Alignment: NST2 (agricultural transformation, financial
inclusion) and Vision 2050.

- **App:** _add Streamlit Cloud link here after deploy_
- **Demo video (≤ 3 min):** _add link here_
- **Data:** aggregate tables in [`data/aggregates/`](data/aggregates) (no respondent-level data); raw microdata
  from the NISR portal (see below)

## The problem

Among Rwanda's 2.16 M agricultural households (AHS 2024):

| Finding | Estimate |
|---|---|
| Have a bank, SACCO or MFI account | 62.7% |
| Have a formal loan | 14.1% |
| Account but no formal loan | 50.2% (95% CI 48.1–52.4) |
| Account, borrowed only informally (mostly tontines) | 35.1%, about 759k households |
| Formal loan, poorest vs richest quintile | 10.8% vs 23.9% |
| Formal loan, female- vs male-headed | 7.8% vs 16.3% |
| Formal loan, < 0.1 ha vs > 1 ha | 9.8% vs 25.3% |
| Farm-input loans from formal lenders | 10.8% |
| Loans taken for food | 29.4% |

FinScope (adults): formal credit reaches 8.5% of adults in farming-only households vs 19.8% in non-farming
households. Regenerate every figure with `python analysis/key_findings.py`; the app reads them from
`data/aggregates/` and no statistic is typed into the interface.

## What we built

**For farmers**
- *My farm records*: record harvests, sales, expenses and savings; a seasonal summary with the formulas
  shown; a downloadable report the farmer can share with a lender by choice; JSON backup. Nothing is stored
  server-side.
- *USSD simulator*: the same tool on a basic phone. Only 13.5% of farming adults own a smartphone, against
  64.2% with any phone and 73.8% using mobile money, so USSD is first-class. Screens are ≤ 160 characters.
- Kinyarwanda and English interface (Kinyarwanda strings need native-speaker review before real use).

**Evidence for lenders and policy**
- *Overview*, *Who gets formal credit*, *Why people don't borrow formally*, *Farmers vs other adults*,
  *Districts* (confidence intervals plus choropleth).
- *Why a record tool*: what the data do and do not support.
- *Adjusted associations*: survey-weighted logistic models, shown as odds ratios with CIs.
- *What to do*: recommendations, each tied to one finding and marked evidence-backed or hypothesis.
- *Methods*: sources, weights, validation against NISR's published tables.

## Methods

- **Weights and design.** AHS: weight `weight`, PSU `clust`, stratum `district`, with Taylor-linearised CIs
  (`src/survey.py`). FinScope: weight `pop_wt`; the public file has no PSU, so **FinScope CIs are
  understated**.
- **Suppression.** Cells with n < 30 are suppressed; CV > 0.30 is flagged "caution" (ochre bars, greyed on
  the map).
- **Indicators** are defined once in `src/indicators.py`; `pipeline/build_aggregates.py` turns microdata
  into the committed aggregates.
- **Models.** Weighted logistic regression of formal loan on welfare quintile, head's sex, farm size, land
  title, cooperative membership and province, with design-based sandwich SEs (`src/models.py`). These are
  associations, not causes.
- **No record linkage** between AHS and FinScope; they are compared side by side as aggregates only.
- **Validation.** AHS estimates reproduce NISR's published tables exactly
  ([`validation.csv`](data/aggregates/validation.csv)). FinScope mobile money (76.2 vs 77) and bank account
  (20.2 vs 22) reconcile; our formal saving, credit and insurance are lower than the official strands
  because the official strand code is not public, so FinScope is used for group comparisons, not national
  totals.

## Limitations

- Survey data are cross-sectional; nothing here shows that records or credit cause better outcomes.
- AHS `s10aq1` is labelled "tried to obtain a loan" but every yes has a denial reason, so it is treated as
  "reported a denial" (n = 295, wide CIs).
- The AHS milk, egg and honey files contain many exact duplicate rows and are not used.
- 55% of farming adults say they always track money; the question went to about half of respondents and
  estimates use answerers only.
- Record-tool entries are self-reported unless the farmer says a receipt is held. `confirmed` evidence is
  reserved for a future verifier and import files can never grant it.
- We claim **no impact on loan approval** without a pilot.

## Responsible use

The tool describes groups of households. It does not score individuals, predict default or make lending
decisions, and it never will in this design. Small cells are suppressed and associations are labelled as such.

## Data

Both datasets are NISR public-use microdata and are **not** redistributed here. Download after registering on
the NISR Microdata Portal:

| Dataset | Catalogue | Place file at |
|---|---|---|
| FinScope Rwanda 2024 (RWA-NISR-FINSCOPE-2024-v01) | https://microdata.statistics.gov.rw/index.php/catalog/120 | `data/raw/FinScope_2024_Rwanda.dta` |
| Agricultural Household Survey 2024 (RWA-NISR-RAHS-2024-V0.1) | https://microdata.statistics.gov.rw/index.php/catalog/123 | `data/raw/Microdata.zip` |

District boundaries: geoBoundaries ADM2 Rwanda, CC BY 4.0 (see [`data/geo/README.md`](data/geo/README.md)).

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                 # uses committed aggregates
```

Rebuild the aggregates from raw microdata and test every page:

```bash
pip install -r requirements-pipeline.txt
python pipeline/build_aggregates.py
python tests/test_app.py                             # must print "0 failures"
```

## Repository layout

```
src/            loaders, indicators, survey estimators, models, record engine, USSD state machine
pipeline/       microdata -> data/aggregates/*.csv
ui/, app.py     Streamlit app (theme, cached readers, pages, farmer tool)
tests/          renders every page and every selector option
analysis/       variable inventory and key-findings scripts
docs/           dataset audit report, variable inventory
```

## Next steps (not in the hackathon build)

Pilot the record tool with a SACCO and a cooperative; buyer and cooperative verification; consent-based
sharing; native-speaker review of Kinyarwanda menus; a real USSD gateway.

## References

- National Institute of Statistics of Rwanda (2024). *Agricultural Household Survey 2024*, main report and
  microdata.
- National Institute of Statistics of Rwanda, Access to Finance Rwanda (2024). *FinScope Rwanda 2024*.
- Republic of Rwanda. *National Strategy for Transformation (NST2)* and *Vision 2050*.
- Runfola et al. (2020). geoBoundaries. *PLOS ONE* 15(4): e0231866. CC BY 4.0.
