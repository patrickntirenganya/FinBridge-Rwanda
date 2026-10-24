# Security and privacy design

FinBridge handles farmers' income records, which are personal and financial data. This note says what we protect,
how, and, just as important, what we do not and cannot protect. It is written for judges, lenders and reviewers.

## Principles

1. **Data minimisation.** No server database. Records are kept in the farmer's own browser (encrypted) and in server
   memory only while the farmer is signed in. Nothing is written to disk, logged or sent elsewhere.
2. **Consent first.** A lender sees records only when the farmer creates a share, chooses what it contains and gives
   the lender a one-time code. Names of buyers and sellers are left out unless the farmer ticks the box.
3. **Easy for farmers, strong underneath.** Phone number + PIN on the surface; scrypt and AES-256-GCM underneath.
4. **No decisions.** The tool gives no score and no verdict, so a security failure cannot, for example, deny a loan.

## What is implemented

| Area | Mechanism | Where |
|---|---|---|
| Key derivation | scrypt (N=2^16, r=8, p=1, 64 MB, ~0.4 s) from PIN + phone, 16-byte random salt per vault | `src/crypto.py` |
| Encryption | AES-256-GCM, fresh random 96-bit nonce per save, purpose bound as associated data (a vault cannot be opened as a share and vice versa) | `src/crypto.py` |
| Farmer profile ("vault") | Encrypted JSON in browser local storage and in a downloadable `.fbvault` backup | `src/vault.py`, `ui/auth.py` |
| PIN rules | 4 to 6 digits; rejects repeated digits (1111), counting runs (1234, 4321) and the end of the phone number | `src/vault.py` |
| Guess lock-out | After 4 wrong tries: 30 s, doubling to 15 min. Same wording for wrong phone, wrong PIN or damaged file | `src/vault.py`, `ui/auth.py` |
| Session | Key and data live in session memory only; cleared on Lock, leaving the page's session, and after 15 minutes idle | `ui/auth.py` |
| Sharing | Farmer creates an encrypted `.fbshare` with a random 12-character code (about 59 bits, no confusable letters), chosen period, optional names, 1/7/30-day validity | `src/share.py` |
| Share opening | Code attempts are rate-limited; expiry is stored inside the authenticated data; contents are re-validated like any import and can never carry `confirmed` evidence | `src/share.py`, `ui/lender.py` |
| Untrusted input | Every imported file goes through `records.parse_import` (known fields and types only); farmer text shown on the lender page is HTML-escaped | `src/records.py`, `ui/lender.py` |
| Browser bridge | A ~30-line JavaScript component copies opaque strings to and from local storage. It never sees a PIN or a record, and no user text is ever put into its code | `ui/auth.py` |
| Tests | Wrong PIN/phone/code, tampering, junk files, nonce reuse, lock-out schedule, expiry, hostile text, plaintext leakage into vault and share | `tests/test_app.py` |

## Threats and what we do about them

| Threat | Response | Residual risk |
|---|---|---|
| Someone picks up the phone and guesses the PIN in the app | Lock-out grows to 15 minutes; idle timeout; Lock button | Low |
| Someone **copies the vault** (browser storage or a backup file) and guesses the PIN offline | Slow key derivation (~0.4 s per guess); trivial PINs refused; advice to use 6 digits and keep backups private | **Real.** A 4-digit PIN falls in about an hour of computing on one core, 6 digits in about 4 days. A PIN cannot be made as strong as a passphrase. Phone screen lock and a 6-digit PIN matter |
| Anyone with the share file guesses the code | 59-bit random code with the same slow key derivation | Negligible |
| A lender keeps what they saw | Not preventable in any system that shows data (same as a printed report). The farmer is told this before sharing; the code is shown once; shares expire; names are off by default | Accepted; consent-based |
| Lender impersonates an institution | Lenders do not have accounts yet, so identity is not verified; the optional institution name appears only on the lender's own access receipt | **Open.** Needs a database (see below) |
| Phone number belongs to someone else | The number is a label, not verified (no SMS). It cannot unlock anything without the PIN | Open until an SMS gateway is added |
| Malicious file or hostile text (XSS) | Strict parsing, escaped output, no user text in script or HTML | Low |
| Server operator reading records | They exist in server memory while a farmer is signed in (the app must compute on them). Never stored or logged. Fully client-side processing would remove this | Accepted for the prototype |
| Lost phone or forgotten PIN | No recovery by design (we hold no key). Restore from the locked backup with the old PIN | Data loss if there is no backup |

## What we do not claim

- It is a prototype, not an audited product. No independent security review has been done.
- A verified lender identity, a server-side audit log and revocable access need a small database. That is the planned
  next step (lender accounts with email and password, and a log of every share opened).
- The farmer's phone number is not verified.
- Expiry of a share is enforced by FinBridge when it opens the file, not by the file itself.

## Data-protection notes

The design follows the usual data-protection principles (purpose limitation, minimisation, consent, security) that
Rwanda's personal data protection law also expects. It has not been reviewed by a lawyer, and any real deployment
would need a registered controller, a privacy notice in Kinyarwanda and a data-protection impact assessment.
