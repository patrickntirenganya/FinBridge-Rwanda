# FinBridge

**Farm records that farmers own and lenders can read.**

Most of Rwanda's farming households have a bank, SACCO or microfinance account, yet only a small share hold a
formal loan. Lenders say they cannot see a farm's income, and farmers have nothing to show them. FinBridge closes
that gap: a farmer keeps simple records on any phone, locks them with a PIN, and chooses to share them with a lender
who reads them as a plain story with charts. The tool never scores anyone and never decides a loan.

Built for the **NISR 2026 Big Data Hackathon**. The design follows from our analysis of NISR's Agricultural Household
Survey 2024 and FinScope Rwanda 2024. It supports **NST2** (agricultural transformation, financial inclusion) and
**Vision 2050**.

| | |
|---|---|
| **Live app** | _add the Streamlit Cloud link here after deploying_ |
| **Demo video (≤ 3 min)** | _add the link here_ |
| **Source code** | https://github.com/patrickntirenganya/FinBridge-Rwanda |
| **Security note** | [`docs/security.md`](docs/security.md) |
| **Demo script** | [`docs/demo_script.md`](docs/demo_script.md) |
| **Research data** | aggregate tables in [`data/aggregates/`](data/aggregates) (no respondent-level data) |

> **One rule shapes everything.** The product shows **no survey statistics**, and it gives **no score, no default
> prediction and no lending decision**. The research is the *why* and lives in this README; the app is the
> *solution*.

## Contents

