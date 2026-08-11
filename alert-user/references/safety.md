# Safety Boundaries

This fork is configured in **maximum-intensity mode** for a single specific user who attested that they:

- have healthy hearing and no tinnitus risk from loud computer audio,
- have no photosensitive epilepsy or related conditions,
- work in an environment where only genuinely loud alerts reliably reach them.

The caps below are still hard properties of the scripts. Do not remove or raise them further, and do not use the loud or strobing modes around bystanders, children, pets, or anyone who has not made the same attestation.

## Hearing

- Generated waveform stays at or below 0.95 full-scale amplitude, harsh harmonic-rich synthesis.
- Temporary system volume may go up to 100 percent when explicitly authorized, and must be restored after each alert, including interrupted runs.
- Never automatically select headphones, hearing aids, Bluetooth devices, virtual meeting devices, or remote outputs.
- Do not use sound when the user might be driving, recording, presenting, sleeping, or sharing a space.

## Display

- Visual strobes require explicit opt-in and an interactive desktop session.
- Cap transitions at 24 Hz and total duration at 60 seconds.
- Provide an immediate Escape/click exit and descriptive static text.
- Do not use unbounded loops or patterns intended to bypass accessibility settings.
- **Photosensitive epilepsy: forbidden, full stop.** The 8-24 Hz range sits squarely inside the photosensitive-seizure risk band. Only the attesting user should ever see this mode; warn anyone else away from the screen first, and never enable `--allow-visual-pulse` on a shared or public display.

## Automation

- Prefer one thread heartbeat over background daemons or cron jobs.
- Do not run hidden infinite processes.
- Stop and disable reminders as soon as the user responds.
- Preserve Focus/Do Not Disturb and operating-system notification controls.

## Copyright

Audio files and musical notation can both be copyrighted. Ship only original or licensed scores. Accept custom note-score files only when the user has the right to use them.
