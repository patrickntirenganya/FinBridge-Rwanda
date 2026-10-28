# FinBridge combined build plan (supersedes the feature list in 02)

Put in `docs/`. Claude Code: read `CLAUDE.md`, then `docs/02_evidence_and_features.md` (international research), then this file. **This file decides what to build.** Every number below was computed from the NISR microdata on 28 October 2026 or comes from a cited source.

## 1. The decision in one paragraph

FinBridge becomes **one product with two connected tools that share one evidence base**:

- **FinBridge Insights** (for SACCOs, BNR, MINAGRI, AFR): where agricultural households are banked but not financed, and why. Already built in Streamlit.
- **Umuhinzi Records** (for farmers): a farmer-owned record and loan-readiness pack, shared only by the farmer's choice. Already prototyped (client-side, JSON backup, USSD preview).

The link: Insights shows that **35.1% of agricultural households (≈759k) save with a SACCO, bank or MFI yet borrow only informally**, and that among AHS loan refusals the most cited reason is **"unclear purpose of the loan" (29.7%)**, followed by collateral (23.6%) and insufficient income (20.9%) (n = 295 refusals, wide CIs). Umuhinzi Records is the farmer-side instrument for exactly that gap: it helps a farmer show a clear purpose and a record of farm activity. This mirrors China's rural credit-household files and India's SHG–Bank Linkage (see doc 02). **That this improves loan approval is a hypothesis, not a finding; say so everywhere.**

Both tools read the same aggregate files produced by `pipeline/build_aggregates.py`. Neither ever sees microdata.

## 2. What we tested in the other proposals

| Claim in the other conversation | Test on AHS 2024 microdata | Result |
|---|---|---|
| Flag a farmer as vulnerable if maize < 2,000 kg/ha | Weighted share of maize plots below 2,000 kg/ha | **62% (Season A), 68% (Season B)**. The flag would fire for most farmers, so it carries no information |
| Bean "baseline" 709 kg/ha | Share of bush-bean plots below 709 | 41% (A), 66% (B); median 820 vs 492 kg/ha: season matters |
| One national kg/ha benchmark per crop | Share of plots intercropped | **86–95%** of maize and bean plots are intercropped; single-crop yield benchmarks do not apply |
| Yield baselines "from NISR AHS" | Checked | Not from AHS. Rice 4.1 t/ha is from the Seasonal Agricultural Survey; the others are unsourced |
| "9.3% financially healthy" | FinScope 2024 presentation | Published figure is **10%** |
| "54% of Rwandan women use informal groups" | Not found in our data or sources | Do not use |
| Input doses (maize 25 kg seed, 5,000 kg organic, 100 kg DAP per ha) | No source given | **Invented.** Fertilizer advice must come from RAB recommendations by zone; wrong doses cost farmers money |
| "Cryptographic" SMS parser sets "Receipt-Verified" | Logic review | Not cryptographic: a regex on pasted text. Anyone can type a fake SMS. It also breaks the app's own rule that "Confirmed" is reserved for a future verifier |

## 3. Feature decisions

| Idea | Decision | Why |
|---|---|---|
| Risk Buffer & Shock Resilience Index (fixed yield thresholds, "save 15%") | **Replace with B1** | Thresholds fire for the majority. Advising a farmer with a failed harvest to save more is backwards |
| Predictive Agronomy Input Planner (fixed doses) | **Replace with B2** | Doses unsourced. Show what peers actually do (descriptive) and point to RAB/extension for doses |
| SMS "Receipt-Verified" parser | **Replace with B4** | Keep the useful part (attaching a reference) without claiming verification |
| China TPA "dynamic monitoring alerts" | **Aggregate version B5; household alerts on roadmap** | Survey data are one-off, so no household-level real-time alerts. District shock exposure is feasible |
| Smart-agriculture pest/weather SMS alerts | **Roadmap** | Needs Meteo Rwanda / RAB pest data feeds we do not have |
| Machinery and subsidy transparency | **Roadmap** (optional aggregate) | Mechanisation is ~0% of plots; low payoff for Track 2 |
| F1 SACCO opportunity map, F2 tontine link, F3 social protection, F4 regression, F5 what-if (doc 02) | **Keep** | Verified, Track 2-aligned |

## 4. Build specifications

Rules from `CLAUDE.md` apply: weighted estimates, CIs, n < 30 suppressed, associations not causes, no individual scoring, no microdata in the repo or the browser.

### B1. Harvest peer comparison (Umuhinzi Records)

**Purpose:** show a farmer how their harvest compares with similar plots nationally, as a band, not a verdict.

**Pipeline** (add to `build_aggregates.py`, export `data/aggregates/yield_benchmarks.json`):
- Source: AHS `Section3_4`, one row per plot × crop slot k = 1..4: crop `s3_q4_k`, crop share `s3_q4_ka` (%), harvest kg `s3_q20_k`, plot area `s2q2` (m²), `Season` (1 = A, 2 = B, 3 = C), weight `weight`, `district`.
- Effective area (ha) = `s2q2 / 10000 × clip(s3_q4_ka, 1, 100) / 100`. Yield = kg / effective area. Drop kg ≤ 0, area ≤ 0.
- Trim the top and bottom 1% per crop × season (document it).
- For each crop × season with n ≥ 100 plots: weighted p25, p50, p75, n, and share intercropped. District-level only where n ≥ 100; else national.
- Reference values from the 28 Oct run (Claude Code must reproduce these): maize A p50 1,547 (IQR 809–2,756); maize B 1,255 (581–2,422); bush bean A 820 (486–1,410); bush bean B 492 (274–862); climbing bean A 871 (516–1,394); climbing bean B 789 (459–1,251). Rice is n < 250 per season; show national only.

