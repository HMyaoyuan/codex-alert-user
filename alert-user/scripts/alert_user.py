#!/usr/bin/env python3
"""Inspect attention channels and send one bounded, progressively stronger alert."""

from __future__ import annotations

import argparse
import json
import os
import platform
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from synth_alarm import load_score, play_wav, render_wav, score_duration, score_path_for_level
from visual_pulse import validated_timing

MAX_VOLUME = 75
SCRIPT_DIR = Path(__file__).resolve().parent


def run(command: list[str], *, check: bool = False, timeout: float = 15) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, capture_output=True, text=True, check=check, timeout=timeout)


def macos_volume() -> dict:
    result = run(["osascript", "-e", "get volume settings"])
    match = re.search(r"output volume:(\d+).*output muted:(true|false)", result.stdout)
    if not match:
        return {"volume": None, "muted": None}
    return {"volume": int(match.group(1)), "muted": match.group(2) == "true"}


def macos_devices() -> list[dict]:
    result = run(["system_profiler", "SPAudioDataType", "-json"], timeout=30)
    if result.returncode != 0:
        return []
    payload = json.loads(result.stdout)
    groups = payload.get("SPAudioDataType", [])
    devices: list[dict] = []
    for group in groups:
        for item in group.get("_items", []):
            if not item.get("coreaudio_device_output"):
                continue
            transport = str(item.get("coreaudio_device_transport", "unknown"))
            name = str(item.get("_name", "Unknown output"))
            devices.append(
                {
                    "name": name,
                    "default": item.get("coreaudio_default_audio_output_device") == "spaudio_yes",
                    "transport": transport,
                    "virtual": "virtual" in transport or "virtual" in name.lower(),
                }
            )
    return devices


def linux_devices() -> list[dict]:
    if not shutil.which("pactl"):
        return []
    default = run(["pactl", "get-default-sink"]).stdout.strip()
    result = run(["pactl", "list", "short", "sinks"])
    devices = []
    for line in result.stdout.splitlines():
        fields = line.split("\t")
        if len(fields) >= 2:
            name = fields[1]
            devices.append(
                {
                    "name": name,
                    "default": name == default,
                    "transport": "pulse",
                    "virtual": "virtual" in name.lower(),
                }
            )
    return devices


def windows_devices() -> list[dict]:
    if not shutil.which("powershell"):
        return []
    command = "Get-CimInstance Win32_SoundDevice | Select-Object -ExpandProperty Name"
    result = run(["powershell", "-NoProfile", "-Command", command])
    return [
        {
            "name": line.strip(),
            "default": False,
            "transport": "windows",
            "virtual": "virtual" in line.lower(),
        }
        for line in result.stdout.splitlines()
        if line.strip()
    ]


def preflight() -> dict:
    system = platform.system()
    devices: list[dict]
    audio: dict = {"volume": None, "muted": None}
    if system == "Darwin":
        devices = macos_devices()
        audio.update(macos_volume())
    elif system == "Linux":
        devices = linux_devices()
    elif system == "Windows":
        devices = windows_devices()
    else:
        devices = []
    physical = [device for device in devices if not device["virtual"]]
    default = next((device for device in devices if device["default"]), None)
    recommended = default if default and not default["virtual"] else (physical[0] if physical else None)
    return {
        "platform": system,
        "notification": bool(shutil.which("osascript") or shutil.which("notify-send") or shutil.which("powershell")),
        "dialog": bool(
            shutil.which("osascript")
            or shutil.which("zenity")
            or shutil.which("kdialog")
            or shutil.which("powershell")
        ),
        "wav_player": bool(
            shutil.which("afplay") or shutil.which("paplay") or shutil.which("aplay") or system == "Windows"
        ),
        "device_switch_helper": shutil.which("SwitchAudioSource"),
        "audio": audio,
        "outputs": devices,
        "recommended_output": recommended,
    }


