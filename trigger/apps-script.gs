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

// The PM edition anchors to New York, not Lisbon: the point of it is to land
// before the US cash open, and that moment is a New York time. 08:00 New York
// is 30 minutes before the 08:30 prints and 90 minutes before the open.
const NY_TZ = 'America/New_York';
const PM_TARGET_NY_HOUR = 8;

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
const SCRIPT_VERSION = '8';

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
 * Fired by the two PM timers. Sends the afternoon delta - but only from the
 * one of them that lands on 08:xx in New York today.
 *
 * Why two timers and a guard, rather than one timer at the right hour: Apps
 * Script fires in the PROJECT's timezone, which is Lisbon, and the
 * Lisbon-to-New-York gap is 4, 5 or 6 hours depending on the week. The US and
 * the EU change clocks on different dates, so any single Lisbon hour is the
 * wrong New York hour for about two weeks a year. This is the same two-slot
 * pattern the workflow already uses for the morning cron, and it is here for
 * the same reason.
 *
 * The guard reads New York's current hour from the clock rather than assuming
 * an offset. That is deliberate: this project has already paid once for
 * hardcoding one.
 */
function sendPm() {
  const nyHour = Number(Utilities.formatDate(new Date(), NY_TZ, 'H'));
  if (nyHour !== PM_TARGET_NY_HOUR) {
    console.log('New York is ' + nyHour + ':xx, not ' + PM_TARGET_NY_HOUR +
                ':xx. The other slot owns today. Exiting.');
    return;
  }
  dispatch('pm');
  console.log('PM delta dispatched (trigger v' + SCRIPT_VERSION + ').');
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
function dispatch(edition) {
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
      inputs: {trigger_version: SCRIPT_VERSION, edition: edition || 'am'}
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
    const fn = t.getHandlerFunction();
    if (fn === 'sendBrief' || fn === 'sendPm') {
      ScriptApp.deleteTrigger(t);
    }
  });

  ScriptApp.newTrigger('sendBrief')
      .timeBased()
      .everyDays(1)
      .atHour(9)
      .nearMinute(25)
      .create();

  // Two PM slots, one New York hour. 13:00 Lisbon is 08:00 New York while the
  // clocks agree; 12:00 Lisbon is 08:00 New York in the two mismatch weeks
  // when they do not. sendPm() checks which is which and the wrong one exits.
  //
  // nearMinute(0) narrows Google's window to roughly +-15 minutes instead of
  // the whole hour, which is what keeps this ahead of the 08:30 prints rather
  // than a coin flip against them.
  [12, 13].forEach(function(hour) {
    ScriptApp.newTrigger('sendPm')
        .timeBased()
        .everyDays(1)
        .atHour(hour)
        .nearMinute(0)
        .create();
  });

  console.log('Installed: sendBrief near 09:25 ' + TZ + ', and sendPm at ' +
              '12:00 and 13:00 ' + TZ + ' with a New York guard so exactly ' +
              'one of them sends. Seven days a week.');
}
