# Alert User

Codex has reached the ancient and terrifying state known as: **waiting for you to click one button**.

`alert-user` is a Codex skill for progressively getting a user's attention when an authorized persistent task is blocked on a confirmation, approval, login, browser interaction, hardware action, or other manual step.

It starts polite. It can become difficult to ignore. It still refuses to turn your desk into a hearing test or a seizure hazard.

## The escalation ladder

| Level | What happens |
| --- | --- |
| 1 | Native notification |
| 2 | Notification and bring Codex forward |
| 3 | Add an original synthesized chime |
| 4 | Add a bounded confirmation dialog and repeated alarm phrase |
| 5 | Add a full-screen, high-contrast **slow** pulse and urgent synthesized alarm |

Each channel has its own permission boundary. Sound, temporary volume changes, device switching, and visual pulses are never inferred from a generic "remind me" request.

## Try it without surprising yourself

```bash
python3 alert-user/scripts/alert_user.py preflight --json
python3 alert-user/scripts/alert_user.py alert --level 5 \
  --allow-sound --allow-dialog --allow-visual-pulse --dry-run
```

A real, quiet notification:

```bash
python3 alert-user/scripts/alert_user.py alert --level 1 \
  --title "Codex is waiting" \
  --message "Please return and confirm the result."
```

The scripts use only the Python standard library plus operating-system helpers such as `osascript`, `afplay`, `notify-send`, `paplay`, or `aplay` when available.

## Install as a Codex skill

Clone the repository, then link or copy the `alert-user` directory into your Codex skills directory:

```bash
git clone https://github.com/HMyaoyuan/codex-alert-user.git
mkdir -p "${CODEX_HOME:-$HOME/.codex}/skills"
ln -s "$PWD/codex-alert-user/alert-user" "${CODEX_HOME:-$HOME/.codex}/skills/alert-user"
```

Restart Codex or begin a new task so the skill metadata is discovered.

## About the alarm "score"

The repository ships note data, not an MP3. The three bundled jingles are original CC0 scores rendered into WAV data at runtime. You can supply another JSON score that you own or are licensed to use.

Musical notation is still copyrighted expression, so this repository does not smuggle a copyrighted song in through the sheet-music door. The door has been checked. It is not a loophole.

## Safety is part of the feature

- Generated audio is amplitude-limited.
- Temporary volume increases are capped at 75% and restored.
- Output devices are never rotated automatically.
- Visual pulses are opt-in, capped at 1 Hz, bounded to 20 seconds, and dismissible with Escape or a click.
- Recurring reminders belong in one stoppable Codex heartbeat, not a hidden infinite daemon.
- Any response from the user pauses escalation; confirmation stops it.

The most dramatic level should feel urgent, not hostile.

## Development

```bash
python3 -m unittest discover -s tests -v
python3 ~/.codex/skills/.system/skill-creator/scripts/quick_validate.py alert-user
du -sh .
```

MIT licensed. The original bundled scores are additionally marked CC0-1.0.