1. [The problem](#1-the-problem)
2. [From research to product](#2-from-research-to-product)
3. [What the product does](#3-what-the-product-does)
4. [Security and privacy](#4-security-and-privacy)
5. [Architecture](#5-architecture)
6. [Research data and methods](#6-research-data-and-methods)
7. [Limitations and responsible use](#7-limitations-and-responsible-use)
8. [Run it locally](#8-run-it-locally)
9. [Test it](#9-test-it)
10. [Deploy it](#10-deploy-it)
11. [How this meets the judging criteria](#11-how-this-meets-the-judging-criteria)
12. [Roadmap](#12-roadmap)
13. [Repository layout](#13-repository-layout)
14. [Credits, licences and references](#14-credits-licences-and-references)

---

## 1. The problem

Among Rwanda's **2.16 million agricultural households** (AHS 2024, survey-weighted):

| Finding | Estimate |
|---|---|
| Have a bank, SACCO or MFI account | **62.7%** |
| Have a formal loan | **14.1%** |
| Have an account but **no** formal loan ("banked but not financed") | **50.2%** (95% CI 48.1–52.4) |
| Have an account yet borrowed **only** informally, mostly through tontines | 35.1%, about 759,000 households |
| Formal loan, poorest vs richest consumption quintile | 10.8% vs 23.9% |
| Formal loan, female- vs male-headed households | 7.8% vs 16.3% |
| Formal loan, under 0.1 ha vs over 1 ha of land | 9.8% vs 25.3% |
| Loans for farm inputs that come from formal lenders | 10.8% |
| Loans taken to buy food | 29.4% |

FinScope Rwanda 2024 (adults): formal credit reaches **8.5%** of adults in farming-only households against **19.8%**
in non-farming households. About **13.5%** of farming adults own a smartphone, while **64.2%** own a phone of any kind
and **73.8%** are registered mobile-money users.

Every figure above is reproduced by `python analysis/key_findings.py` from the committed aggregate tables, and the
AHS estimates match NISR's published tables ([validation](#validation)).

**What it means.** Farmers are already inside the financial system but cannot turn that into credit. Lenders cannot
judge a farm they cannot see, so most borrowing stays informal and small. The missing piece is a record a lender can
read, one that works for people with basic phones and little digital experience.

## 2. From research to product

Each design choice traces back to a finding. We mark which links are direct responses and which are hypotheses that
need a field pilot.

| What the research found | What we built | Status |
|---|---|---|
| Most farm households have an account, few have a formal loan, and lenders lack records they can read | Farm records the farmer owns, plus a lender view that turns them into a plain story and charts | Direct response |
| Only a minority of farming adults own a smartphone; most own any phone and use mobile money | USSD route for basic phones, big tap buttons, Kinyarwanda first, no email or password | Direct response |
| Most borrowing is informal (tontines, relatives), so lenders cannot see cash flow | Month-by-month money in and out, cumulative cash, and prompts to ask about other loans | Direct response |
| Loans for farm inputs rarely come from formal lenders | Input costs (seed, fertiliser, labour) recorded by category so an input-finance lender can see them | Hypothesis, needs a pilot |
| Female-headed and smallest households have lower formal-loan rates | A free, phone-first tool with no individual score, so it adds no new hurdle | Hypothesis, needs a pilot |
| About half of farming adults say they already track money | Make tracking a one-minute tap flow instead of a new habit | Design assumption |

The adjusted models below show the gaps are not just a side effect of wealth or land. They are **associations, not
causes**.

| Formal loan, odds ratio (AHS, survey-weighted logistic, n = 3,717) | OR | 95% CI |
|---|---|---|
| Female-headed vs male-headed household | 0.43 | 0.32–0.57 |
| Richest vs poorest quintile | 2.87 | 1.91–4.30 |
| Over 1 ha vs under 0.1 ha | 2.39 | 1.40–4.07 |
| Has titled land vs none | 1.47 | 1.04–2.08 |
| Cooperative member vs not | 1.28 | 0.93–1.76 (not clear) |

## 3. What the product does

```mermaid
flowchart LR
    A[Farmer records<br/>harvest, sale, cost, saving] --> B[(Encrypted vault<br/>in the farmer's browser)]
    B --> C[Plain summary<br/>with visible formulas]
    B --> D[Share: locked file<br/>+ one-time code]
    D --> E[Lender opens it<br/>with the code]
    E --> F[Story, charts,<br/>repayment worksheet]
    F --> G{{Lender decides.<br/>The tool never does.}}
```

### 3.1 For farmers

**Sign in with a phone number and a PIN.** No email, no password, no account on our server.
- The PIN is 4 to 6 digits and must not be trivial (no `1111`, no `1234`, no end of the phone number).
- Records are encrypted with a key derived from the PIN and stored in the farmer's own browser. A locked backup file
  (`.fbvault`) restores them on another phone.
- After four wrong tries the app makes the farmer wait (30 seconds, doubling up to 15 minutes). After 15 idle
  minutes it locks itself.
- **Try the demo** lets anyone look around with invented records, with nothing saved.

**Record in three taps.**

| Step | What the farmer does |
|---|---|
| 1. What happened? | Tap *I harvested*, *I sold*, *I spent* or *I saved* |
| 2. Which crop or cost? | Tap a picture button (maize, beans, potato, cassava, sorghum, rice, banana, coffee, tea, vegetables, milk, other; or seed, fertiliser, pesticide, labour, transport, equipment, land rent, loan repayment, other) |
| 3. How much? | Type the amount in RWF (and the quantity for harvests and sales) |

Date, buyer or seller, unit and "I have a receipt or mobile-money message" are tucked under *More details*. A
confirmation sentence follows, such as "Saved: you sold Maize for 50,000 RWF."

**Read a plain-language summary.** For the chosen season: *"Between these dates you sold X, spent Y, and have Z left."*
Under that sit four figures, a monthly money-in and money-out chart, and a *detailed figures* section with the formula,
average price per kg and share of harvest sold. Seasons follow Rwanda's calendar: **A** (Sep–Jan), **B** (Feb–Jun),
**C** (Jul–Aug).

**Share only what they choose.** The *Share* tab creates a locked `.fbshare` file and a random code such as
`P4G4-NSFG-VXEP`:

| Farmer's choice | Default |
|---|---|
| Which period (all dates or one season) | all |
| Include names of buyers and sellers | **off** |
| Include the farmer's own name | on |
| How long the share stays open | 7 days (1, 7 or 30) |

The farmer gives the lender the file and tells them the code separately, in person or by phone. A plain HTML report
and a CSV are also available for printing.

**Use a basic phone.** The *USSD preview* is a working simulation of the same tool on a feature phone. Every screen
is 160 characters or fewer and uses the same record engine as the web page.

```
FinBridge
1 Record sale
2 Record expense
3 Record harvest
4 Record saving
5 My summary
0 Exit
```

### 3.2 For lenders (SACCOs, MFIs, banks, cooperatives)

No account is needed. The lender opens the locked file with the farmer's code and optionally types their institution
name, which appears only on their own access receipt.

| Tab | What the lender sees |
|---|---|
| **At a glance** | A *"What the records say"* story of plain facts (period covered, totals, main income source, biggest cost, months with sales, savings, share backed by receipts), four key figures, monthly money in and out, cumulative cash, where income came from, where money went, price per kg and share of harvest sold |
| **Repayment worksheet** | The lender types a loan amount, term and interest. The sheet shows the monthly repayment, the farmer's recorded net for each month against that line, and how many months covered it. It is arithmetic on figures the lender sets. It gives **no verdict**, and a *"read this with care"* box lists the caveats |
| **Record quality** | Months with entries, how entries are backed (the farmer's own word or a receipt or message), simple counts, and questions the lender may ask |
| **All entries** | Every record with its evidence type |

The monthly repayment uses the standard level-payment formula, `P·r / (1 − (1 + r)^−n)` with `r` the monthly rate, or
`P / n` when the rate is zero.

**What the lender is told, and the farmer's records can never claim.** Every entry is *self-reported* unless the
farmer says a receipt or mobile-money message is held (and that is not checked). A third level, *confirmed by a buyer
or cooperative*, is reserved for a future verifier, and an imported file can never grant it.

### 3.3 Throughout

- **Languages.** Kinyarwanda (default) and English, switchable in the sidebar. The Kinyarwanda is a working draft that
  needs native-speaker review before field use.
- **Landing page.** A TypeScript and Tailwind page with photos of Rwandan farmers, explaining the problem, both
  user paths and the trust promises, with no statistics.
- **About page.** What the tool is and is not, privacy, evidence types, limits and a link to this research.
- **Accessible by design.** Large tap targets, plain verbs, sentence case, a font designed for legibility (Atkinson
  Hyperlegible), reduced-motion support and works down to phone width.

### 3.4 What the product deliberately does not do

- It shows no survey data.
- It gives no individual score, no default prediction and no lend or do-not-lend verdict.
- It does not verify entries or the phone number.
- It claims no effect on loan approval until it has been piloted.

## 4. Security and privacy

The design keeps farmers' data on their own device by default, asks for consent before anything is shared, and says
plainly what it cannot protect. The full threat model is in [`docs/security.md`](docs/security.md).

| Area | How it works |
|---|---|
| **Encryption** | AES-256-GCM with a fresh random nonce per save; key derived from PIN and phone number with scrypt (N = 2^16, r = 8, p = 1, 64 MB, about 0.4 s per guess) and a random salt per vault |
| **Storage** | The encrypted vault lives in browser local storage and in a downloadable backup. **Nothing is stored on a server.** Unlocked data and the key sit in session memory only while signed in and are cleared on lock, on leaving, and after 15 idle minutes |
| **Guess protection** | PIN rules, lock-out that grows to 15 minutes, identical error for wrong phone, wrong PIN or damaged file |
| **Sharing** | Locked file plus a random 12-character code (about 59 bits, no confusable letters), a chosen period and validity, buyer names off by default, rate-limited code attempts, an access receipt for the lender |
| **Untrusted input** | Every imported file is strictly parsed (known fields and types only); text from a farmer's file is HTML-escaped on the lender page |
| **Purpose binding** | A vault cannot be opened as a share and the reverse, because the purpose is bound into the ciphertext |

**Honest limits.**
- Someone who *copies* the vault can guess a short PIN offline. With slow key derivation a 4-digit PIN falls in about
  an hour of computing on one core and a 6-digit PIN in about four days. The app steers farmers to six digits and a
  private backup.
- The phone number is a label and is not verified (no SMS gateway).
- A lender who has opened a share can keep what they saw, like a printed report. The farmer is told this first.
- Lender identity and a server-side audit log need a database; they are not built.
- The prototype has **not been independently audited**.

## 5. Architecture

```mermaid
flowchart TB
    subgraph Browser["Farmer's browser"]
        UI[Streamlit pages]
        LS[(Local storage<br/>encrypted vault)]
        BR[Tiny JS bridge<br/>copies opaque strings]
        UI <--> BR <--> LS
    end
    subgraph Server["Streamlit app (session memory only)"]
        AUTH[ui/auth.py]
        REC[src/records.py<br/>record engine]
        VAULT[src/vault.py + crypto.py]
        SHARE[src/share.py]
        USSD[src/ussd.py]
        LAND[ui/landing.py]
    end
    UI --- AUTH --> VAULT
    AUTH --> REC
    UI --- USSD --> REC
    UI --- SHARE --> REC
    LAND --- LP[ui/landing/landing.html<br/>built from frontend/]
```

**Design principles.**
1. **One record engine, many channels.** `src/records.py` is channel-agnostic. The web tool, the USSD simulator, the
   report, the lender view and a future SMS channel all use it.
2. **Security code has no UI.** `src/crypto.py`, `vault.py` and `share.py` are plain, separately tested modules.
3. **Strings in one place.** All text is in `src/i18n.py` as Kinyarwanda and English pairs, with a test that checks
   every key is filled in both languages with matching placeholders.
4. **Research and product are separate.** `pipeline/` and `analysis/` produce the research tables; the app reads none
   of them, and a test fails if any `ui/` module does.

| Layer | Technology |
|---|---|
| App framework | Streamlit 1.65+ (pages, forms, `st.iframe`, Components v2 for the storage bridge) |
| Charts | Plotly |
| Landing page | TypeScript, Tailwind CSS 3, Vite, built to one self-contained HTML file |
| Cryptography | `cryptography` (AES-256-GCM, scrypt) |
| Data and tables | pandas, numpy |
| Research pipeline | pyreadstat, statsmodels, scipy (only needed to rebuild the research tables) |
| Tests | Streamlit `AppTest`, plus direct tests of the engine, crypto, vault, share and USSD |

## 6. Research data and methods

### Data

Both datasets are NISR public-use microdata and are **not** redistributed here. Register on the NISR Microdata Portal
and download:

| Dataset | Catalogue | Place the file at |
|---|---|---|
| FinScope Rwanda 2024 (RWA-NISR-FINSCOPE-2024-v01) | https://microdata.statistics.gov.rw/index.php/catalog/120 | `data/raw/FinScope_2024_Rwanda.dta` |
| Agricultural Household Survey 2024 (RWA-NISR-RAHS-2024-V0.1) | https://microdata.statistics.gov.rw/index.php/catalog/123 | `data/raw/Microdata.zip` |

`data/raw/` is git-ignored. Only aggregate tables are committed:

| File | Contents |
|---|---|
| `ahs_national.csv`, `ahs_segments.csv` | National indicators and the four-way account/loan segmentation |
| `ahs_by_group.csv` | Indicators by quintile, head's sex, farm size, province, district, cooperative and more |
| `ahs_loan_sources.csv`, `ahs_loan_purpose.csv`, `ahs_denial_reasons.csv` | Where loans come from, what they are for, why they are refused |
| `fs_national.csv`, `fs_by_group.csv`, `fs_barriers.csv`, `fs_farmer_digital.csv`, `fs_records_link.csv` | FinScope adult indicators, barriers, phone and mobile-money use, record-keeping |
| `models.csv` | Odds ratios with confidence intervals |
| `validation.csv`, `meta.json` | Checks against NISR's published tables; sample sizes and build date |

`docs/01_dataset_audit.md` and `docs/variable_inventory.csv` document the datasets and variables we examined.

### Methods

- **Weights and design.** AHS: weight `weight`, primary sampling unit `clust`, stratum `district`, with Taylor-linearised
  confidence intervals (`src/survey.py`). FinScope: weight `pop_wt`; the public file has no PSU, so **FinScope
  intervals are understated**.
- **Suppression.** Cells with n < 30 are suppressed; a coefficient of variation above 0.30 is flagged "caution".
- **Indicators.** Defined once in `src/indicators.py`; `pipeline/build_aggregates.py` turns microdata into the committed
  tables.
- **Models.** Weighted logistic regression of formal loan on welfare quintile, head's sex, farm size, land title,
  cooperative membership and province, with design-based sandwich standard errors (`src/models.py`). Associations only.
- **No record linkage** between AHS and FinScope. They are compared side by side as aggregates.

### Validation

AHS estimates reproduce NISR's published tables ([`validation.csv`](data/aggregates/validation.csv)):

| Indicator | Ours | Published | Source |
|---|---|---|---|
| Household has a bank, SACCO or MFI account | 62.7 | 62.7 | AHS Main Report, Table 32 |
| Household requested a loan | 71.1 | 71.1 | Table 34 |
| Loans from tontines (share of loans) | 58.1 | 58.1 | Table 35 |
| Loans from relatives or friends | 25.1 | 25.1 | Table 35 |
| Loans from SACCOs | 6.0 | 6.0 | Table 35 |
| Cooperative membership | 11.8 | 11.8 | Table 30 |

FinScope mobile money (76.2 vs 77) and bank account (20.2 vs 22) reconcile. Our formal saving, credit and insurance
figures are lower than the official strands because the official strand code is not public, so we use FinScope for
**group comparisons, not national totals**.

### Reproduce the research

```bash
pip install -r requirements-pipeline.txt
python pipeline/build_aggregates.py     # needs data/raw/ (see Data)
python analysis/key_findings.py         # prints the headline findings with CIs and n
```

## 7. Limitations and responsible use

**Research limits**
- The surveys are cross-sectional: nothing here shows that records or credit *cause* better outcomes.
- AHS `s10aq1` is labelled "tried to obtain a loan", but every "yes" has a denial reason, so we treat it as "reported
  a denial" (n = 295, wide intervals).
- The AHS milk, egg and honey files contain many exact duplicate rows and are not used.
- The "always track money" question went to about half of respondents; estimates use answerers only.
- FinScope intervals are understated (no cluster variable in the public file).

**Product limits**
- Entries are self-reported and unverified. The prototype cannot tell a true record from a false one.
- A short PIN protects a *copied* vault only weakly (see [Security](#4-security-and-privacy)).
- Phone numbers are not verified, and there are no lender accounts or server audit log yet.
- The USSD menu is a simulation, not connected to a telecom gateway.
- The Kinyarwanda text needs native-speaker review.
- We claim **no impact on loan approval** without a pilot.

**Responsible use.** The tool describes a farm's own records. It does not score individuals, predict default or make
lending decisions, and it never will in this design, so a lender stays responsible for the decision. The design
follows common data-protection principles (consent, minimisation, security) that Rwanda's personal data protection law
also expects, but it has not had legal review. A real deployment needs a registered data controller, a Kinyarwanda
privacy notice and a data-protection impact assessment.

## 8. Run it locally

**Requirements:** Python 3.11 or newer. Node.js 18 or newer is needed only if you change the landing page.

```bash
git clone https://github.com/patrickntirenganya/FinBridge-Rwanda.git
cd FinBridge-Rwanda
python -m venv .venv && source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r requirements.txt
streamlit run app.py                                  # opens http://localhost:8501
```

The product needs no survey data and no secrets.

**Change the landing page** (TypeScript + Tailwind, source in `frontend/`):

```bash
cd frontend
npm install
npm run build          # type-checks, builds, and writes ui/landing/landing.html
```

`ui/landing/landing.html` is committed, so Streamlit Cloud needs no Node.

## 9. Test it

```bash
python tests/test_app.py        # must print "... 0 failures"
```

The suite needs only `requirements.txt`. It covers:

| Area | What is checked |
|---|---|
| **Every page** | Renders in Kinyarwanda and English, including every option of every selector |
| **Farmer flows** | Demo entry, the tap-to-record flow, saving a record, every season in the summary and report |
| **Record engine** | Totals, insights, the farm story, loan instalment arithmetic, report escaping and disclaimers, import validation (junk rows skipped, `confirmed` evidence refused) |
| **Vault** | PIN and phone rules; wrong PIN, wrong phone and tampering rejected; no plaintext in storage; fresh nonce each save; junk files rejected; lock-out schedule |
| **Sharing** | Wrong code, tampering, expiry, season filter, names dropped unless chosen, no plaintext in the file |
| **Sign-in** | End to end: sign up, autosave a record, lock, sign in again, five wrong PINs, lock-out holds against the right PIN |
| **Lender page** | Opens a real share; hostile text in a farmer's file is escaped |
| **USSD** | Every screen is 160 characters or fewer, both languages, menus re-prompt on bad input |
| **Language** | Every string exists in both languages with matching placeholders |
| **Separation** | The landing copy contains no percentage and no `ui/` module reads survey data |

The browser-storage bridge cannot run inside `AppTest`, so it was verified separately in a real browser: create a
profile, confirm the stored vault holds no plaintext, reload, see the remembered phone, refuse a wrong PIN, accept the
right one.

## 10. Deploy it

The app deploys to **Streamlit Community Cloud** from this public repository.

1. Make sure the repository is **public**.
2. Sign in at https://share.streamlit.io with GitHub and choose **Create app → Deploy a public app from GitHub**.
3. Set repository `patrickntirenganya/FinBridge-Rwanda`, branch `main`, main file `app.py`.
4. Under **Advanced settings**, pick Python 3.11 or newer. No secrets are needed.
5. Deploy. Cloud installs `requirements.txt` (app dependencies only).
6. After it is live: create a profile, reload and sign in again (this checks browser storage on the live domain),
   then try the lender page and the demo. Check a real phone.

Notes: apps that get no visits go to sleep and need a click to wake, so open the app shortly before judging. One
sign-up briefly uses about 64 MB for key derivation.

**Troubleshooting**

| Symptom | Likely cause |
|---|---|
| Landing page missing | `ui/landing/landing.html` not built; run `cd frontend && npm run build` |
| "Loading…" never ends on *My farm records* | Browser blocks local storage; use *Continue without saving on this device* and rely on the backup file |
| Sign-in says "Wrong phone number or PIN" | Wrong credentials, a damaged file, or a different browser (the vault lives in the browser it was created in; restore from the backup file) |
| Lender cannot open a share | Wrong code, damaged file, or the share expired; ask the farmer for a new one |

## 11. How this meets the judging criteria

| Criterion | How FinBridge answers it |
|---|---|
| **Problem relevance (NST2 / Vision 2050)** | A direct response to the gap between financial access and formal credit among farm households, supporting agricultural transformation and financial inclusion |
| **Data use and methodology** | Two NISR surveys analysed with survey weights and design-based errors; adjusted models; estimates validated against NISR's published tables; findings traced to each design choice ([section 2](#2-from-research-to-product)) |
| **Tangible impact** | A working tool that farmers and lenders can use today, built for basic phones; honest about what a pilot must still prove |
| **Technical innovation** | Local-first encryption with consent-based sharing and no server database; one record engine across web and USSD; a lender story generated from the farmer's own records; TypeScript and Tailwind front end |
| **Usability** | Three-tap recording, plain-language summaries, large targets, Kinyarwanda first, phone-number-and-PIN sign-in, a one-click demo |

## 12. Roadmap

Not part of the hackathon build:

1. **Pilot** with a SACCO and a cooperative, to test whether lenders find the records useful and measure any effect on
   access.
2. **Verified lenders:** institution accounts and a server-side audit log (needs a small database).
3. **Third-party confirmation:** buyers and cooperatives confirm entries, enabling the `confirmed` evidence level.
4. **Phone verification** by SMS, and a **PIN change** option.
5. **A real USSD gateway** with a telecom partner.
6. **Native-speaker review** of every Kinyarwanda string; voice prompts and a pictures-only mode for low-literacy
   users.
7. **Independent security review** and legal review under Rwandan data-protection law.

## 13. Repository layout

```
app.py                     entry point: navigation, language, auth flush
requirements.txt           app dependencies (what Streamlit Cloud installs)
requirements-pipeline.txt  extra packages to rebuild the research tables

src/
  records.py               record engine: validation, summaries, insights, farm story, loan instalment, report
  vault.py                 PIN-locked profile: create, unlock, reseal, PIN rules, lock-out
  share.py                 encrypted share package, one-time code, expiry
  crypto.py                scrypt and AES-256-GCM primitives
  ussd.py                  USSD menu state machine (screens <= 160 characters)
  i18n.py                  every string, Kinyarwanda and English
  indicators.py, survey.py, models.py, load.py   research code (not used by the app)

ui/
  landing.py               embeds the landing bundle
  farmer.py                sign-in gate, tap-to-record flow, summary, sharing, USSD preview
  lender.py                opening a share; story, charts, worksheet, quality, entries
  auth.py                  sign-up, sign-in, restore, erase, browser-storage bridge, idle lock
  about.py                 how it works, limits, link to the research
  theme.py                 colours, CSS, hero banner
  assets/, landing/        logo, farmer photos, built landing page

frontend/                  Vite + TypeScript + Tailwind source of the landing page

pipeline/                  microdata -> data/aggregates/*.csv
analysis/                  variable inventory, key findings
data/aggregates/           committed research tables (safe to publish)
data/geo/                  district boundaries (display only; not used by the app)
data/raw/                  NISR microdata, git-ignored, never committed

tests/test_app.py          the test suite
docs/                      security note, demo script, dataset audit, variable inventory
```

**Contributor rules.**
- Never commit microdata (`.dta`, `.zip`, `data/raw/`, `*.pkl`).
- Change an indicator only in `src/indicators.py`, then rebuild the aggregates and rerun the tests.
- Add every user-facing string to `src/i18n.py` in both languages.
- Never add a score, a prediction or a lending decision.
- Run `python tests/test_app.py` after every change.

## 14. Credits, licences and references

- **Data:** National Institute of Statistics of Rwanda (NISR), Agricultural Household Survey 2024 and FinScope Rwanda
  2024 (with Access to Finance Rwanda). Public-use microdata; follow the NISR terms of use and do not redistribute.
- **Photographs:** photos of Rwandan farmers were supplied by the team for this prototype. Confirm their licence and
  the subjects' consent before any public release beyond the hackathon.
- **Boundaries:** geoBoundaries ADM2 for Rwanda, CC BY 4.0. See [`data/geo/README.md`](data/geo/README.md).
- **Font:** Atkinson Hyperlegible, loaded from Google Fonts.

**References**
- National Institute of Statistics of Rwanda (2024). *Agricultural Household Survey 2024*, main report and microdata.
- National Institute of Statistics of Rwanda and Access to Finance Rwanda (2024). *FinScope Rwanda 2024*.
- Republic of Rwanda. *National Strategy for Transformation (NST2)* and *Vision 2050*.
- Runfola, D. et al. (2020). geoBoundaries: a global database of political administrative boundaries. *PLOS ONE*
  15(4): e0231866.
