from __future__ import annotations

import contextlib
import io
import json
import struct
import sys
import tempfile
import unittest
import wave
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "alert-user" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import alert_user
import synth_alarm
import visual_pulse


def read_peak_amplitude(path: Path) -> float:
    with wave.open(str(path), "rb") as wav_file:
        frames = wav_file.readframes(wav_file.getnframes())
    samples = struct.unpack(f"<{len(frames) // 2}h", frames)
    return max(abs(sample) for sample in samples) / 32_767


class ScoreTests(unittest.TestCase):
    def test_bundled_score_renders_bounded_wav(self) -> None:
        score = synth_alarm.load_score(synth_alarm.default_score_path())
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "alarm.wav"
            duration = synth_alarm.render_wav(score, output, repeat=3)
            self.assertLessEqual(duration, synth_alarm.MAX_TOTAL_SECONDS)
            with wave.open(str(output), "rb") as wav_file:
                self.assertEqual(wav_file.getnchannels(), 1)
                self.assertEqual(wav_file.getframerate(), synth_alarm.SAMPLE_RATE)
                self.assertGreater(wav_file.getnframes(), 0)
            self.assertLessEqual(read_peak_amplitude(output), synth_alarm.MAX_MASTER_GAIN)

    def test_siren_scores_render_loud_and_near_full_scale(self) -> None:
        for level in (3, 4, 5):
            score = synth_alarm.load_score(synth_alarm.score_path_for_level(level))
            self.assertIn("siren", score)
            with tempfile.TemporaryDirectory() as temp_dir:
                output = Path(temp_dir) / f"siren-{level}.wav"
                synth_alarm.render_wav(score, output, repeat=1)
                # Fire-truck sirens should be loud, not a polite chime.
                self.assertGreaterEqual(read_peak_amplitude(output), 0.7)

    def test_rejects_unsafe_frequency(self) -> None:
        payload = {"notes": [{"frequency": 12_000, "duration": 0.2}]}
        with tempfile.TemporaryDirectory() as temp_dir:
            score_path = Path(temp_dir) / "bad.json"
            score_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                synth_alarm.load_score(score_path)

    def test_rejects_siren_outside_bounds(self) -> None:
        payload = {
            "siren": {
                "type": "yelp",
                "low_hz": 600,
                "high_hz": 9000,
                "cycle_seconds": 0.5,
                "cycles": 10,
            }
        }
        with tempfile.TemporaryDirectory() as temp_dir:
            score_path = Path(temp_dir) / "bad-siren.json"
            score_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                synth_alarm.load_score(score_path)

    def test_escalation_levels_use_distinct_original_scores(self) -> None:
        paths = {synth_alarm.score_path_for_level(level) for level in (3, 4, 5)}
        self.assertEqual(len(paths), 3)
        for path in paths:
            self.assertTrue(path.exists())


class EscalationTests(unittest.TestCase):
    def test_intensity_caps_match_maximum_mode(self) -> None:
        self.assertLessEqual(alert_user.MAX_VOLUME, 100)
        self.assertLessEqual(synth_alarm.MAX_MASTER_GAIN, 1.0)
        self.assertGreaterEqual(synth_alarm.MAX_MASTER_GAIN, 0.9)
        self.assertLessEqual(visual_pulse.MAX_RATE_HZ, 12.0)
        self.assertLessEqual(visual_pulse.MAX_DURATION_SECONDS, 60.0)

    def test_level_five_degrades_without_permissions(self) -> None:
        self.assertEqual(
            alert_user.plan_for_level(5, allow_sound=False, allow_dialog=False, allow_visual=False),
            [
                "notification",
                "activate-app",
                "sound-skipped-no-permission",
                "dialog-skipped-no-permission",
                "visual-skipped-no-permission",
            ],
        )

    def test_level_five_enables_only_explicit_channels(self) -> None:
        actions = alert_user.plan_for_level(5, allow_sound=True, allow_dialog=True, allow_visual=True)
        self.assertIn("synthesized-sound", actions)
        self.assertIn("dialog", actions)
        self.assertIn("visual-pulse", actions)

    def test_visual_caps_are_enforced(self) -> None:
        with self.assertRaises(ValueError):
            visual_pulse.validated_timing(15.0, 5)
        with self.assertRaises(ValueError):
            visual_pulse.validated_timing(8.0, 120)

    def test_visual_defaults_are_aggressive(self) -> None:
        rate, duration = visual_pulse.validated_timing(8.0, 30.0)
        self.assertEqual((rate, duration), (8.0, 30.0))

    def test_volume_parser_is_bounded_by_cli(self) -> None:
        parser = alert_user.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["alert", "--target-volume", "101"])


if __name__ == "__main__":
    unittest.main()
