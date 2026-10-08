# SPDX-License-Identifier: MIT
"""Shared input checks for the offline audio-review plotters."""
import argparse
import importlib
import json
import math
from pathlib import Path
import subprocess
import sys


def arguments(description, argv=None):
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument('--runtime', help='Optional directory containing installed Python dependencies')
    parser.add_argument('--input', required=True, help='Local source audio file')
    parser.add_argument('--ranges', required=True, help='JSON list of named source windows in seconds')
    parser.add_argument('--output', required=True, help='Review image, for example review.png')
    return parser.parse_args(argv)


def finite_number(value, label):
    try:
        valid = not isinstance(value, bool) and isinstance(value, (int, float)) and math.isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f'{label} must be a finite number')
    return value


def validate_ranges(rows, duration=None):
    if not isinstance(rows, list) or not rows:
        raise ValueError('Ranges must be a nonempty JSON list')
    for index, row in enumerate(rows, 1):
        if not isinstance(row, dict):
            raise ValueError(f'Range {index} must be an object')
        if not isinstance(row.get('role'), str) or not row['role'].strip():
            raise ValueError(f'Range {index} needs a nonblank role')
        start = finite_number(row.get('start'), f'Range {index} start')
        end = finite_number(row.get('end'), f'Range {index} end')
        if not 0 <= start < end:
            raise ValueError(f'Range {index} requires 0 <= start < end')
        if duration is not None and end > duration:
            raise ValueError(f'Range {index} exceeds the decoded source duration ({duration:.6f}s)')
    return rows


def load_ranges(path):
    with Path(path).open(encoding='utf-8-sig') as stream:
        return validate_ranges(json.load(stream))


def validate_paths(source, ranges, output):
    source, ranges, output = map(Path, (source, ranges, output))
    if not source.is_file():
        raise ValueError('Input must be an existing local audio file')
    if not ranges.is_file():
        raise ValueError('Ranges must be an existing JSON file')
    if output.resolve() in (source.resolve(), ranges.resolve()):
        raise ValueError('Output must not replace the source audio or ranges file')
    if output.exists() and (output.samefile(source) or output.samefile(ranges)):
        raise ValueError('Output must not replace the source audio or ranges file')
    if not output.parent.is_dir():
        raise ValueError('Output directory must already exist')


def dependencies(runtime=None):
    if runtime:
        path = Path(runtime)
        if not path.is_dir():
            raise ValueError('--runtime must be an existing dependency directory')
        sys.path.insert(0, str(path.resolve()))
    try:
        return (importlib.import_module('numpy'), importlib.import_module('imageio_ffmpeg'),
                importlib.import_module('PIL.Image'), importlib.import_module('PIL.ImageDraw'))
    except ImportError as error:
        raise ValueError('Install numpy, Pillow and imageio-ffmpeg in this Python environment '
                         'or provide their directory with --runtime') from error


def decode_audio(source, sample_rate, np, ffmpeg):
    try:
        result = subprocess.run(
            [ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', str(source), '-f', 'f32le',
             '-ac', '1', '-ar', str(sample_rate), 'pipe:1'],
            check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except subprocess.CalledProcessError as error:
        raise ValueError(f'FFmpeg could not decode the input audio (exit {error.returncode})') from error
    if not result.stdout or len(result.stdout) % 4:
        raise ValueError('Decoded audio must contain complete float32 samples')
    samples = np.frombuffer(result.stdout, dtype='<f4')
    if not np.isfinite(samples).all():
        raise ValueError('Decoded audio contains nonfinite samples')
    return samples
