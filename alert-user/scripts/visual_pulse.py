#!/usr/bin/env python3
"""Show a bounded, opt-in, aggressive full-screen visual attention strobe."""

from __future__ import annotations

import argparse
import json
import sys

MAX_RATE_HZ = 24.0
MAX_DURATION_SECONDS = 60.0


def validated_timing(rate_hz: float, duration: float) -> tuple[float, float]:
    if not 0.2 <= rate_hz <= MAX_RATE_HZ:
        raise ValueError(f"rate must be between 0.2 and {MAX_RATE_HZ} Hz")
    if not 1.0 <= duration <= MAX_DURATION_SECONDS:
        raise ValueError(f"duration must be between 1 and {MAX_DURATION_SECONDS} seconds")
    return rate_hz, duration


def show(message: str, rate_hz: float, duration: float) -> None:
    import tkinter as tk

    rate_hz, duration = validated_timing(rate_hz, duration)
    root = tk.Tk()
    root.title("Alert User")
    root.attributes("-fullscreen", True)
    root.attributes("-topmost", True)
    root.configure(cursor="hand2")
    colors = [
        ("#ff0000", "#ffffff"),
        ("#000000", "#ffff00"),
        ("#ffffff", "#ff0000"),
        ("#ffff00", "#000000"),
        ("#b00020", "#ffffff"),
        ("#000000", "#ffffff"),
    ]
    label = tk.Label(root, text=message, font=("Helvetica", 64, "bold"), padx=48, pady=48, wraplength=1100)
    label.pack(expand=True, fill="both")
    root.bind("<Escape>", lambda _event: root.destroy())
    root.bind("<Button-1>", lambda _event: root.destroy())

    interval_ms = int(1000 / rate_hz)
    state = {"index": 0}

    def pulse() -> None:
        background, foreground = colors[state["index"] % len(colors)]
        root.configure(bg=background)
        label.configure(bg=background, fg=foreground)
        state["index"] += 1
        root.after(interval_ms, pulse)

    pulse()
    root.after(int(duration * 1000), root.destroy)
    root.mainloop()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--message", default="Codex needs your attention")
    parser.add_argument("--rate", type=float, default=16.0)
    parser.add_argument("--duration", type=float, default=30.0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    rate, duration = validated_timing(args.rate, args.duration)
    if args.dry_run:
        print(
            json.dumps(
                {"message": args.message, "rate_hz": rate, "duration_seconds": duration},
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0
    show(args.message, rate, duration)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (RuntimeError, ValueError) as error:
        print(f"alert-user: {error}", file=sys.stderr)
        raise SystemExit(2)
