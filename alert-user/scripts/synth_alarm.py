#!/usr/bin/env python3
"""Render and optionally play a loud synthesized alarm from a JSON score.

Two score kinds are supported:

- ``notes``: the original discrete note list.
- ``siren``: a fire-truck style continuous siren sweep (``wail``, ``yelp``,
  or ``hilo``) rendered with a harsh harmonic-rich waveform.
"""

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
MAX_TOTAL_SECONDS = 300.0
MAX_REPEAT = 8
MIN_FREQUENCY = 80.0
MAX_FREQUENCY = 4_000.0
MAX_NOTE_SECONDS = 2.0
MAX_MASTER_GAIN = 0.95
MAX_SIREN_CYCLE_SECONDS = 5.0
MIN_SIREN_CYCLE_SECONDS = 0.2
MAX_SIREN_CYCLES = 24
SIREN_TYPES = ("wail", "yelp", "hilo")


def default_score_path() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "scores" / "fire-truck-wail.json"


def score_path_for_level(level: int) -> Path:
    filename = {
        3: "fire-truck-yelp.json",
        4: "fire-truck-wail.json",
        5: "fire-truck-hilo.json",
    }.get(level, "fire-truck-yelp.json")
    return default_score_path().parent / filename


def audio_dir() -> Path:
    return Path(__file__).resolve().parent.parent / "assets" / "audio"


def audio_path_for_level(level: int) -> Path | None:
    filename = {1: "1.mp3", 2: "2.mp3"}.get(level)
    if filename is None:
        return None
    path = audio_dir() / filename
    return path if path.exists() else None


def audio_duration(path: Path) -> float:
    manifest_path = path.parent / "manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if path.name in manifest:
            return float(manifest[path.name])
    raise ValueError(f"no duration recorded for {path.name}; add it to manifest.json")


def audio_player_command(path: Path) -> list[str] | None:
    system = platform.system()
    if system == "Darwin" and shutil.which("afplay"):
        return ["afplay", str(path)]
    if system == "Linux":
        for player in ("mpg123", "ffplay", "paplay"):
            if shutil.which(player):
                return [player, str(path)]
    return None


def play_audio_file(path: Path) -> None:
    command = audio_player_command(path)
    if command is None:
        raise RuntimeError("no supported audio player found (expected afplay, mpg123, ffplay, or paplay)")
    subprocess.run(command, check=True)


def _validate_notes(data: dict) -> None:
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
        if not 0 <= gap <= 20.0:
            raise ValueError(f"note {index} gap is outside 0-20 seconds")
        if not 0 < gain <= 1.0:
            raise ValueError(f"note {index} gain is outside 0-1")


def _validate_siren(data: dict) -> None:
    siren = data.get("siren")
    if not isinstance(siren, dict):
        raise ValueError("siren score must contain a siren object")
    siren_type = str(siren.get("type", ""))
    if siren_type not in SIREN_TYPES:
        raise ValueError(f"siren type must be one of {SIREN_TYPES}")
    low = float(siren.get("low_hz", 0))
    high = float(siren.get("high_hz", 0))
    cycle = float(siren.get("cycle_seconds", 0))
    cycles = int(siren.get("cycles", 0))
    gain = float(siren.get("gain", 0.9))
    if not MIN_FREQUENCY <= low < high <= MAX_FREQUENCY:
        raise ValueError(f"siren sweep must stay inside {MIN_FREQUENCY}-{MAX_FREQUENCY} Hz with low < high")
    if not MIN_SIREN_CYCLE_SECONDS <= cycle <= MAX_SIREN_CYCLE_SECONDS:
        raise ValueError(
            f"siren cycle_seconds is outside {MIN_SIREN_CYCLE_SECONDS}-{MAX_SIREN_CYCLE_SECONDS} seconds"
        )
    if not 1 <= cycles <= MAX_SIREN_CYCLES:
        raise ValueError(f"siren cycles must be between 1 and {MAX_SIREN_CYCLES}")
    if not 0 < gain <= 1.0:
        raise ValueError("siren gain is outside 0-1")


def load_score(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "siren" in data:
        _validate_siren(data)
    else:
        _validate_notes(data)
    return data


def score_duration(score: dict, repeat: int) -> float:
    if "siren" in score:
        siren = score["siren"]
        one_pass = float(siren["cycle_seconds"]) * int(siren["cycles"])
    else:
        one_pass = sum(float(note["duration"]) + float(note.get("gap", 0)) for note in score["notes"])
    return one_pass * repeat


def _harsh_wave(phase: float) -> float:
    """Harmonic-rich buzz: sawtooth-flavored stack, normalized to unit peak."""
    value = (
        math.sin(phase)
        + 0.5 * math.sin(phase * 2)
        + 0.33 * math.sin(phase * 3)
        + 0.25 * math.sin(phase * 4)
    )
    return value / 2.08


def _render_siren(siren: dict) -> bytearray:
    siren_type = str(siren["type"])
    low = float(siren["low_hz"])
    high = float(siren["high_hz"])
    cycle = float(siren["cycle_seconds"])
    cycles = int(siren["cycles"])
    gain = float(siren.get("gain", 0.9))
    mid = (low + high) / 2.0
    span = (high - low) / 2.0

    total_samples = int(SAMPLE_RATE * cycle * cycles)
    fade_count = max(1, min(int(SAMPLE_RATE * 0.02), total_samples // 8))
    raw: list[float] = []
    phase = 0.0
    for sample_index in range(total_samples):
        t = sample_index / SAMPLE_RATE
        position = (t % cycle) / cycle
        if siren_type == "hilo":
            # European fire-truck two-tone: hard alternation between two pitches.
            frequency = high if position < 0.5 else low
        else:
            # wail: slow sweeping sine curve; yelp: same shape, fast cycle.
            frequency = mid + span * math.sin(2 * math.pi * position - math.pi / 2)
        phase += 2 * math.pi * frequency / SAMPLE_RATE
        raw.append(_harsh_wave(phase))

    # Normalize so the siren peaks exactly at its gain: maximum loudness, no clipping.
    peak = max(abs(value) for value in raw) or 1.0
    frames = bytearray()
    for sample_index, value in enumerate(raw):
        envelope = 1.0
        if sample_index < fade_count:
            envelope = sample_index / fade_count
        elif sample_index >= total_samples - fade_count:
            envelope = (total_samples - sample_index - 1) / fade_count
        pcm = int(32_767 * gain * envelope * value / peak)
        frames.extend(struct.pack("<h", max(-32_768, min(32_767, pcm))))
    return frames


def render_wav(score: dict, output: Path, repeat: int = 1, master_gain: float = 0.9) -> float:
    if not 1 <= repeat <= MAX_REPEAT:
        raise ValueError(f"repeat must be between 1 and {MAX_REPEAT}")
    if not 0 < master_gain <= MAX_MASTER_GAIN:
        raise ValueError(f"master gain must be between 0 and {MAX_MASTER_GAIN}")
    total = score_duration(score, repeat)
    if total > MAX_TOTAL_SECONDS:
        raise ValueError(f"rendered alert would exceed {MAX_TOTAL_SECONDS} seconds")

    frames = bytearray()
    if "siren" in score:
        for _ in range(repeat):
            frames.extend(_render_siren(score["siren"]))
    else:
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
    parser.add_argument("--gain", type=float, default=0.9)
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
