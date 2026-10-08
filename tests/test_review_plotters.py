# SPDX-License-Identifier: MIT
"""Synthetic inputs only; no production media or external requests."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

TOOLS = Path(__file__).resolve().parents[1] / 'tools'
sys.path.insert(0, str(TOOLS))
import _audio_review as review
import plot_audio_review_windows as rms_plot
import plot_mirrored_audio_review as signed_plot

HAS_PLOT_DEPS = all(importlib.util.find_spec(name) for name in ('numpy', 'PIL'))
if HAS_PLOT_DEPS:
    import numpy as np
    from PIL import Image, ImageDraw


def window(start=0, end=.1, **extra):
    return {'role': 'Synthetic source', 'start': start, 'end': end, **extra}


class InputTests(unittest.TestCase):
    def test_rejects_malformed_and_nonfinite_ranges(self):
        invalid = [None, {}, [], [None], [window(role='')], [window(start=True)],
                   [window(start=-1)], [window(start=.1, end=.1)],
                   [window(start=.2, end=.1)], [window(end=float('inf'))],
                   [window(end=float('nan'))], [window(end=10 ** 1000)]]
        for rows in invalid:
            with self.subTest(rows=repr(rows)[:100]), self.assertRaises(ValueError):
                review.validate_ranges(rows)
        with self.assertRaisesRegex(ValueError, 'duration'):
            review.validate_ranges([window(end=1.1)], 1)

    def test_accepts_bom_and_preserves_window_data(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'ranges.json'
            rows = [window(markers=[{'seconds': .05, 'label': 'Acoustic observation'}])]
            path.write_text(json.dumps(rows), encoding='utf-8-sig')
            self.assertEqual(review.load_ranges(path), rows)

    def test_output_cannot_replace_input_or_hardlink(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, ranges, alias = root / 'source.wav', root / 'ranges.json', root / 'alias.png'
            source.write_bytes(b'synthetic'); ranges.write_text('[]')
            for output in (source, ranges):
                with self.assertRaisesRegex(ValueError, 'replace'):
                    review.validate_paths(source, ranges, output)
            os.link(source, alias)
            with self.assertRaisesRegex(ValueError, 'replace'):
                review.validate_paths(source, ranges, alias)

    def test_marker_policy_and_invalid_candidates(self):
        for markers in ('wrong', [None], [{'seconds': float('nan'), 'label': 'Observation'}],
                        [{'seconds': .05, 'label': ''}],
                        [{'seconds': .05, 'label': 'Observation', 'label_y': 250}]):
            with self.subTest(markers=markers), self.assertRaises(ValueError):
                signed_plot.validate_markers([window(markers=markers)])
        with self.assertRaisesRegex(ValueError, 'candidate_lines'):
            signed_plot.validate_markers([window(candidate_lines=[.05])])
        for candidates in ('wrong', [float('nan')], [-.1], [.2]):
            with self.subTest(candidates=candidates), self.assertRaises(ValueError):
                rms_plot.validate_candidates([window(candidate_lines=candidates)])

    def test_cli_help_needs_no_media_or_dependencies(self):
        for tool in ('plot_audio_review_windows.py', 'plot_mirrored_audio_review.py'):
            result = subprocess.run([sys.executable, '-B', str(TOOLS / tool), '--help'],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn('--ranges', result.stdout)

    def test_invalid_cli_input_preserves_existing_output(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            source, ranges, output = root / 'source.wav', root / 'ranges.json', root / 'review.png'
            source.write_bytes(b'not decoded because ranges are invalid')
            ranges.write_text(json.dumps([window(end=float('nan'))]))
            for tool in ('plot_audio_review_windows.py', 'plot_mirrored_audio_review.py'):
                output.write_bytes(b'keep this image')
                result = subprocess.run([sys.executable, '-B', '-O', str(TOOLS / tool),
                                         '--input', str(source), '--ranges', str(ranges),
                                         '--output', str(output)], capture_output=True, text=True)
                self.assertEqual(result.returncode, 1)
                self.assertIn('finite', result.stderr)
                self.assertNotIn('Traceback', result.stderr)
                self.assertEqual(output.read_bytes(), b'keep this image')


@unittest.skipUnless(HAS_PLOT_DEPS, 'Install numpy and Pillow to run synthetic rendering checks')
class RenderTests(unittest.TestCase):
    def test_rms_image_has_expected_rows_and_candidate_marker(self):
        samples = np.full(3200, .1, dtype=np.float32)
        image = rms_plot.render(samples, [window(candidate_lines=[.05]), window(.1, .2)],
                                np, Image, ImageDraw)
        self.assertEqual(image.size, (1800, 480))
        self.assertEqual(image.getpixel((915, 100)), (255, 0, 0))
        self.assertTrue(any(image.getpixel((x, 83)) == (23, 110, 181) for x in range(100, 800)))

    def test_rms_rejects_insufficient_bins_and_invalid_samples(self):
        for samples, rows in [(np.zeros(79), [window(end=79/16000)]),
                              (np.zeros(160), [window(start=.009, end=.0091)]),
                              (np.full(160, float('nan')), [window(end=.01)])]:
            with self.subTest(length=len(samples)), self.assertRaises(ValueError):
                rms_plot.render(samples, rows, np, Image, ImageDraw)

    def test_signed_plot_preserves_both_polarities(self):
        samples = np.tile(np.array([-.5, .5], dtype=np.float32), 2400)
        image = signed_plot.render(samples, [window()], np, Image, ImageDraw)
        self.assertEqual(image.size, (1900, 250))
        self.assertEqual(image.getpixel((500, 40)), (165, 220, 177))
        self.assertEqual(image.getpixel((500, 195)), (165, 220, 177))

    def test_one_sample_at_end_and_narrow_window_do_not_read_past_stop(self):
        image = signed_plot.render(np.array([.5], dtype=np.float32), [window(end=1/48000)],
                                   np, Image, ImageDraw)
        self.assertEqual(image.size, (1900, 250))
        guarded = np.array([.5, 1000], dtype=np.float32)
        image = signed_plot.render(guarded, [window(end=1/48000)], np, Image, ImageDraw)
        self.assertEqual(image.getpixel((1000, 33)), (165, 220, 177))
        self.assertEqual(image.getpixel((1000, 118)), (143, 160, 153))

    def test_silence_markers_and_out_of_source_rejection(self):
        samples = np.zeros(4800, dtype=np.float32)
        row = window(markers=[{'seconds': .05, 'label': 'Acoustic observation'},
                              {'seconds': 1, 'label': 'Outside this window'}])
        image = signed_plot.render(samples, [row], np, Image, ImageDraw)
        self.assertEqual(image.getpixel((965, 100)), (86, 217, 255))
        for invalid in [window(end=.101), window(end=.000001)]:
            with self.assertRaises(ValueError):
                signed_plot.render(samples, [invalid], np, Image, ImageDraw)

    def test_decoder_errors_and_nonfinite_output_are_clear(self):
        ffmpeg = Mock(); ffmpeg.get_ffmpeg_exe.return_value = 'fixture-ffmpeg'
        for raw in (b'', b'bad', np.array([float('nan')], dtype='<f4').tobytes()):
            with patch.object(review.subprocess, 'run', return_value=Mock(stdout=raw)):
                with self.assertRaises(ValueError):
                    review.decode_audio('synthetic.wav', 16000, np, ffmpeg)
        with patch.object(review.subprocess, 'run', side_effect=subprocess.CalledProcessError(1, ['fixture'])):
            with self.assertRaisesRegex(ValueError, 'FFmpeg'):
                review.decode_audio('synthetic.wav', 16000, np, ffmpeg)


if __name__ == '__main__':
    unittest.main()
