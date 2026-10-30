# Demo video script

**Target length: 2 minutes 47 seconds (hard limit 3:00). Screen-recorded with voice-over. Deliver as `.webm`.**

**Story in one line:** the evidence shows where Rwanda's farmers are banked but not financed, and the farmer tools are
the response. The Evidence pages show survey statistics; the farmer pages do not.

**Narration note.** The spoken line in scene 7 ("no database or account on our server; what's saved is an encrypted
copy in the farmer's own browser") is true. Do not widen it to "the server never sees the data" or "records never
leave the phone": while a farmer is signed in, the records sit in the app's memory for that session. Do not call the
share code "one-time forever": it works once while the app keeps running (see `docs/security.md`).

---

## 1. Scene-by-scene plan

Speaking pace is about 145 words a minute (2.4 words a second). Each row gives the clicks, then the words to say. Say
the words while you click. Times include the clicking, so they run longer than the speech alone.

| # | Time | Screen and clicks | Narration | Words |
|---|---|---|---|---|
| 1 | 0:00–0:12 | **Home.** Hero visible, mouse still. | "FinBridge uses NISR's Agricultural Household Survey and FinScope 2024 to show where Rwanda's farmers are banked but not financed, and gives farmers a tool to respond." | 26 |
| 2 | 0:12–0:34 | Click **See the evidence**. On **Overview**, hover the red segment of the bar, then rest on the three figure cards. | "62.7% of farm households have a bank, SACCO or microfinance account, but only 14.1% have a formal loan. About 759,000 households hold a formal account yet borrowed only from informal sources. Every figure is weighted with a confidence range, and the household figures reproduce NISR's published tables." | 47 |
| 3 | 0:34–0:54 | Click **Where SACCOs could reach savers**. Hover **Nyagatare**, point at the grey Kigali districts, then scroll to **Tontines: an existing bridge** and rest on the three figures. | "The map shows which districts they are in, and hides districts with too few respondents. Eight in ten farm households have a member in a tontine, and more than half of tontine borrowers already have a SACCO account." | 38 |
| 4 | 0:54–1:08 | Click **Social protection and finance**. Rest on the first chart (bank account bars). | "Adults in households receiving VUP cash transfers have bank accounts at 7%, against 21% for everyone else. That is an association, not an effect of the programme." | 27 |
| 5 | 1:08–1:22 | Click **What the evidence suggests**. Scroll slowly past cards 1 and 2 so the *Finding* and *Hypothesis* lines are visible. | "NST2 aims to raise agriculture's share of national lending from 6 to 10 percent by 2029. Each recommendation separates what the data show from what still needs a pilot." | 29 |
| 6 | 1:22–1:30 | Click **My farm records**, then **Just looking? Try the demo**. | "The response is a record tool. Here we use invented demo records." | 12 |
| 7 | 1:30–1:43 | Click **I sold**, **Maize**, click the money box and type **50000**, click **Save**. Hold on the green confirmation. | "Recording a sale takes three taps. There's no database or account on our server; what's saved is an encrypted copy in the farmer's own browser." | 25 |
| 8 | **CUT** | _(Tab **4 · Harvest check**: Maize, Season A, 500 kg, 1 hectare.)_ Cut first: with it the video runs 3:02. | _"A harvest check compares this harvest with similar survey plots, for guidance only, and is never saved or shared."_ | 19 |
| 9 | 1:43–1:58 | Click tab **5 · Loan plan** (already filled with the example). Scroll once to show purpose, items, cost and repayment. | "A loan plan states what the money is for and how it would be repaid, since an unclear purpose is among the most common reasons loans are refused. It does not guarantee a loan." | 34 |
| 10 | 1:58–2:12 | Click tab **3 · Share**. **Tick "Include my loan plan"**, click **Create a share**, click **Download the locked file (.fbshare)**. Point at the code. | "To apply, the farmer shares a locked file and a separate code. The loan plan goes only if they choose." | 20 |
| 11 | 2:12–2:39 | Open **Open a farmer's report**. Choose the downloaded file, type the code, click **Open**. Rest on **At a glance**, then click **Repayment worksheet** (the loan plan is at the top). | "The lender sees the farmer's story, the loan plan and a repayment worksheet. No score, no decision. Entries are self-reported, and references are marked not checked." | 26 |
| 12 | 2:39–2:47 | Open **About**, then the GitHub page for one second. | "FinBridge: evidence for policy, records farmers own. Code, methods and limits are on GitHub." | 14 |

**Totals.** Narration with scene 8 cut is 298 words, about 2:03 of speech, inside a 2:47 timeline. With scene 8 kept
the narration is 317 words and the timeline is about 3:02, which is over the limit, so scene 8 stays out.

**If your take runs over 2:50:** shorten scene 5 to the NST2 sentence only (saves about 6 s). Do not cut scenes 10
and 11: sharing and the lender view are the core of the product.

### Narration only (to read straight through)

"FinBridge uses NISR's Agricultural Household Survey and FinScope 2024 to show where Rwanda's farmers are banked but not financed, and gives farmers a tool to respond.

62.7% of farm households have a bank, SACCO or microfinance account, but only 14.1% have a formal loan. About 759,000 households hold a formal account yet borrowed only from informal sources. Every figure is weighted with a confidence range, and the household figures reproduce NISR's published tables.

The map shows which districts they are in, and hides districts with too few respondents. Eight in ten farm households have a member in a tontine, and more than half of tontine borrowers already have a SACCO account.

Adults in households receiving VUP cash transfers have bank accounts at 7%, against 21% for everyone else. That is an association, not an effect of the programme.

NST2 aims to raise agriculture's share of national lending from 6 to 10 percent by 2029. Each recommendation separates what the data show from what still needs a pilot.

The response is a record tool. Here we use invented demo records.

Recording a sale takes three taps. There's no database or account on our server; what's saved is an encrypted copy in the farmer's own browser.

A loan plan states what the money is for and how it would be repaid, since an unclear purpose is among the most common reasons loans are refused. It does not guarantee a loan.

To apply, the farmer shares a locked file and a separate code. The loan plan goes only if they choose.

The lender sees the farmer's story, the loan plan and a repayment worksheet. No score, no decision. Entries are self-reported, and references are marked not checked.

FinBridge: evidence for policy, records farmers own. Code, methods and limits are on GitHub."

### Where each spoken number comes from

| Said in the video | Value | Source |
|---|---|---|
| "62.7% ... account" | 62.7% | AHS 2024; matches NISR Main Report Table 32 |
| "14.1% ... formal loan" | 14.1% | AHS 2024, weighted |
| "About 759,000 households" | 35.1% of 2.16 M households | AHS 2024 (account, borrowed only informally) |
| "Eight in ten ... tontine" | 81.1% (CI 79.2–83.1) | AHS 2024 |
| "More than half of tontine borrowers ... SACCO account" | 57.8% (CI 55.3–60.2, n = 1,850) | AHS 2024 |
| "7% against 21%" | 7.1% vs 21.3% bank account | FinScope 2024, VUP transfer households (n = 1,078); intervals understated |
| "6 to 10 percent by 2029" | NST2 and PSTA5 target | MINAGRI; it is about loan value, so say it only as context |
| "among the most common reasons loans are refused" | unclear purpose 29.7% of 295 refusals | AHS 2024; wide intervals |

---

## 2. Before you record (preflight)

Do this once, 10 minutes before.

**Prepare the app**
- Run the app (`streamlit run app.py`) or open the deployed link a few minutes early so it is awake. Use the
  **English** interface for the main take.
- Open it in a **clean browser window**: close other tabs, hide the bookmarks bar, turn on *Do Not Disturb*, and quit
  chat and email apps so no notification appears.
- Your screen is 1366×768. Set the browser zoom to **100%** (use 110% only if text looks small after you test).
- Keep the sidebar visible; it shows the Evidence and farmer groups.
- Use the **demo profile**, not a real farmer or a real phone number. Never show real personal data.

**Do a dry run of the share file (this is scene 10, and it makes scene 11 work)**
1. Open *My farm records*, click **Try the demo**, then open the *Share* tab.
2. **Tick "Include my loan plan"**, click **Create a share**, click **Download the locked file (.fbshare)** and note
   where it lands (usually `~/Downloads/finbridge_share.fbshare`).
3. Delete that file afterwards. A code works once while the app is running, so the real take needs a fresh file and
   a fresh code. If you forget to tick the box, scene 11 will show "the farmer did not include a loan plan".

**Know the file picker.** In scene 11 the file dialog opens. Practise choosing `finbridge_share.fbshare` quickly. Keep
the dialog on your *Downloads* folder so it appears already in place.

**Reset between takes.** Reload the page, or click **Leave the demo**, and press the lender page's **Close this
report** button so both sides start empty. Open each Evidence page once before the take, so charts are cached.

---

## 3. Recording on your machine (Ubuntu 22.04, GNOME, Wayland, OBS)

You have OBS installed. The built-in GNOME recorder can stop early, so OBS is the safer choice.

**One-time OBS setup**
1. Open OBS. **Settings → Video:** Base and Output resolution `1366x768`, FPS `30`.
2. **Settings → Output → Recording:** Recording Format `mkv` (it survives a crash), Encoder `x264`, Rate control `CRF`
   with value `23`.
3. **Settings → Audio:** pick your microphone as *Mic/Auxiliary*. Speak a test line and check the meter peaks around
   the yellow zone, not red.
4. In **Sources**, click **+**, choose **Screen Capture (PipeWire)**, and in the system dialog choose your screen (or
   the browser window). This is the Wayland-friendly source.
5. Do a 10-second test, play it back, and confirm there is sound and the text is sharp.

**Record**
1. Click **Start Recording**. Count to two in silence.
2. Follow the table, speaking as you click. Move the mouse slowly and keep it still when you want viewers to read.
3. After scene 12, count to two, then **Stop Recording**. The file is in your `Videos` folder.

**Convert to `.webm`** (the submission needs `.webm` or `.gif`)

```bash
sudo apt install ffmpeg
ffmpeg -i ~/Videos/your_recording.mkv -c:v libvpx-vp9 -crf 33 -b:v 0 -c:a libopus demo.webm
```

If the file is too large, raise `-crf` to `36`. For a silent preview GIF, optionally:
`ffmpeg -i demo.webm -vf "fps=10,scale=960:-1" -loop 0 demo.gif`.

**Check the result**
- Plays in a browser (drag `demo.webm` into Firefox or Chrome).
- Length is **under 3:00** (`ffprobe demo.webm` or the browser's seek bar).
- Voice is clear, and no notification, password or real phone number is visible.

---

## 4. Voice and delivery

- **Warm and plain.** Say it as if telling a SACCO manager, not reading. Short sentences.
- **Say it slightly slower than feels natural**; screen recordings feel fast.
- **Do not read the screen aloud.** Say why it matters, let the screen show what it is.
- **No numbers you cannot defend.** Say only the figures in the table "Where each spoken number comes from" in section 1.
- **Never promise results.** Do not say it "gets farmers loans". Say it "gives lenders something to read".
- **Do not call anything a score or approval.** The tool does neither, and saying it clearly is a strength.

If a native Kinyarwanda speaker can record a second, shorter version (scenes 1, 3, 4, 6, 9), it makes the pitch
stronger for local judges. Have them review the wording first. Good scenes to translate: 1, 3, 4, 6, 10.

---

## 5. If something goes wrong

| Problem | Fix |
|---|---|
| The file picker is slow or fails | In scene 11, click **See an example farmer** instead, and say "In a real case the lender opens the farmer's file with the code." Cut the file step |
| Over 3:00 | Scene 8 is already cut. Then shorten scene 5 to the NST2 sentence only (saves about 6 s) |
| Sound is quiet or noisy | Re-record only the narration over the finished screen capture with OBS or Audacity, and mux with `ffmpeg` |
| A wrong click | Keep going and trim later, or reload and restart the scene. Take 2 to 3 attempts |
| The app is asleep (Streamlit Cloud) | Open the link a few minutes before and click the wake button |
| Wi-Fi drops (deployed app) | Record from the local copy instead (`streamlit run app.py`); it behaves the same |

---

## 6. What the judges should walk away with

1. **The problem is real and measured**: access without credit, and a missing paper trail.
2. **The product is a direct, working response**: farmer records, consent-based sharing, a lender view.
3. **It fits real users**: any phone, plain words, Kinyarwanda first, a PIN instead of passwords.
4. **It is honest**: no score, no verdict, limits stated openly.

## 7. After recording

- Put the video link in the README (`Demo video` row) and in the submission form.
- Commit the final `demo.webm` only if the file is small; otherwise upload it and link it.
- Tell the team the deployed app link so it appears next to the video.
