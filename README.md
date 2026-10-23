# FinBridge Insights

**Half of Rwanda's farm households have a formal account but no formal loan.** FinBridge Insights uses NISR's Agricultural Household Survey 2024 and FinScope Rwanda 2024 to show where agricultural households are banked but not financed, who is left out, and why.

> Work in progress for the NISR 2026 Big Data Hackathon. The full README (methods, limitations, references, demo) is on the backlog in `CLAUDE.md`.

## Data

Both datasets are NISR public-use microdata and are **not** redistributed in this repository. Download them after registering on the NISR Microdata Portal:

| Dataset | Catalogue | Place file at |
|---|---|---|
| FinScope Rwanda 2024 (RWA-NISR-FINSCOPE-2024-v01) | https://microdata.statistics.gov.rw/index.php/catalog/120 | `data/raw/FinScope_2024_Rwanda.dta` |
| Agricultural Household Survey 2024 (RWA-NISR-RAHS-2024-V0.1) | https://microdata.statistics.gov.rw/index.php/catalog/123 | `data/raw/Microdata.zip` |

The aggregate tables the app uses (`data/aggregates/`, ~150 KB, no respondent-level data) are committed, so the app runs without the raw files.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                 # uses committed aggregates
```

To rebuild the aggregates from the raw microdata and test every page:

```bash
pip install -r requirements-pipeline.txt
python pipeline/build_aggregates.py
python tests/test_app.py
```

## Two parts

**For farmers.** *My farm records* lets a farmer record harvests, sales, expenses and savings, see a
seasonal summary with the formulas shown, and download a one-page report to share with a lender by choice.
Records stay in the browser session; a JSON backup lets the farmer reload them. A USSD simulator shows the
same tool on a basic phone, because only 13.5% of farming adults own a smartphone. Entries are labelled
self-reported unless the farmer holds a receipt. The tool never scores a farmer or recommends a loan.

**For lenders and policy.** The evidence layer below, plus *Why a record tool* (what the data do and do not
support) and *Adjusted associations* (weighted logistic models, associations only).

## What the evidence layer shows

Overview of the account-to-credit gap; who gets formal credit (by welfare quintile, poverty, head's sex, farm size, land title, cooperative membership, province); what loans are for and why they are refused; how farming adults compare with other adults; district patterns with confidence intervals; and data, methods and validation against NISR's published figures.

## Responsible use

All estimates are survey-weighted with 95% confidence intervals. Small cells (n < 30) are suppressed. The tool describes groups of households; it does not score individuals or make lending decisions.
