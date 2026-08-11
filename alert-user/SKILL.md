---
name: alert-user
description: Escalate user-attention reminders when Codex is blocked waiting for an explicit confirmation, approval, credential, browser interaction, hardware action, or other manual step. Use when the user asks Codex to keep calling, notify, wake, ping, or get their attention until they respond, or when a user-authorized persistent task cannot proceed without them. Start quietly, inspect available notification and audio channels, escalate one level at a time, and stop immediately after confirmation. Do not use for ordinary progress updates or without permission to send external alerts.
---

# Alert User

Escalate from a quiet notification to a loud, intense, bounded audiovisual attention burst. The user attested to healthy hearing and no photosensitivity — so the top levels are deliberately extreme: full-scale fire-truck sirens, 100% temporary system volume, and a rapid full-screen strobe.

## The Five Stages

Levels have names, because numbers are not urgent enough:

| Level | Name | Channels added |
| --- | --- | --- |
| 1 | The Serenade | Native notification plus the bundled audio clip played once |
| 2 | The Infinite Loop | Bring the task app forward; the second audio clip loops back-to-back |
| 3 | Fire Truck Incoming | Synthesized fire-truck yelp siren |
| 4 | Citywide Meltdown | Bounded dialog plus repeated fire-truck wail |
| 5 | TOTAL APOCALYPSE | Hi-lo siren at up to 100% volume plus a full-screen 16-24 Hz strobe |

## When to Alert

Alert only when ALL of these hold:

1. A user-authorized persistent task is blocked on a manual step only the user can do: a confirmation, approval, credential entry, login, browser interaction, hardware action, or similar.
2. The blocker is still unresolved — check first, every time.
3. The user has not responded since the blocker was raised.

Never alert for ordinary progress updates, finished steps, or anything the task can resolve on its own. One blocker, one heartbeat, no duplicate timers.

## Escalation Cadence

While a stage goes unanswered, repeat its alert at the stage's rhythm, then escalate exactly one stage. Thirty minutes without a response means TOTAL APOCALYPSE.

| Stage | Repeat alert every | Escalate after | Total elapsed |
| --- | --- | --- | --- |
| 1 The Serenade | 3 minutes | 6 minutes (2 unanswered) | 6 min |
| 2 The Infinite Loop | 4 minutes | 8 minutes (2 unanswered) | 14 min |
| 3 Fire Truck Incoming | 4 minutes | 8 minutes (2 unanswered) | 22 min |
| 4 Citywide Meltdown | 4 minutes | 8 minutes (2 unanswered) | 30 min |
| 5 TOTAL APOCALYPSE | 5 minutes, at most 3 bursts | Then back off to one reminder every 15 minutes | — |

Rules:

1. Start at stage 1 unless the user explicitly requested a starting stage.
2. Escalate by at most one stage per unanswered interval. Never skip a stage.
3. Record the current stage and the next allowed alert time in the task message so the heartbeat can resume correctly.
4. Any user response pauses escalation; an explicit confirmation stops the heartbeat immediately, restores any changed volume or output device, and ends the sequence.
5. If the response is ambiguous, hold the current stage and ask one concise question in chat.

## Workflow

1. State the exact action needed and the consequence of waiting.
2. Confirm the user authorized persistent reminders. Treat permission for notifications, sound, volume changes, device switching, and visual pulses as separate permissions.
3. Run a read-only preflight before the first sound alert:

   ```bash
   python3 scripts/alert_user.py preflight
   ```

4. Follow the escalation cadence above; read [references/escalation.md](references/escalation.md) for the heartbeat prompt invariants.
5. Preview every level 3-5 invocation with `--dry-run` before running it.
6. Send one alert, report the channel used, and wait for the stage's interval before alerting again or escalating.
7. For recurring reminders, create or update one thread heartbeat. Do not create duplicate timers. Its prompt must check for confirmation first and disable itself immediately after confirmation.
8. After the user confirms, stop the heartbeat, stop active alert processes, restore any changed volume or output device, and report completion.

## Commands

Resolve paths relative to this skill directory.

```bash
# Inspect audio outputs, default device, mute state, volume, and available helpers.
python3 scripts/alert_user.py preflight --json

# Level 1 (The Serenade): notification; with sound consent, play the bundled song once.
python3 scripts/alert_user.py alert --level 1 --allow-sound --title "Action needed" --message "Please confirm the result."

# Level 2 (The Infinite Loop): bring the app forward and loop the song nonstop.
python3 scripts/alert_user.py alert --level 2 --allow-sound --title "Still waiting" --message "Please return and confirm."

# Level 3 (Fire Truck Incoming): foreground notification plus the yelp siren.
python3 scripts/alert_user.py alert --level 3 --allow-sound --title "Still waiting" --message "Please return and confirm."

# Level 5 (TOTAL APOCALYPSE) preview. Visual and volume permissions are intentionally explicit.
python3 scripts/alert_user.py alert --level 5 --allow-sound --allow-dialog --allow-visual-pulse --dry-run
```

Use `--allow-volume-change --target-volume N` only when the user explicitly authorized a temporary volume change. The script caps `N` at 100 and restores the original setting. Use `--device NAME --allow-device-switch` only for a device the user selected; never rotate through devices automatically.

## Permission Boundaries

- Treat notification permission as the baseline only.
- Require explicit sound permission before `--allow-sound`.
- Require explicit permission in the current task before changing volume, switching output devices, or showing a visual strobe.
- Never unmute silently, cycle every output, defeat Focus/Do Not Disturb, or keep an alert process alive indefinitely.
- Never run visual strobes faster than the script's 24 Hz cap or longer than its 60-second cap. The user attested to no photosensitivity; do not use the visual strobe around anyone else who has not.
- Do not alert when the user said they are driving, sleeping, presenting, in a call, or in a safety-sensitive setting.
- Stop on any equivalent of "confirmed", "done", "stop", "cancel", or "mute".

Read [references/safety.md](references/safety.md) before changing volume, selecting an output device, or using level 5.

## Scores

The synthesized alarm reads JSON scores. Levels 1-2 play the bundled MP3 clips (`assets/audio/1.mp3`, `assets/audio/2.mp3`) through the OS player; levels 3-5 select bundled original fire-truck siren scores (yelp, wail, hi-lo) rendered with a harsh harmonic-rich waveform at near full scale. Pass a user-owned/licensed score with `--score PATH`. Do not fetch or reconstruct copyrighted melodies. Musical notation is still protected expression; a score is not a copyright workaround.

```bash
python3 scripts/synth_alarm.py --score assets/scores/fire-truck-wail.json --output /tmp/alert-user.wav
```

## Failure Handling

- If native notifications fail, report the failure and stay in chat; do not silently jump to a louder level.
- If no physical audio output is detected, do not use a virtual device automatically. Ask the user to choose an output.
- If sound playback fails, retain notification/dialog channels and report the exact missing helper.
- If the graphical session or Tk is unavailable, skip the visual pulse and continue with the already authorized channels.
