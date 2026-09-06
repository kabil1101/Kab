# Making the brief arrive on time

## Why this is needed

The workflow has a schedule. GitHub does not honour it. Actions treats
`on: schedule` as best-effort and deprioritises it for low-activity
repositories, so across twelve consecutive briefs the run started between
**39 minutes and 11 hours 49 minutes late, median about 4.5 hours**. Nothing in
this repository can fix that — it is queueing on GitHub's side, before our code
runs at all.

What *does* fire immediately is a **manual dispatch**. So a timer outside
GitHub calls the dispatch API at 09:25 Lisbon, and the run starts within
seconds. The timer used here is a Google Apps Script trigger: free, no new
account, and it lives in the same Google account that already receives the
brief.

The workflow's two cron entries stay exactly as they are. They become the
fallback: if Google ever misses a morning, the late scheduled run still
delivers, and `state/latest.json` records the send so a schedule that fires
*after* Apps Script already delivered exits without emailing a second, staler
copy.

## What the token can do — measured, not assumed

`.github/workflows/probe-permissions.yml` asked GitHub directly, from a runner,
with three different permission sets:

| Token permission | Result |
|---|---|
| none | `HTTP 403` · `x-accepted-github-permissions: actions=write` |
| `Actions: write` | `HTTP 204` — dispatch accepted |
| `Contents: write` | `HTTP 403` · `x-accepted-github-permissions: actions=write` |

So the endpoint wants **`Actions: write` and nothing else**, and `Contents:
write` is not merely unnecessary — it is refused. That matters, because a
`Contents: write` token could push to `scripts/main.py`, which runs with
`GMAIL_APP_PASSWORD` in its environment; an `Actions: write` token cannot push
code, cannot edit a workflow, and cannot read a secret. Its worst case is
someone making the brief run more often than you want.

Re-run that workflow (**Actions → Probe Dispatch Permissions → Run workflow**)
if GitHub ever changes the requirement.

---

## Part 1 — Create the token (about 3 minutes)

1. Open <https://github.com/settings/personal-access-tokens/new>.
   (The long way round: your avatar, top right → **Settings** → scroll to
   **Developer settings** at the very bottom of the left menu → **Personal
   access tokens** → **Fine-grained tokens** → **Generate new token**.)
2. **Token name**: `market-brief-trigger`
3. **Expiration**: pick the longest offered, around 1 year. GitHub emails you
   before it expires; when it does, redo Part 1 and Part 3 step 3.
4. **Resource owner**: `kabil1101`
5. **Repository access**: select **Only select repositories**, then choose
   **Kab** from the dropdown. Not "All repositories".
6. **Permissions** → **Repository permissions** → find **Actions** in the list
   → set its dropdown to **Read and write**.
   *"Metadata: Read-only" appears on its own and cannot be removed. That is
   normal — every fine-grained token gets it.*
7. Leave every other permission on **No access**. Scroll down, click
   **Generate token**.
8. GitHub shows a string starting `github_pat_` **once**. Copy it now and keep
   the tab open until Part 3.

**Checkpoint.** The token summary should read: 1 repository (Kab), and
Repository permissions: Actions (read/write), Metadata (read). If it lists
anything else, click **Edit** and remove it.

## Part 2 — Create the Apps Script project (about 2 minutes)

1. Go to <https://script.google.com/home> and sign in as `kabil.dh@gmail.com`.
   Make sure that is the account shown top-right — this is the whole reason the
   token stays in your own infrastructure.
2. Click **New project**.
3. Click the project name at the top left (it says "Untitled project") and
   rename it **Market Brief Trigger**.
4. Click the **gear icon** (⚙ Project Settings) in the left sidebar.
5. Find **Time zone** and set it to **Lisbon**. This one is load-bearing:
   Apps Script fires timed triggers in the *project's* timezone, and the wrong
   one means a brief an hour early or late for half the year. The script
   refuses to install itself if this is not set to Europe/Lisbon.

