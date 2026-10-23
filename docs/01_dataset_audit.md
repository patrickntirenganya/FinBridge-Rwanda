# FinBridge Insights: Dataset Audit (Deliverable 1)

Audit date: 23 October 2026. Every number below was computed from the microdata files in this project, not copied from reports, unless marked "published".

## 1. Availability

| Item | Status | Notes |
|---|---|---|
| FinScope 2024 microdata (`FinScope_2024_Rwanda.dta`) | Available, readable | Stata 118, 50.8 MB, single file |
| FinScope 2024 questionnaire, final report, presentation | Available | Report (77 pp.) and questionnaire (54 pp.) have text layers |
| AHS 2024 microdata (`Microdata.zip`, 14 `.dta` files) | Available, readable | One file (Section 1) needs Latin-1 encoding |
| AHS 2024 questionnaire and main report | Available | Questionnaire PDF omits the finance module (Section 10) that **is** in the data |
| FinScope derived-variable syntax (strand definitions) | **Not available** | Prevents exact replication of some published strands (see §4) |
| `3Assignment_AD.docx` | Unrelated | Active Directory assignment; ignored |

## 2. FinScope 2024 (RWA-NISR-FINSCOPE-2024-v01)

**Shape:** 13,994 respondents × 2,442 variables, no duplicate rows. One adult (16+) per household; refugee-camp sample is not in the public file.

**Unit:** individual adult, with household context fields.

**Design:** PPS sample on the 2022 census frame (published methodology). Public file contains `pop_wt` (person weight, sums to **8.156 M**, matching the published 8.2 M adults) and `hh_wt` (sums to 3.575 M households). Weight coefficient of variation is 0.90 (range 21.9–5,526), so unweighted estimates would be badly biased. **There is no PSU/cluster or explicit stratum variable** (EA, sector and cell were removed for anonymisation). Our standard errors therefore treat respondents as PSUs within district strata and **understate** true uncertainty; this is disclosed wherever FinScope CIs appear.

**Geography:** province (`a1`), district (`a2`, 30), urban/rural (`a6`). District is the finest level. Average n ≈ 466 per district is adequate for common indicators but not for rare ones.

**Data quality:** core demographics have no missing values. Missingness elsewhere is structural (skip logic), e.g. `k17` is asked only of the unbanked (20.8% missing), `h7` only of non-borrowers. Many multi-select items are stored as `object`/string and need coercion. Some labels contain encoding artefacts (`Didn?t`).

**Reconciliation with published figures**

| Indicator | Our estimate | Published | Status |
|---|---|---|---|
| Adult population | 8.156 M | 8.2 M | Match |
| Registered mobile money (`f5` ∈ 3,4,6) | 76.2% | 77% | Match |
| Bank account in own name (`k1`) | 20.2% | 22% banked | Close; official strand also counts other bank product use |
| Formal credit, past 12 months (`h3` items) | 13.3% | 24% | **Gap**; official definition is wider and its syntax is not public |

Decision: the app uses transparent, documented definitions and shows published figures alongside, labelled as such.

## 3. Agricultural Household Survey 2024 (RWA-NISR-RAHS-2024-V0.1)

**Files (rows):** Section0 households (3,724), Section1 members (16,292), Section2 plots (23,266), Section3_4 crops and inputs (32,616 × 331 vars), Section5 fruit (9,193), Section6 extension and programmes (9,286), Section7 tools (9,981), Section8 sustainable practice (3,724), Section9_10_12 livestock (9,947), Section11 milk/eggs/honey, **Saving** (10,342 person-account rows), **Credits** (5,224 loan rows).

**Unit:** agricultural household (plus member, plot and loan sub-levels joined by `hhid`).

**Design:** AHS is a PPS subsample of 600 EICV7 enumeration areas, allocated to districts in proportion to agricultural households, with implicit urban/rural stratification inside districts. Public file contains `clust` (**581 PSUs**) and `weight` (sums to **2.164 M agricultural households**). We use PSU = `clust`, stratum = `district` for linearised variance. This is a sound, disclosed approximation.

