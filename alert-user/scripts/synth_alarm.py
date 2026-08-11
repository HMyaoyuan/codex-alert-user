#!/usr/bin/env python3
"""Render and optionally play a small synthesized alert from a JSON note score."""

from __future__ import annotations

import argparse
import json
import math
import os
import platform
import shutil
import struct
import subprocess
import sys
import tempfile
import wave
from pathlib import Path

SAMPLE_RATE = 44_100
MAX_TOTAL_SECONDS = 20.0
MAX_REPEAT = 5
MIN_FREQUENCY = 80.0
MAX_FREQUENCY = 2_200.0
MAX_NOTE_SECONDS = 1.2
MAX_MASTER_GAIN = 0.4


def default_score_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "scores" / "original-urgent.json"


def score_path_for_level(level: int) -> Path:
    filename = {3: "original-gentle.json", 4: "original-urgent.json", 5: "original-critical.json"}.get(
        level, "original-gentle.json"
    )
    return default_score_path().parent / filename


def load_score(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    notes = data.get("notes")
    if not isinstance(notes, list) or not notes:
        raise ValueError("score must contain a non-empty notes list")
    for index, note in enumerate(notes):
        if not isinstance(note, dict):
            raise ValueError(f"note {index} must be an object")
        frequency = float(note.get("frequency", 0))
        duration = float(note.get("duration", 0))
        gap = float(note.get("gap", 0))
        gain = float(note.get("gain", 0.7))
        if not MIN_FREQUENCY <= frequency <= MAX_FREQUENCY:
            raise ValueError(f"note {index} frequency is outside {MIN_FREQUENCY}-{MAX_FREQUENCY} Hz")
        if not 0.02 <= duration <= MAX_NOTE_SECONDS:
            raise ValueError(f"note {index} duration is outside 0.02-{MAX_NOTE_SECONDS} seconds")
        if not 0 <= gap <= 1.0:
            raise ValueError(f"note {index} gap is outside 0-1 seconds")
        if not 0 < gain <= 1.0:
            raise ValueError(f"note {index} gain is outside 0-1")
    return data


def score_duration(score: dict, repeat: int) -> float:
    one_pass = sum(float(note["duration"]) + float(note.get("gap", 0)) for note in score["notes"])
    return one_pass * repeat


def render_wav(score: dict, output: Path, repeat: int = 1, master_gain: float = 0.35) -> float:
    if not 1 <= repeat <= MAX_REPEAT:
        raise ValueError(f"repeat must be between 1 and {MAX_REPEAT}")
    if not 0 < master_gain <= MAX_MASTER_GAIN:
        raise ValueError(f"master gain must be between 0 and {MAX_MASTER_GAIN}")
    total = score_duration(score, repeat)
    if total > MAX_TOTAL_SECONDS:
        raise ValueError(f"rendered alert would exceed {MAX_TOTAL_SECONDS} seconds")

    frames = bytearray()
    for _ in range(repeat):
        for note in score["notes"]:
            frequency = float(note["frequency"])
            duration = float(note["duration"])
            gap = float(note.get("gap", 0))
            gain = float(note.get("gain", 0.7)) * master_gain
            sample_count = int(SAMPLE_RATE * duration)
            fade_count = max(1, min(int(SAMPLE_RATE * 0.012), sample_count // 4))
            for sample_index in range(sample_count):
                envelope = 1.0
                if sample_index < fade_count:
                    envelope = sample_index / fade_count
                elif sample_index >= sample_count - fade_count:
                    envelope = (sample_count - sample_index - 1) / fade_count
                phase = 2 * math.pi * frequency * sample_index / SAMPLE_RATE
                value = math.sin(phase) + 0.18 * math.sin(phase * 2)
                pcm = int(32_767 * gain * envelope * value / 1.18)
                frames.extend(struct.pack("<h", max(-32_768, min(32_767, pcm))))
            frames.extend(b"\x00\x00" * int(SAMPLE_RATE * gap))

    output.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(output), "wb") as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(SAMPLE_RATE)
        wav_file.writeframes(frames)
    return total


def player_command(path: Path) -> list[str] | None:
    system = platform.system()
    if system == "Darwin" and shutil.which("afplay"):
        return ["afplay", str(path)]
    if system == "Linux":
        for player in ("paplay", "aplay"):
            if shutil.which(player):
                return [player, str(path)]
    return None


def play_wav(path: Path) -> None:
    if platform.system() == "Windows":
        import winsound

        winsound.PlaySound(str(path), winsound.SND_FILENAME)
        return
    command = player_command(path)
    if command is None:
        raise RuntimeError("no supported WAV player found (expected afplay, paplay, or aplay)")
    subprocess.run(command, check=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--score", type=Path, default=default_score_path())
    parser.add_argument("--output", type=Path)
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--gain", type=float, default=0.35)
    parser.add_argument("--play", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    score = load_score(args.score)
    duration = score_duration(score, args.repeat)
    if duration > MAX_TOTAL_SECONDS:
        raise ValueError(f"rendered alert would exceed {MAX_TOTAL_SECONDS} seconds")
    summary = {
        "score": score.get("name", args.score.name),
        "duration_seconds": round(duration, 2),
        "repeat": args.repeat,
    }
    if args.dry_run:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    temporary = args.output is None
    output = args.output or Path(tempfile.gettempdir()) / f"alert-user-{os.getpid()}.wav"
    try:
        render_wav(score, output, args.repeat, args.gain)
        summary["output"] = str(output)
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        if args.play:
            play_wav(output)
    finally:
        if temporary:
            output.unlink(missing_ok=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError) as error:
        print(f"alert-user: {error}", file=sys.stderr)
        raise SystemExit(2)
