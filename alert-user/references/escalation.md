# Escalation Ladder

Alert only while a user-authorized task is blocked on a manual step only the user can complete. Check that the blocker still exists before every single alert. While a stage goes unanswered, repeat its alert at the stage's rhythm, then escalate exactly one stage. Thirty minutes without a response means TOTAL APOCALYPSE.

| Level | Name | Channels | Repeat every | Escalate after | Total elapsed |
| --- | --- | --- | --- | --- | --- |
| 1 | The Serenade | Chat plus native notification, plus the bundled audio clip once when sound is allowed | 3 minutes | 6 minutes (2 unanswered) | 6 min |
| 2 | The Infinite Loop | Level 1 plus bring the task app forward; the second audio clip loops back-to-back | 4 minutes | 8 minutes (2 unanswered) | 14 min |
| 3 | Fire Truck Incoming | Level 2 plus a fire-truck yelp siren burst | 4 minutes | 8 minutes (2 unanswered) | 22 min |
| 4 | Citywide Meltdown | Level 3 plus a bounded dialog and a repeated fire-truck wail | 4 minutes | 8 minutes (2 unanswered) | 30 min |
| 5 | TOTAL APOCALYPSE | Level 4 plus a full-screen 16-24 Hz high-contrast strobe for up to 60 seconds and the hi-lo siren at full volume | 5 minutes, at most 3 bursts | Then back off to one reminder every 15 minutes | — |

## Selection Rules

1. Start at level 1 unless the user explicitly requested a starting level.
2. Use preflight data before level 3. Prefer the current default physical output.
3. Never infer that "keep reminding me" permits volume changes, device switching, or a visual pulse.
4. Escalate by at most one level per unanswered interval. Never skip a level.
5. Keep the requested manual action in every alert. Avoid generic noise with no actionable text.
6. Stop immediately when the user responds, even if the response is not the expected confirmation.
7. If the response is ambiguous, pause escalation and ask one concise question in chat.

## Recurring Heartbeat Prompt

Use a prompt with these invariants:

- Check the current task for confirmation before alerting.
- If confirmed, disable this heartbeat and emit no alert.
- If not confirmed, send exactly one reminder at the current level, but only once the stage's interval has elapsed.
- Escalate exactly one level after the stage's unanswered budget is spent (see the table).
- Record the level and next allowed time in the task message.
- Never create another heartbeat for the same blocker.
