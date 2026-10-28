# Demo video script

**Target length: 2 minutes 50 seconds (hard limit 3:00). Screen-recorded with voice-over. Deliver as `.webm`.**

The farmer pages show no survey statistics. The Evidence pages do; show one (Overview) for a few seconds at the start,
then move to the farmer tool. The full numbers are in the README.

**Story in one line:** farmers have accounts but no way to show their income; FinBridge lets them keep records they
own and share by choice, and lets a lender read those records without scores or decisions.

---

## 1. Scene-by-scene plan

Speaking pace is about 145 words a minute. Each scene lists what to click, then the words to say. Say the words while
you click; do not wait in silence.

| # | Time | Screen and clicks | Narration | Words |
|---|---|---|---|---|
| 1 | 0:00–0:20 | **Home.** Hero visible, mouse still. | "Most Rwandan farmers already have a bank or SACCO account, but about half of farm households have no formal loan. Lenders can't see what a farm earns, and farmers have nothing to show them. We found this gap in NISR's survey data. FinBridge is the solution." | 46 |
| 2 | 0:20–0:30 | **Home.** Scroll slowly past *For farmers*, *For lenders* and the phone section. | "Farmers keep simple records on any phone. Lenders read what a farmer chooses to share. No scores. No loan decisions." | 20 |
| 3 | 0:30–0:45 | Click **Start recording**. The sign-in screen appears. Pause one second on it, then click **Just looking? Try the demo**. | "A farmer signs in with a phone number and a PIN. Their records are encrypted and stay on their own phone, not on our server. For this demo I'll use the demo profile." | 33 |
| 4 | 0:45–1:10 | **My farm records.** Click **I sold**, click **Maize**, click the money box and type **50000**, click **Save**. Hold on the green confirmation. | "Recording takes three taps: what happened, which crop, and how much. Big buttons, plain words, in Kinyarwanda or English. The farmer sees a clear confirmation." | 25 |
| 5 | 1:10–1:20 | Click the tab **2 · My summary**. | "The summary is a plain sentence, with the sums shown. Nothing is a black box." | 15 |
| 6 | 1:20–1:45 | Click the tab **3 · Share**. Leave **7 days** and the names box **off**. Click **Create a share**. Point at the code, then click **Download the locked file**. | "When the farmer chooses to apply for credit, they share. Buyer names are off by default. They get a locked file and a one-time code, and give the code to the lender separately. Nothing goes through our server." | 38 |
| 7 | 1:45–2:25 | Open **Open a farmer's report**. Choose the downloaded file, type the code, click **Open**. Pause on **At a glance** (the story). Scroll to the money in and out chart. Click **Repayment worksheet**, then stop on the chart. | "The lender opens the file with the code. FinBridge turns the records into a plain story: income, costs, where the money came from. Charts show money in and out each month. The repayment worksheet lets the lender set a loan, and compare the farmer's recorded income with the monthly repayment. There is no score and no verdict. The lender decides." | 60 |
| 8 | 2:25–2:40 | Open **Basic-phone (USSD) preview**. Type **1**, send; **1**, send; **50000**, send; **30**, send. | "Not every farmer has a smartphone, so the same tool runs on any phone by USSD, with the same records and the same rules." | 24 |
| 9 | 2:40–2:50 | Open **About** (limits visible), then the README or GitHub page for one second. | "FinBridge: farm records farmers own and lenders can read. Limits, security and the research are open on GitHub." | 18 |

Total narration is about 280 words, roughly 1:55 of speaking, which leaves room for clicks and pauses inside the
2:50. If you finish early, that is fine. If you run long, use the cut list in section 5.

---

## 2. Before you record (preflight)

Do this once, 10 minutes before.

**Prepare the app**
- Run the app (`streamlit run app.py`) or open the deployed link. Use the **English** interface for the main take.
- Open it in a **clean browser window**: close other tabs, hide the bookmarks bar, turn on *Do Not Disturb*, and quit
  chat and email apps so no notification appears.
- Your screen is 1366×768. Set the browser zoom to **100%** (use 110% only if text looks small after you test).
- Keep the sidebar visible; it shows the Home, farmers and lenders structure.
- Use the **demo profile**, not a real farmer or a real phone number. Never show real personal data.

**Do a dry run of the share file**
1. Open *My farm records*, click **Try the demo**, then in the *Share* tab click **Create a share**.
2. Click **Download the locked file** and note where it lands (usually `~/Downloads/finbridge_share.fbshare`).
3. Delete that file afterwards, so the real take downloads a fresh one with a fresh code.

**Know the file picker.** In scene 7 the file dialog opens. Practise choosing `finbridge_share.fbshare` quickly. Keep
the dialog on your *Downloads* folder so it appears already in place.

**Reset between takes.** Reload the page, or click **Leave the demo** and open the lender page's **Close this report**
button so both sides start empty.

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
3. After scene 9, count to two, then **Stop Recording**. The file is in your `Videos` folder.

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
- **No numbers you cannot defend.** The only figure is "about half of farm households", from the README.
- **Never promise results.** Do not say it "gets farmers loans". Say it "gives lenders something to read".
- **Do not call anything a score or approval.** The tool does neither, and saying it clearly is a strength.

If a native Kinyarwanda speaker can record a second, shorter version (scenes 1, 3, 4, 6, 9), it makes the pitch
stronger for local judges. Have them review the wording first.

---

## 5. If something goes wrong

| Problem | Fix |
|---|---|
| The file picker is slow or fails | In scene 7, click **See an example farmer** instead, and say "In a real case the lender opens the farmer's file with the code." Cut the file step |
| Over 3:00 | Cut scene 2 (10 s) and shorten scene 8 to the menu only (save 8 s) |
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
