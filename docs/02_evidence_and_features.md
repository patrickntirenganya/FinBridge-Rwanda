# Evidence and features: what to build next

Put this file in `docs/`. Claude Code: read it after `CLAUDE.md`, then add the features below to the backlog in `CLAUDE.md` in the order given. Every number here was computed from the microdata with the project's `src/` code on 28 October 2026; regenerate rather than retype.

## 1. Where we compete

**Track 2: Financial Inclusion & Poverty Reduction** ("understand financial exclusion, poverty dynamics, and the impact of social protection programmes"). Our core story covers exclusion and poverty; feature F3 adds the social-protection angle the track names explicitly. Track 1 (agricultural productivity) is a secondary link through input finance (F1, F2).

**NST2 hook:** MINAGRI states that NST2 and PSTA5 target raising agriculture's share of the national loan portfolio from 6% to 10% by 2029 (https://www.minagri.gov.rw/updates/news-details/minagri-and-rab-spiu-encourage-farmers-to-embrace-the-national-agriculture-insurance-scheme-nais). The FSDS 2025–2029 targets better access to finance for women and agriculture. This target is about **loan value**, not households; never compute it from our household percentages. Use it as policy context only.

## 2. What other countries did about "banked but not financed"

| Model | Country | What it does | Lesson for Rwanda | Source |
|---|---|---|---|---|
| Credit households / credit villages | China (PBC, rural credit cooperatives, since 2000) | Cooperatives keep credit files on every household; village committees help rate households; rated households get collateral-free small loans and credit lines | SACCOs already hold accounts for 63% of farm households. The same relationship can carry a credit record | PBC guidelines: https://camlmac.pbc.gov.cn/en/3688110/3688172/4048362/2025080817551068801/index.html |
| Satellite-informed farm lending ("Tomtit") | China (MYbank) | Remote sensing estimates crop type and output on farmer-marked plots to set collateral-free credit lines; about 1.69 M growers by end-2023 | Long-term vision only. We have no farm-level imagery or repayment data, so we do **not** build this | https://www.qorusglobal.com/content/28190-mybank-leverages-ai-to-serve-53-million-smes |
| Credit guarantees | China (national agricultural credit guarantee system) | Provincial agencies guarantee farm loans; national level re-guarantees | Rwanda's BDF guarantees play this role; collateral is cited in 24% of AHS loan refusals | https://policycn.com/policy-briefs/17-06-28-betting-the-farm |
| SHG–Bank Linkage | India (NABARD, since 1992) | Banks lend to savings groups in multiples of group savings, without collateral; peer pressure secures repayment | Rwanda's tontines are the equivalent: 81% of farm households are members. Link tontines to SACCOs | https://findevgateway.org/sites/default/files/publications/files/mfg-en-paper-nabard-and-microfinance-2002.pdf |
| In-kind input credit, flexible repayment | Rwanda/East Africa (One Acre Fund / Tubura) | Seed and fertiliser on credit, repay any amount any time before the deadline; Rwanda preliminary 2025 repayment 99% | Smallholders repay when credit fits the season. Counters the "worried I can't repay" barrier (26% of FinScope non-borrowers) | https://www.globalgiving.org/pfil/59148/2025_Q4_One_Acre_Fund_Performance_Report.pdf |
| Graduation approach | BRAC model; RCTs in 6 countries (Science, 2015) | Asset transfer + consumption support + coaching + savings; lasting gains in consumption and assets | VUP cash-transfer recipients have bank accounts at one-third the rate of others (F3). A graduation pathway would connect transfers to SACCO accounts | https://economics.mit.edu/sites/default/files/2022-08/science.1260799.pdf |

## 3. Features (priority order)

Rules from `CLAUDE.md` apply to all: weighted estimates with CIs, n < 30 suppressed, aggregates only in the app, associations not causes, no individual scoring.

### F1. SACCO opportunity map (highest priority)

**Question it answers:** where are the households that already save formally but borrow only informally?
**Verified evidence:** 35.1% of agricultural households (≈759k) have an account but borrowed only informally. Largest district counts: Nyagatare ≈48.8k (CI 37.5k–60.0k), Gisagara ≈42.4k (53.3% of households), Gicumbi ≈37.2k, Nyamagabe ≈34.8k, Ruhango ≈34.6k, Gakenke ≈33.0k.
**Users:** SACCO managers, BNR, MINAGRI, AFR.
**Data:** AHS. Segment = `acct_formal & loan_any & ~loan_formal` (already in `build_aggregates.py` as "Account, borrowed only informally").
**Pipeline:** new table `ahs_district_opportunity.csv` with district, province, pct, lo, hi, households = pct × district weighted households (and hh_lo, hh_hi from the CI bounds), n, reliability.
**Map:** download `https://github.com/wmgeolab/geoBoundaries/raw/main/releaseData/gbOpen/RWA/ADM2/geoBoundaries-RWA-ADM2_simplified.geojson` (Git LFS; follow redirects). Property `shapeName` = district name; check all 30 match AHS names and fix spelling differences in a mapping dict. Save to `data/geo/rwanda_districts.geojson` (CC BY 4.0, credit geoBoundaries in Methods).
**UI:** choropleth of household **counts** (toggle: share), plus a table sorted by count that shows CI ranges. Districts with reliability "caution" get a visible note, not a rank. Title: "Where SACCOs could reach existing savers with credit".
**Accept when:** 30 districts render; totals across districts ≈ 759k; test passes.

