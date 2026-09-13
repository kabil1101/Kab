/**
 * On-time trigger for the daily market brief.
 *
 * GitHub's own scheduler is the reason this file exists. `on: schedule` is
 * best-effort and deprioritised for low-activity repositories: across twelve
 * consecutive briefs it ran between 39 minutes and 11h49m late, median about
 * 4.5 hours. A brief that arrives at lunchtime is not a morning brief.
 *
 * So the schedule stops being the primary sender and becomes the fallback.
 * This script, running on Google's timers inside the same account that
 * receives the brief, fires the run at 09:25 Lisbon. The workflow's crons stay
 * registered; if Google ever misses, the late scheduled run still delivers,
 * and `state/latest.json` stops it sending a second copy on a day the brief
 * already went out.
 *
 * The token
 * ---------
 * Tested from an Actions runner rather than assumed: the dispatch endpoint
 * answers a 403 with `x-accepted-github-permissions: actions=write`, and a
 * token holding only `Contents: write` is refused. So this needs exactly one
 * fine-grained permission — Actions: Read and write, on this repository alone.
 * That permission cannot push code, cannot edit a workflow, and cannot read a
 * secret. Its worst case is someone making the brief run more often than
 * wanted. It is not equivalent to the Gmail password, and it is never written
 * into this file — it lives in Script Properties.
 *
 * Setup is in docs/trigger-setup.md.
 */

const OWNER = 'kabil1101';
const REPO = 'Kab';
const WORKFLOW = 'market-brief.yml';
const REF = 'claude/daily-market-brief-kvfi35';
const TZ = 'Europe/Lisbon';

/**
 * Which version of this file is actually installed.
 *
 * This file lives in the repository; the copy that runs lives in a Google
 * account and is updated by pasting. On 12 September 2026 those two drifted:
 * the weekend guard was removed here, never re-pasted there, and the brief
 * stopped arriving at weekends. Nothing detected it - the workflow was simply
 * never asked to run, so there was no failure anywhere to notice.
 *
 * So the script now says which version it is on every dispatch, and the brief
 * compares that against EXPECTED_TRIGGER_VERSION in scripts/health.py. If you
 * change this file, bump both.
 */
const SCRIPT_VERSION = '7';

/**
 * Fired by the time-driven trigger. Asks GitHub to run the brief now.
 *
 * Seven days a week since 2026-09-12. The weekday-only guard that used to
 * live here was inherited from the cash session, but the brief has never been
 * about the cash session alone - crypto, funding and open interest run
 * through the weekend, and Monday's setup is built on what happened during it.
 */
function sendBrief() {
  dispatch();
}

/**
 * Send a brief right now, by hand. Identical to the scheduled path - it
 * exists so the setup can be proved the day it is done, and so a brief can be
 * pulled on demand without waiting for tomorrow morning.
 */
function testNow() {
  dispatch();
  console.log('If a brief lands in the next few minutes, the setup is done.');
}

/**
 * The actual call. Throws with GitHub's own words on anything but success.
 */
function dispatch() {
  const token = PropertiesService.getScriptProperties()
      .getProperty('GITHUB_TOKEN');
  if (!token) {
    throw new Error(
        'Script property GITHUB_TOKEN is missing. Project Settings → ' +
        'Script Properties → add GITHUB_TOKEN with the fine-grained PAT.');
  }

  const url = 'https://api.github.com/repos/' + OWNER + '/' + REPO +
              '/actions/workflows/' + WORKFLOW + '/dispatches';
  const res = UrlFetchApp.fetch(url, {
    method: 'post',
    contentType: 'application/json',
    headers: {
      Authorization: 'Bearer ' + token,
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28'
    },
    payload: JSON.stringify({
      ref: REF,
      inputs: {trigger_version: SCRIPT_VERSION}
    }),
    // Read the status ourselves so a refusal produces a message that says
    // what GitHub actually objected to.
    muteHttpExceptions: true
  });

  const code = res.getResponseCode();
  if (code !== 204) {
    // Throwing is deliberate. Apps Script emails the account owner when a
    // trigger fails, so a broken or expired token announces itself instead of
    // being discovered as a week of missing briefs.
    throw new Error(
        'GitHub refused the trigger: HTTP ' + code + ' — ' +
        res.getContentText().slice(0, 300) +
        ' (wanted: ' + res.getHeaders()['x-accepted-github-permissions'] + ')');
  }
  console.log('Brief dispatched ' +
              Utilities.formatDate(new Date(), TZ, 'HH:mm') + ' LIS' +
              ' (trigger v' + SCRIPT_VERSION + ').');
}


/**
 * Run this once, by hand, to install the daily trigger. Safe to re-run: it
 * clears its own previous trigger first, so it cannot stack duplicates.
 */
function install() {
  const projectTz = Session.getScriptTimeZone();
  if (projectTz !== TZ) {
    // Time-driven triggers fire in the *project's* timezone, not this
    // constant's. Getting that wrong is an hour-off brief twice a year, and it
    // would look like a bug in the brief rather than in the trigger.
    throw new Error(
        'Project timezone is ' + projectTz + ', not ' + TZ + '. Fix it under ' +
        'Project Settings → Time zone, then run install() again.');
  }

  ScriptApp.getProjectTriggers().forEach(function(t) {
    if (t.getHandlerFunction() === 'sendBrief') {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger('sendBrief')
      .timeBased()
      .everyDays(1)
      .atHour(9)
      .nearMinute(25)
      .create();

  console.log('Installed: sendBrief runs daily near 09:25 ' + TZ +
              ', seven days a week.');
}
