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
                frames = wav_file.readframes(wav_file.getnframes())
            samples = struct.unpack(f"<{len(frames) // 2}h", frames)
            self.assertLessEqual(max(abs(sample) for sample in samples) / 32_767, synth_alarm.MAX_MASTER_GAIN)

    def test_rejects_unsafe_frequency(self) -> None:
        payload = {"notes": [{"frequency": 12_000, "duration": 0.2}]}
        with tempfile.TemporaryDirectory() as temp_dir:
            score_path = Path(temp_dir) / "bad.json"
            score_path.write_text(json.dumps(payload), encoding="utf-8")
            with self.assertRaises(ValueError):
                synth_alarm.load_score(score_path)

    def test_escalation_levels_use_distinct_original_scores(self) -> None:
        paths = {synth_alarm.score_path_for_level(level) for level in (3, 4, 5)}
        self.assertEqual(len(paths), 3)
        for path in paths:
            self.assertTrue(path.exists())


class EscalationTests(unittest.TestCase):
    def test_hard_safety_caps_cannot_reach_injury_or_strobe_ranges(self) -> None:
        self.assertLessEqual(alert_user.MAX_VOLUME, 75)
        self.assertLessEqual(synth_alarm.MAX_MASTER_GAIN, 0.4)
        self.assertLessEqual(visual_pulse.MAX_RATE_HZ, 1.0)
        self.assertLessEqual(visual_pulse.MAX_DURATION_SECONDS, 20.0)

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
            visual_pulse.validated_timing(3.0, 5)
        with self.assertRaises(ValueError):
            visual_pulse.validated_timing(0.8, 60)

    def test_volume_parser_is_bounded_by_cli(self) -> None:
        parser = alert_user.build_parser()
        with contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit):
                parser.parse_args(["alert", "--target-volume", "100"])


if __name__ == "__main__":
    unittest.main()