**Checkpoint.** Project Settings shows Time zone = Lisbon.

## Part 3 — Store the token (about 2 minutes)

1. Still on **Project Settings**, scroll to the bottom: **Script Properties**.
2. Click **Add script property**.
3. **Property**: `GITHUB_TOKEN` (exactly, capitals and underscore)
   **Value**: paste the `github_pat_...` string from Part 1.
4. Click **Save script properties**.

**Checkpoint.** One property listed, named `GITHUB_TOKEN`. The token is now in
your Google account and nowhere else — it is never written into the code.

## Part 4 — Paste the code (about 2 minutes)

1. Click the **`<>` Editor** icon in the left sidebar.
2. Open [`trigger/apps-script.gs`](../trigger/apps-script.gs) in this
   repository and copy the whole file.
3. In the Apps Script editor, click inside `Code.gs`, select everything
   (`Ctrl+A` / `Cmd+A`) and paste over it.
4. Click the **floppy-disk Save** icon.

**Checkpoint.** No red error markers in the editor.

## Part 5 — Prove it works (about 3 minutes)

1. In the toolbar there is a function dropdown. Choose **`testNow`**.
   Not `sendBrief` — that one refuses to run at weekends, so on a Saturday or
   Sunday it would log "Weekend in Lisbon" and you would have no way to tell a
   correct setup from a broken token. `testNow` skips only that check.
2. Click **Run**.
3. Google asks for authorisation the first time:
   **Review permissions** → choose `kabil.dh@gmail.com` → the screen says
   "Google hasn't verified this app" → **Advanced** → **Go to Market Brief
   Trigger (unsafe)** → **Allow**.
   That warning appears for every unpublished personal script. The script is
   the one you just pasted, in your own account; there is no third party.
4. Watch the **Execution log** at the bottom. You want:
   `Brief dispatched 17:42 LIS.`
   Anything else is an error message that says what GitHub objected to.
5. Check <https://github.com/kabil1101/Kab/actions> — a **Daily Market Brief**
   run should be starting. The email follows in two to three minutes.

**Checkpoint.** The email arrives. Note that this is a real brief, so if
today's already came, you now have two — that is only true for this one test.

`testNow` is yours to run by hand any time you want a brief immediately. The
daily trigger never calls it, so it cannot cause a weekend delivery on its own.

## Part 6 — Install the daily trigger (1 minute)

1. In the function dropdown, choose **`install`**.
2. Click **Run**.
3. The log should read:
   `Installed: sendBrief runs daily near 09:25 Europe/Lisbon.`
   If instead it complains about the timezone, go back to Part 2 step 5.
4. Click the **clock icon** (⏰ Triggers) in the left sidebar to confirm: one
   trigger, `sendBrief`, Time-driven, Day timer, 9am to 10am.

`install` is safe to run again — it deletes its own previous trigger first, so
it cannot stack duplicates.

**Checkpoint.** Exactly one trigger listed.

---

## What to expect, and how to check it

Google's day timers fire **within about 15 minutes** of the requested minute,
so expect the brief between roughly **09:10 and 09:40 Lisbon**. Against a
4.5-hour median that is the problem solved; if you ever need
minute-precision, a Cloudflare Worker cron is the free alternative, at the cost
of a new account.

Every brief carries its own build time in the header line. **One good day
proves nothing** — the GitHub schedule was also only ~40 minutes late on its
first two days before degrading to 10+ hours. Read that line for a full week
and compare it against 09:25.

If a morning goes missing, Apps Script emails you: the script throws on any
response other than `HTTP 204`, and Google reports failed triggers to the
account owner. An expired token therefore announces itself rather than
appearing as a week of silence.

## Turning it off

Apps Script → **Triggers** (clock icon) → hover the row → **⋮** → **Delete
trigger**. The workflow's own crons keep running, late, as before.
