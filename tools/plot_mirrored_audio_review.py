# SPDX-License-Identifier: MIT
"""Plot both waveform polarities from the source, without audio exports."""
import sys

from _audio_review import (arguments, decode_audio, dependencies, finite_number,
                           load_ranges, validate_paths, validate_ranges)

SAMPLE_RATE = 48000
WIDTH, ROW_HEIGHT, LEFT, RIGHT = 1900, 250, 90, 1840


def validate_markers(rows):
    for index, row in enumerate(rows, 1):
        if row.get('candidate_lines'):
            raise ValueError('candidate_lines are not accepted for signed waveform review; '
                             'use labeled acoustic markers instead')
        markers = row.get('markers', [])
        if not isinstance(markers, list):
            raise ValueError(f'Range {index} markers must be a list')
        for marker in markers:
            if not isinstance(marker, dict):
                raise ValueError(f'Range {index} marker must be an object')
            finite_number(marker.get('seconds'), f'Range {index} marker seconds')
            if not isinstance(marker.get('label'), str) or not marker['label'].strip():
                raise ValueError(f'Range {index} marker needs a nonblank label')
            label_y = finite_number(marker.get('label_y', 30), f'Range {index} marker label_y')
            if not 0 <= label_y < ROW_HEIGHT:
                raise ValueError(f'Range {index} marker label_y must fit its image row')
            if not isinstance(marker.get('color', '#56d9ff'), str):
                raise ValueError(f'Range {index} marker color must be a color string')


def render(samples, rows, np, Image, ImageDraw):
    validate_ranges(rows, len(samples) / SAMPLE_RATE)
    validate_markers(rows)
    if not len(samples) or not np.isfinite(samples).all():
        raise ValueError('Audio must contain finite samples')
    windows = []
    for index, row in enumerate(rows, 1):
        start, stop = round(row['start'] * SAMPLE_RATE), round(row['end'] * SAMPLE_RATE)
        if not 0 <= start < stop <= len(samples):
            raise ValueError(f'Range {index} must contain at least one decoded source sample')
        windows.append((start, stop))
    image = Image.new('RGB', (WIDTH, ROW_HEIGHT * len(rows)), '#182622')
    draw = ImageDraw.Draw(image)
    for index, (row, (start, stop)) in enumerate(zip(rows, windows)):
        low, high, top = row['start'], row['end'], index * ROW_HEIGHT
        center = top + 118
        scale = max(float(np.max(np.abs(samples[start:stop]))), 1e-9)

        def xx(time):
            return LEFT + (time - low) / (high - low) * (RIGHT - LEFT)

        draw.text((12, top + 7), row['role'] + ' | Full signed waveform; range display scale '
                  + f'{scale:.4f}', fill='white')
        draw.line([(LEFT, center), (RIGHT, center)], fill='#8fa099')
        for pixel in range(RIGHT - LEFT):
            # Clamp narrow windows so no display pixel reads beyond the requested source interval.
            first = min(stop - 1, round(start + pixel / (RIGHT - LEFT) * (stop - start)))
            end = min(stop, max(first + 1, round(start + (pixel + 1) / (RIGHT - LEFT) * (stop - start))))
            values = samples[first:end]
            upper = center - 85 * float(np.max(values)) / scale
            lower = center - 85 * float(np.min(values)) / scale
            draw.line([(LEFT + pixel, upper), (LEFT + pixel, lower)], fill='#a5dcb1')
        for time in np.arange(low, high + .00001, .1 if high - low <= 2 else .2):
            x = xx(time)
            draw.line([(x, top + 28), (x, top + 209)], fill='#294338', width=1)
            draw.text((x - 15, top + 216), f'{time:.2f}', fill='#d4ded9')
        for marker in row.get('markers', []):
            time = marker['seconds']
            if not low <= time <= high:
                continue
            x, color = xx(time), marker.get('color', '#56d9ff')
            draw.line([(x, top + 27), (x, top + 209)], fill=color, width=2)
            draw.text((x + 3, top + marker.get('label_y', 30)), marker['label'], fill=color)
    return image


def main(argv=None):
    args = arguments(__doc__, argv)
    try:
        validate_paths(args.input, args.ranges, args.output)
        rows = load_ranges(args.ranges)
        validate_markers(rows)
        np, ffmpeg, Image, ImageDraw = dependencies(args.runtime)
        samples = decode_audio(args.input, SAMPLE_RATE, np, ffmpeg)
        render(samples, rows, np, Image, ImageDraw).save(args.output)
    except (ValueError, OSError, RuntimeError) as error:
        print(f'Error: {error}', file=sys.stderr)
        return 1
    print(args.output)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