def notify(title: str, message: str) -> bool:
    system = platform.system()
    if system == "Darwin":
        script = (
            'on run argv\ndisplay notification (item 2 of argv) with title (item 1 of argv) sound name "Glass"\nend run'
        )
        return run(["osascript", "-e", script, title, message]).returncode == 0
    if system == "Linux" and shutil.which("notify-send"):
        return run(["notify-send", title, message]).returncode == 0
    if system == "Windows" and shutil.which("powershell"):
        command = f"[console]::beep(900,120); Write-Output {json.dumps(title + ': ' + message)}"
        return run(["powershell", "-NoProfile", "-Command", command]).returncode == 0
    return False


def activate_app(app: str) -> bool:
    if platform.system() != "Darwin" or not shutil.which("osascript"):
        return False
    script = "on run argv\ntell application (item 1 of argv) to activate\nend run"
    return run(["osascript", "-e", script, app]).returncode == 0


def dialog(title: str, message: str, timeout: int) -> bool:
    system = platform.system()
    if system == "Darwin":
        script = (
            "on run argv\n"
            "display alert (item 1 of argv) message (item 2 of argv) as critical "
            f'buttons {{"OK"}} default button "OK" giving up after {timeout}\n'
            "end run"
        )
        return run(["osascript", "-e", script, title, message], timeout=timeout + 5).returncode == 0
    if system == "Linux" and shutil.which("zenity"):
        command = ["zenity", "--warning", f"--title={title}", f"--text={message}", f"--timeout={timeout}"]
        return run(command, timeout=timeout + 5).returncode == 0
    return False


def set_macos_volume(value: int) -> None:
    run(["osascript", "-e", f"set volume output volume {value}"], check=True)


def current_macos_device() -> str | None:
    if not shutil.which("SwitchAudioSource"):
        return None
    result = run(["SwitchAudioSource", "-c"])
    return result.stdout.strip() or None


def switch_macos_device(name: str) -> None:
    run(["SwitchAudioSource", "-s", name], check=True)


def plan_for_level(level: int, allow_sound: bool, allow_dialog: bool, allow_visual: bool) -> list[str]:
    actions = ["notification"]
    if level >= 2:
        actions.append("activate-app")
    if level >= 3:
        actions.append("synthesized-sound" if allow_sound else "sound-skipped-no-permission")
    if level >= 4:
        actions.append("dialog" if allow_dialog else "dialog-skipped-no-permission")
    if level >= 5:
        actions.append("visual-pulse" if allow_visual else "visual-skipped-no-permission")
    return actions