### F2. Tontine-to-SACCO linkage panel

**Question:** can savings groups be the bridge to formal credit, as in India's SHG–Bank Linkage?
**Verified evidence:** 81.1% of agricultural households are tontine members (CI 79.2–83.1); 57.8% of tontine borrowers already hold a SACCO account (CI 55.3–60.2, n = 1,850); 35.5% of account-holders who borrowed only informally borrowed for farm purposes (inputs, equipment or livestock).
**Data:** AHS `Saving.s10cq8` (tontine), `acct_sacco`, `loan_tontine`, loan purposes.
**Pipeline:** add indicators `tontine_member`, and `sacco_among_tontine_borrowers` (computed on the tontine-borrower subset) to the national table; group breakdowns by quintile and head sex.
**UI:** a short three-step visual: tontine member → borrowed from tontine → already has a SACCO account. Text box with the India SHG–Bank Linkage lesson and its source.

### F3. Social protection lens (Track 2)

**Question:** do social-protection recipients also get connected to formal finance?
**Verified evidence (FinScope, adults in households receiving a VUP direct cash transfer, `c13d == 1`, n = 1,078):** bank account 7.1% (CI 4.7–9.5) vs 21.3% for others; registered mobile money 69.0% vs 77.0%; emergency fund 16.3% vs 21.2%. Formal credit is similar (14.1% vs 13.4%) because VUP/Ubudehe loans count as formal in our definition (`h3_07`); show `h3_07` separately so this is transparent.
**Data:** FinScope `c13d` (add a `vup` group to `FS_GROUPS` in `src/indicators.py`), Ubudehe category already present. AHS: VUP as a loan source (2.8% of loans) and `poverty`/`quintile` groups.
**UI:** page "Social protection and finance": paired bars VUP vs not, plus Ubudehe category 1 vs others. Note on the graduation approach with source. Remind users that FinScope CIs are understated (no PSU).

### F4. Adjusted associations (methodology credibility)

Already backlog item 1 in `CLAUDE.md`: survey-weighted logistic regression of `loan_formal` on quintile, head sex, farm size, land title, cooperative membership, province; cluster-robust SEs on `clust`. Forest plot of odds ratios. Answers: "Is the gap for female-headed households still there after accounting for farm size and welfare?"

### F5. Scenario calculator (transparent, not a prediction)

**Question:** what would it mean if SACCOs converted part of their existing savers into borrowers?
**Logic (pure arithmetic from aggregates):** slider p% of the "account, borrowed only informally" segment gains a formal loan. New formal-loan rate = 14.1% + p × 35.1%; households reached = p × 759k (show CI bounds). Optional filter by district from F1.
**UI copy must say:** "This is a what-if calculation, not a forecast. It does not assume these households qualify or want a loan." Do not convert to the NST2 loan-value target.

### F6. Shocks without a cushion (if time allows)

FinScope `cc1_*` (climate events experienced), `cc7_*` (coping plans: formal savings, insurance claim), by farm status; AHS crop insurance 1.7%. Message: farmers face repeated shocks with almost no insured or formal-savings cushion. Link to NAIS.

## 4. Recommendations page (tie each to a finding)

1. **SACCO credit for existing savers** (F1, F5): use the savings history SACCOs already hold, as China's credit-household files do. *Evidence-backed:* the segment size. *Hypothesis:* that savings records predict repayment.
2. **Link tontines to SACCOs** (F2): group loans backed by group savings, following India's SHG–Bank Linkage. *Evidence-backed:* 81% membership; 58% overlap.
3. **Season-shaped input credit** (loan purposes; One Acre Fund): only 10.8% of input loans are formal. *Hypothesis:* flexible repayment raises uptake in Rwanda's SACCOs.
4. **Target female-headed households** (7.8% vs 16.3% formal loans; check F4 after adjustment).
5. **Connect VUP recipients to accounts** (F3): graduation pathway. *Evidence-backed:* 7.1% vs 21.3% bank accounts.

## 5. Datasets

| Dataset | Status | Why |
|---|---|---|
| Rwanda district boundaries (geoBoundaries ADM2) | Fetch in F1 (public, CC BY 4.0) | Map |
| EICV7 VUP sample (NISR catalog 121) | Optional, post-hackathon | Deeper social-protection analysis; AHS person IDs are EICV7 IDs, so check NISR's terms before any linkage |
| EICV7 cross-section (NISR catalog 119) | Optional, post-hackathon | Income, consumption, finance for all households |

No further data is needed to finish by 30 October.

## 6. Two-day plan (deadline 30 October, 23:59)

- **28 Oct:** F1 map and table; F3 social protection page. Deploy a first version to Streamlit Community Cloud today so the link exists.
- **29 Oct:** F2, F4, F5; recommendations page; full README with references.
- **30 Oct (morning):** record the ≤ 3-minute demo, final tests, submit early. Leave the evening as buffer.

## 7. Prompt for Claude Code

```
Read CLAUDE.md and docs/02_evidence_and_features.md. Add features F1–F6 to the CLAUDE.md
backlog in that order. Then implement F1 end to end: pipeline table, geojson download and
name matching, map + table page, and update tests/test_app.py. Run the pipeline and the tests,
show me the district totals check (≈759k), and stop for my review before starting F3.
```
