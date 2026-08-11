# Escalation Ladder

Use the lowest level that can reasonably reach the user. Escalate only after the prior interval passes without a response.

| Level | Channels | Earliest escalation | Permission |
| --- | --- | --- | --- |
| 1 | Chat plus native notification | Immediate | Persistent-reminder permission |
| 2 | Level 1 plus bring the task app forward | 5 minutes | Persistent-reminder permission |
| 3 | Level 2 plus a fire-truck yelp siren burst | 10 minutes | Explicit sound permission |
| 4 | Level 3 plus a bounded dialog and a repeated fire-truck wail | 15 minutes | Explicit sound and dialog permission |
| 5 | Level 4 plus a full-screen 8-12 Hz high-contrast strobe for up to 60 seconds and the hi-lo siren at full volume | 20 minutes | Explicit sound and visual-pulse permission |

## Selection Rules

1. Start at level 1 unless the user explicitly requested a starting level.
2. Use preflight data before level 3. Prefer the current default physical output.
3. Never infer that "keep reminding me" permits volume changes, device switching, or a visual pulse.
4. At level 5, run at most three bursts five minutes apart, then back off to one reminder every 15 minutes.
5. Keep the requested manual action in every alert. Avoid generic noise with no actionable text.
6. Stop immediately when the user responds, even if the response is not the expected confirmation.
7. If the response is ambiguous, pause escalation and ask one concise question in chat.

## Recurring Heartbeat Prompt

Use a prompt with these invariants:

- Check the current task for confirmation before alerting.
- If confirmed, disable this heartbeat and emit no alert.
- If not confirmed, send exactly one reminder at the current level.
- Record the level and next allowed time in the task message.
- Never create another heartbeat for the same blocker.