def alert(args: argparse.Namespace) -> dict:
    report = preflight()
    actions = plan_for_level(args.level, args.allow_sound, args.allow_dialog, args.allow_visual_pulse)
    result = {"level": args.level, "actions": actions, "preflight": report, "dry_run": args.dry_run}
    score = None
    score_path = args.score or score_path_for_level(args.level)
    repeat = 1 if args.level == 3 else (2 if args.level == 4 else 3)
    if args.level >= 3 and args.allow_sound:
        score = load_score(score_path)
        result["score"] = score.get("name", score_path.name)
        result["sound_duration_seconds"] = round(score_duration(score, repeat), 2)
    if args.level >= 5 and args.allow_visual_pulse:
        validated_timing(args.pulse_rate, args.pulse_duration)
    if args.dry_run:
        return result

    original_volume: int | None = None
    original_device: str | None = None
    wav_path: Path | None = None
    visual_process: subprocess.Popen[str] | None = None
    try:
        if args.device:
            if not args.allow_device_switch:
                raise ValueError("--device requires --allow-device-switch")
            if platform.system() != "Darwin" or not shutil.which("SwitchAudioSource"):
                raise RuntimeError("device switching requires SwitchAudioSource on macOS")
            names = {item["name"] for item in report["outputs"]}
            if args.device not in names:
                raise ValueError(f"output device not found: {args.device}")
            original_device = current_macos_device()
            switch_macos_device(args.device)

        if args.allow_volume_change:
            if platform.system() != "Darwin":
                raise RuntimeError("automatic volume changes are supported only on macOS")
            original_volume = report["audio"].get("volume")
            if original_volume is None:
                raise RuntimeError("could not read the current output volume")
            target = min(args.target_volume, MAX_VOLUME)
            if target > original_volume:
                set_macos_volume(target)

        result["notification_sent"] = notify(args.title, args.message)
        if args.level >= 2:
            result["app_activated"] = activate_app(args.activate_app)
        if args.level >= 5 and args.allow_visual_pulse:
            command = [
                sys.executable,
                str(SCRIPT_DIR / "visual_pulse.py"),
                "--message",
                args.message,
                "--rate",
                str(args.pulse_rate),
                "--duration",
                str(args.pulse_duration),
            ]
            visual_process = subprocess.Popen(command, text=True)
        if args.level >= 3 and args.allow_sound:
            wav_path = Path(tempfile.gettempdir()) / f"alert-user-{os.getpid()}.wav"
            assert score is not None
            render_wav(score, wav_path, repeat=repeat)
            play_wav(wav_path)
            result["sound_played"] = True
        if args.level >= 4 and args.allow_dialog:
            result["dialog_shown"] = dialog(args.title, args.message, args.dialog_timeout)
        if visual_process:
            result["visual_exit_code"] = visual_process.wait(timeout=args.pulse_duration + 5)
        return result
    finally:
        if visual_process and visual_process.poll() is None:
            visual_process.terminate()
            try:
                visual_process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                visual_process.kill()
        if wav_path:
            wav_path.unlink(missing_ok=True)
        if original_device:
            switch_macos_device(original_device)
        if original_volume is not None:
            set_macos_volume(original_volume)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    inspect_parser = subparsers.add_parser("preflight")
    inspect_parser.add_argument("--json", action="store_true")

    alert_parser = subparsers.add_parser("alert")
    alert_parser.add_argument("--level", type=int, choices=range(1, 6), default=1)
    alert_parser.add_argument("--title", default="Codex needs your attention")
    alert_parser.add_argument("--message", default="Please return and complete the requested action.")
    alert_parser.add_argument("--activate-app", default="Codex")
    alert_parser.add_argument("--allow-sound", action="store_true")
    alert_parser.add_argument("--allow-dialog", action="store_true")
    alert_parser.add_argument("--allow-visual-pulse", action="store_true")
    alert_parser.add_argument("--allow-volume-change", action="store_true")
    alert_parser.add_argument("--target-volume", type=int, choices=range(1, MAX_VOLUME + 1), default=60)
    alert_parser.add_argument("--allow-device-switch", action="store_true")
    alert_parser.add_argument("--device")
    alert_parser.add_argument("--score", type=Path)
    alert_parser.add_argument("--dialog-timeout", type=int, choices=range(5, 31), default=15)
    alert_parser.add_argument("--pulse-rate", type=float, default=0.8)
    alert_parser.add_argument("--pulse-duration", type=float, default=12.0)
    alert_parser.add_argument("--dry-run", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "preflight":
        report = preflight()
        if args.json:
            print(json.dumps(report, ensure_ascii=False, indent=2))
        else:
            print(f"Platform: {report['platform']}")
            print(f"Volume: {report['audio'].get('volume')}  Muted: {report['audio'].get('muted')}")
            for output in report["outputs"]:
                markers = ["default"] if output["default"] else []
                if output["virtual"]:
                    markers.append("virtual")
                suffix = f" ({', '.join(markers)})" if markers else ""
                print(f"- {output['name']}{suffix}")
        return 0
    print(json.dumps(alert(args), ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, RuntimeError, ValueError, json.JSONDecodeError, subprocess.SubprocessError) as error:
        print(f"alert-user: {error}", file=sys.stderr)
        raise SystemExit(2)
