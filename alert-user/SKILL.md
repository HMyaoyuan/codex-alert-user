---
name: alert-user
description: Escalate user-attention reminders when Codex is blocked waiting for an explicit confirmation, approval, credential, browser interaction, hardware action, or other manual step. Use when the user asks Codex to keep calling, notify, wake, ping, or get their attention until they respond, or when a user-authorized persistent task cannot proceed without them. Start quietly, inspect available notification and audio channels, escalate one level at a time, and stop immediately after confirmation. Do not use for ordinary progress updates or without permission to send external alerts.
---

# Alert User

Escalate from a quiet notification to a loud, intense, bounded audiovisual attention burst. This fork is configured for a user who attested to healthy hearing, no photosensitivity, and who wears sound-isolating earmuffs — so the top levels are deliberately extreme: full-scale fire-truck sirens, 100% temporary system volume, and a rapid full-screen strobe.

## The Five Stages

Levels have names, because numbers are not urgent enough:

| Level | Name | Channels added |
| --- | --- | --- |
| 1 | The Serenade | Native notification plus the bundled song played once |
| 2 | The Infinite Loop | Bring the task app forward; the song loops back-to-back up to 5 minutes |
| 3 | Fire Truck Incoming | Synthesized fire-truck yelp siren |
| 4 | Citywide Meltdown | Bounded dialog plus repeated fire-truck wail |
| 5 | TOTAL APOCALYPSE | Hi-lo siren at up to 100% volume plus a full-screen 16-24 Hz strobe |

## Workflow

1. State the exact action needed and the consequence of waiting.
2. Confirm the user authorized persistent reminders. Treat permission for notifications, sound, volume changes, device switching, and visual pulses as separate permissions.
3. Run a read-only preflight before the first sound alert:

   ```bash
   python3 scripts/alert_user.py preflight
   ```

4. Read [references/escalation.md](references/escalation.md) and select the lowest sufficient level.
5. Preview every level 3-5 invocation with `--dry-run` before running it.
6. Send one alert, report the channel used, and wait for the configured interval. Escalate by at most one level after an unanswered interval.
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

The synthesized alarm reads JSON scores. Levels 1-2 select the bundled song score (`song-music.json`, user-supplied, license `NOASSERTION`); levels 3-5 select bundled original fire-truck siren scores (yelp, wail, hi-lo) rendered with a harsh harmonic-rich waveform at near full scale. Pass a user-owned/licensed score with `--score PATH`. Do not fetch or reconstruct copyrighted melodies. Musical notation is still protected expression; a score is not a copyright workaround.

```bash
python3 scripts/synth_alarm.py --score assets/scores/fire-truck-wail.json --output /tmp/alert-user.wav
```

## Failure Handling

- If native notifications fail, report the failure and stay in chat; do not silently jump to a louder level.
- If no physical audio output is detected, do not use a virtual device automatically. Ask the user to choose an output.
- If sound playback fails, retain notification/dialog channels and report the exact missing helper.
- If the graphical session or Tk is unavailable, skip the visual pulse and continue with the already authorized channels.
