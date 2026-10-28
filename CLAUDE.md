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

Regenerate with `python analysis/key_findings.py`. These figures live in the README, the demo narration and the Evidence pages (never in the farmer zone).

## Product (updated 24 Oct 2026)

**Two zones, enforced by `tests/test_app.py` (decided 28 Oct).** One app, two kinds of page.
- **Evidence zone** (`ui/pages.py`, `ui/data.py`; nav group "Evidence": Overview, Who gets formal credit, Loan purposes and
  barriers, Farmers vs other adults, Districts, Data and methods): shows aggregate NISR statistics from `data/aggregates`
  with CIs, n < 30 suppression and a source note. It never reads or imports farmer records, share, vault, crypto, auth,
  lender or benchmark code, and never the microdata loader.
- **Farmer zone** (`src/records.py`, `share.py`, `vault.py`, `crypto.py`, `usedcodes.py`, `otp.py`, `ussd.py`,
  `benchmarks.py`, `ui/farmer.py`, `auth.py`, `lender.py`, `landing.py`): shows no survey statistic except the two
  allow-listed files `data/aggregates/yield_benchmarks.json` and `input_use.json`, read only through `src/benchmarks.py`.
  It never imports `ui/data.py` or `ui/pages.py`. Benchmark output (the harvest band) is computed on the fly, shown
  only to the farmer on screen, and NEVER written into a record, the JSON backup, the share file or the loan pack
  (tested). Every survey number shown to a farmer carries "AHS 2024, plots of the same crop and season, for guidance
  only". No "vulnerable" label, no savings advice, no fertilizer doses. The improved-seed share is labelled "seasonal-crop
  plots where seed type was recorded". The landing copy carries no percentage; Home has a "See the evidence" page link.
Nav order: Home; Evidence; For farmers (My farm records, USSD simulator, Open a farmer's report); About.
Pages: `Home` (landing, TypeScript + Tailwind), **for farmers** `My farm records`
(record harvests, sales, expenses, savings; seasonal summary with visible formulas; downloadable report; JSON backup,
nothing stored server-side) and the USSD simulator; **for lenders** `Open a farmer's report` (opens the locked `.fbshare` file a
farmer chose to share, with the farmer's one-time code: summary, details, all entries, evidence mix, what to check, questions to ask); `About`.
Auth (24 Oct): farmers sign in with phone + PIN; data is encrypted (scrypt + AES-256-GCM) in the browser's local
storage via a tiny JS bridge (`ui/auth.py`), never stored server-side; sharing is a locked file + single-use code (`src/share.py`, `src/usedcodes.py`); sign-up verifies the phone with a one-time code (`src/otp.py`, DEMO: shown on screen, no SMS gateway yet).
Verified lender accounts and a server audit log need a database and are NOT built. See `docs/security.md`.
Record fields (25 Oct): saving records carry a place in `item` (MoMo, Ibimina, SACCO, Bank); harvests may carry `retained_kg`
(kept at home); `offfarm` is a fifth kind (livestock, trade, casual labour...). Other income never enters the farm net; savings are shown
beside the repayment worksheet, never merged into a ratio; food value uses the farmer's own sale price per kg and skips crops with none.
Rules for the record tool: entries are self-reported unless the farmer says a receipt is held; `confirmed`
evidence is reserved for a future verifier and import files can never grant it; **no score, no lending
decision, ever**; claim no impact on loan approval without a pilot. Tests fail if the landing copy contains a
percentage or any `ui/` module reads survey data.

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
ui/theme.py           palette, CSS, hero banner, chart layout helper
ui/farmer.py          farmer tool and USSD preview
ui/lender.py          lender view of a shared farmer file
ui/auth.py            farmer sign-in, vault persistence bridge, lock-out, idle timeout
src/crypto.py         scrypt + AES-256-GCM primitives
src/vault.py          PIN-locked profile (create/unlock/reseal, PIN rules, lock-out)
src/share.py          encrypted share package + one-time code
ui/about.py           how it works, limits, link to the research
ui/landing.py         landing page: embeds the TypeScript + Tailwind bundle, injects numbers from aggregates
frontend/             Vite + TypeScript + Tailwind source for the landing page (npm run build -> ui/landing/landing.html)
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

1. **Never commit microdata** (`.dta`, `.zip`, `data/raw/`, `*.pkl`). The farmer zone reads no survey data except the two benchmark files above; the Evidence zone reads only `data/aggregates`.
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

## Backlog (priority order, updated 28 Oct from `docs/03_combined_build_plan.md` section 5)

Done: landing page, farmer tool, USSD preview, lender view (print stylesheet, session notes, evidence legend), about page.
Pipeline exports `yield_benchmarks.json` (B1) and `input_use.json` (B2) built 28 Oct; medians reproduce doc 03 within 2%.

1. **Deploy** both tools and cross-link them; have both URLs in hand before anything else (Insights/Records on Streamlit Community Cloud, `app.py`, Python 3.11+). Never cut.
2. DONE 28 Oct: F1 SACCO opportunity map (`ahs_district_opportunity.csv`, Evidence > "Where SACCOs could reach savers"). Next: F3 social protection lens; review the existing Recommendations page against doc 02 section 4 before re-adding it to the nav.
3. 29 Oct: B1 harvest peer comparison and B4 evidence levels in the record tool; B3 loan purpose sheet; recommendations page; README.
4. 30 Oct morning, only if all above is tested: B2 inputs reference, then B5 district shock exposure or F4 adjusted regression.
5. **Demo video** (<= 3 min, `docs/demo_script.md`; story: Insights finds the 759k, Records shows how one farmer prepares) and submit by early evening 30 Oct. Never cut.
6. Native-speaker review of every Kinyarwanda string (`src/i18n.py`).

Cut first if late: B5, F4, F5, B2. Never cut: deployment, README, demo video, tests passing.
Rule conflict resolved 28 Oct (see Product). Insights pages restored 28 Oct from e9c3c48^.

## Next (after 23 Oct)
Record-tool pilot plan with a SACCO and a cooperative; buyer/cooperative verification; consent-based sharing;
Kinyarwanda menus (native-speaker review required); real USSD gateway. Not in the hackathon build.