**App logic** (client-side, reads the JSON):
- Inputs: crop, season, harvest kg, plot area, and crop share of plot (default 100%, with a hint that most plots are mixed).
- Output band: "below most similar plots" (< p25), "typical" (p25–p75), "above most similar plots" (> p75).
- Copy when below p25: "Many things lower a harvest, including weather, pests and seed. Farmers in this position can ask their extension officer or Twigire Muhinzi group, and check whether crop insurance (NAIS) covers this crop." No savings instruction, no "vulnerable" label.
- Footer: "Compared with AHS 2024 plots of the same crop and season. Self-reported harvests; for guidance only."

**Accept when:** the JSON reproduces the reference medians within ±2%; three test inputs land in the right bands.

### B2. What farmers like you use (Umuhinzi Records + Insights)

**Purpose:** descriptive peer reference on inputs, which are also the most common farm loan purpose.

**Pipeline:** export `input_use.json` with plot-level weighted shares by district (and national): organic fertilizer `s4_q1 == 1` (national 63.6%), inorganic `s4_q4 == 1` (29.5%), pesticide `s4_q12 == 1` (15.7%), improved seed `s3_q9_1 ∈ {2, 3}` (17.0%), irrigated `s4_q22 == 1` (5.6%), **"can't afford irrigation" `s4_q22 == 3`** (finance barrier; compute and show). Use PSU `clust`, stratum `district`; suppress n < 30.

**UI:** "In {district}, X% of plots used inorganic fertilizer last season (Rwanda: 29.5%)." Link text: "For the right amount for your soil, ask your extension officer or check RAB fertilizer recommendations." **No doses.** In Insights, add the "can't afford irrigation" share by district beside the SACCO map.

### B3. Loan purpose sheet (Umuhinzi Records)

**Purpose:** address the most cited refusal reason, "unclear purpose" (29.7% of 295 refusals; CI 22.5–36.9).

**Fields:** what the money is for (inputs, equipment, livestock, other), items and quantities, expected cost (RWF), planting and harvest months, how repayment will be made (crop sales, other income), and group membership (tontine, cooperative, Twigire Muhinzi). Export as a one-page printable summary alongside the farmer's records.

**Copy:** "A clear plan can help a SACCO officer understand your request. It does not guarantee a loan."

### B4. Evidence levels (replace "Receipt-Verified")

Three statuses, shown as text labels:
1. **Self-reported** (default).
2. **Reference attached**: the farmer typed a transaction or receipt reference. Label: "Reference attached, not checked."
3. **Confirmed**: reserved for a future institutional check (cooperative or SACCO officer, or an operator API with the farmer's consent). It cannot be set by the farmer or by an imported file. Keep the existing rule.

No regex "verification". If you keep a paste box, it only extracts a reference string and amount into the record and still shows "not checked".

### B5. District shock exposure (Insights; aggregate version of the China TPA alert idea)

**Data:**
- FinScope `cc1_1..cc1_8` (climate events in the past year), by district and farm status, plus coping plans `cc7_*`. Show the shares planning to use formal savings or insurance.
- AHS `s3_q21_1_1` (main explanation of crop production): share of plots citing drought, heavy rain/hail, flood, or pests/diseases, by district.
- AHS crop insurance (1.7% of households).

**UI:** "Where shocks hit and the cushion is thin": district table and map with CIs. Clearly state "survey snapshot, not a live alert". Roadmap note: a live version would need Meteo Rwanda and MINAGRI administrative data.

### Carry over from doc 02 (unchanged)

F1 SACCO opportunity map (highest priority), F3 social protection lens, F2 tontine-to-SACCO link, F4 adjusted regression, F5 what-if calculator.

## 5. Order of work (deadline 30 Oct, 23:59)

1. **Today:** deploy both tools as they are (Insights on Streamlit Community Cloud; Records on GitHub Pages or Netlify if it is static). Cross-link them. Submit nothing yet, but have both links.
2. **Today / tonight:** F1 SACCO map; pipeline exports `yield_benchmarks.json` and `input_use.json`.
3. **29 Oct:** B1 and B4 in Records; F3 social protection; B3 loan purpose sheet; recommendations page; README.
4. **30 Oct morning:** B2, B5 or F4 only if everything above is done and tested. Record the ≤ 3-minute demo (story: Insights finds the 759k → Records shows how one farmer prepares). Submit by early evening.

Cut first if late: B5, F4, F5, B2. Never cut: deployment, README, demo video, tests passing.

## 6. Prompt for Claude Code

```
Read CLAUDE.md, docs/02_evidence_and_features.md and docs/03_combined_build_plan.md.
Update the CLAUDE.md backlog to match section 5 of doc 03. Then:
1. Tell me the stack and folder of the Umuhinzi Records app and how both tools will be deployed.
2. Implement the pipeline exports for B1 (yield_benchmarks.json) and B2 (input_use.json),
   reproduce the reference medians in section 4/B1, and run the tests.
Stop and show me the medians before touching any UI.
```
