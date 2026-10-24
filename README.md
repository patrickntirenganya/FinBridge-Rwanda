# FinBridge Insights

**Banked but not financed.** Half of Rwanda's farm households have a formal account but no formal loan.
We analysed NISR's Agricultural Household Survey 2024 (AHS) and FinScope Rwanda 2024 to find where
agricultural households are banked but not financed, who is left out, and why. The product built from that
research gives farmers a record-keeping tool (web and USSD) and gives lenders a clear way to read the records
a farmer chooses to share, building the paper trail lenders say they lack.

Entry for the NISR 2026 Big Data Hackathon. Alignment: NST2 (agricultural transformation, financial
inclusion) and Vision 2050.

- **App:** _add Streamlit Cloud link here after deploy_ (the app is the product; the research is in this README)
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

The research above is the **why**. The product contains no survey data: it is the solution the research points to.

**For farmers**
- *My farm records*: record harvests, sales, expenses and savings; a seasonal summary with the formulas shown;
  a downloadable report and a JSON file the farmer can give a lender by choice. Nothing is stored server-side.
- *USSD simulator*: the same tool on a basic phone (screens ≤ 160 characters), because most farmers do not
  own a smartphone (see the research).

**For lenders (SACCO, MFI, bank, cooperative)**
- *Open a farmer's report*: open the file a farmer shared and read income, costs and savings by season, the
  detail by crop and expense, every entry, and which entries are self-reported or backed by a receipt. A
  "what to check" tab lists simple counts and questions to ask. **No score, no recommendation, no decision.**

**Throughout**: a landing page (TypeScript + Tailwind), Kinyarwanda and English (Kinyarwanda needs
native-speaker review), and an *About* page on limits and privacy.

## Run it

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                 # the product reads no survey data
```

Rebuild the research aggregates from raw microdata (not needed to run the app) and test every page:

```bash
pip install -r requirements-pipeline.txt
python pipeline/build_aggregates.py
python tests/test_app.py                             # must print "0 failures"
```

## Repository layout

```
src/            loaders, indicators, survey estimators, models, record engine, USSD state machine
pipeline/       microdata -> data/aggregates/*.csv
ui/, app.py     Streamlit app (theme, landing, farmer tool, lender view, about)
frontend/       TypeScript + Tailwind source for the landing page
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

## Landing page (TypeScript + Tailwind)

The home page is a Vite + TypeScript + Tailwind CSS bundle in `frontend/`, built into one self-contained file
(`ui/landing/landing.html`, committed so Streamlit Cloud needs no Node). `ui/landing.py` injects every number from
`data/aggregates/`. To change it: `cd frontend && npm install && npm run build`, then `python tests/test_app.py`.
Photos of Rwandan farmers are in `frontend/src/img` and `ui/assets/photos`.
