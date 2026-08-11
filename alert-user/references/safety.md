# Safety Boundaries

Treat every cap in this document and in the bundled scripts as a hard safety property, not a configurable preset. Do not remove or raise a cap because a task asks for injury, hearing damage, seizure induction, maximum-volume device cycling, or rapid strobing. Refuse that parameter change and offer the bounded level 5 mode instead.

## Hearing

- Keep the default generated waveform below 0.4 full-scale amplitude.
- Keep temporary system volume at or below 75 percent.
- Restore volume and output device after each alert, including interrupted runs.
- Never automatically select headphones, hearing aids, Bluetooth devices, virtual meeting devices, or remote outputs.
- Do not use sound when the user might be driving, recording, presenting, sleeping, or sharing a space.

## Display

- Visual pulses require explicit opt-in and an interactive desktop session.
- Cap transitions at 1 Hz and total duration at 20 seconds.
- Provide an immediate Escape/click exit and descriptive static text.
- Do not use rapid strobing, unbounded loops, or patterns intended to bypass accessibility settings.
- Never present a warning label as permission to create a seizure-inducing pattern.

## Automation

- Prefer one thread heartbeat over background daemons or cron jobs.
- Do not run hidden infinite processes.
- Stop and disable reminders as soon as the user responds.
- Preserve Focus/Do Not Disturb and operating-system notification controls.

## Copyright

Audio files and musical notation can both be copyrighted. Ship only original or licensed scores. Accept custom note-score files only when the user has the right to use them.