**Linkage inside AHS:** member IDs are EICV7 IDs, and Section 2 carries EICV7 **consumption quintiles and poverty flags** (`quintile`, `pov_jan`, `epov_jan`). Welfare can therefore be analysed alongside finance within the same households, which is legitimate because it is the same sample.

**Reconciliation with published figures (all match)**

| Indicator | Our estimate | Published |
|---|---|---|
| Agricultural households | 2.164 M | 2.2 M |
| Main livelihood is agriculture | 88.4% | 88.4% |
| Household has bank/MFI/SACCO account | 62.7% | 62.7% |
| Household requested a loan | 71.1% | 71.1% |
| Loan source: tontine / relatives / bank / SACCO / VUP | 58.1 / 25.1 / 6.3 / 6.0 / 2.8% | 58.1 / 25.1 / 6.4 / 6.0 / 2.8% |
| Cooperative membership | 11.8% | 11.8% |

**Data quality flags:** exact-duplicate rows in milk (3,002), egg (2,779) and honey (3,510) files must be investigated before use; Section 1 needs Latin-1 decoding; `s10aq1` is labelled "tried to obtain a loan" but every "yes" carries a denial reason, so we treat it as "reported a loan denial" (n = 295 rows, wide CIs); `s2q8` collateral rights are coded member lists where `99` means none.

## 4. Can the two datasets be combined?

**Not at record level.** They are different samples (FinScope: individuals, census-frame PPS, Dec 2023–Feb 2024; AHS: agricultural households, EICV7 subsample, 2023/24 agricultural year), share no identifiers, and FinScope's sub-district geography was removed. Matching on district or demographics would fabricate links and break data-use terms.

**Allowed:** side-by-side comparison of aggregate estimates at national or province level, with definitions and populations stated (FinScope "farming household" from `m1` ≈ AHS "agricultural household"; individual vs household unit).

## 5. Analytical capacity

| Use | FinScope | AHS |
|---|---|---|
| Weighted descriptives | Yes | Yes |
| Design-based inference | Approximate (no PSU; understated SEs) | Yes (PSU + strata proxy) |
| Weighted regression | Yes, with SE caveat | Yes |
| Predictive ML | Possible but low value; not a credit score | Possible with cluster-grouped CV; association only |

## 6. Restrictions

Both are NISR public-use files. Respondent-level data will **not** be committed to GitHub. The repository will contain code, aggregated estimate tables, and links to the NISR catalogue (catalog/120 and catalog/123), which satisfies the hackathon "data file + link" requirement without redistributing microdata.

## 7. Research questions ranked by feasibility

1. **Account-to-credit gap among agricultural households (AHS)**: how many farm households are banked but not financed, and which characteristics are associated with formal credit? Validated variables, proper design, welfare linkage. *Feasibility: high.*
2. **RQ1, lowest-access groups (FinScope)**: sex, age, education, Ubudehe, urban/rural, farming status. *High (SE caveat).*
3. **RQ3, reported barriers**: FinScope `h7`, `k17`, `i7`, `g9`; AHS denial reasons (small n). *High / medium.*
4. **RQ4, farmers vs others**: FinScope `m1` directly; AHS comparison at aggregate level only. *High.*
5. **RQ6, geography**: province robust; district with CIs and sample sizes, no rankings. *Medium.*

RQ5 (vulnerability) is folded into #1 through EICV7 quintiles and poverty status.

## 8. Recommended direction

**"Banked but not financed": the agricultural credit gap.** Half of agricultural households (50.2%) hold a formal account yet have no formal loan, while 71.1% borrowed, mostly from tontines. The MVP is an evidence explorer (Option A) with an agricultural-household focus (Option D framed as needs, not creditworthiness). Survey-weighted logistic regression supplies adjusted associations; no individual credit score is produced.
