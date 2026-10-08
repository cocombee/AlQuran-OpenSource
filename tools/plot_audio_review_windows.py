# SPDX-License-Identifier: MIT
"""Draw source RMS context around uncertain boundaries; candidates only."""
import sys

from _audio_review import (arguments, decode_audio, dependencies, finite_number,
                           load_ranges, validate_paths, validate_ranges)

SAMPLE_RATE = 16000
BIN_SAMPLES = 80
BIN_SECONDS = BIN_SAMPLES / SAMPLE_RATE


def validate_candidates(rows):
    for index, row in enumerate(rows, 1):
        lines = row.get('candidate_lines', [])
        if not isinstance(lines, list):
            raise ValueError(f'Range {index} candidate_lines must be a list')
        for value in lines:
            value = finite_number(value, f'Range {index} candidate line')
            if not row['start'] <= value <= row['end']:
                raise ValueError(f'Range {index} candidate line lies outside its window')


def render(samples, rows, np, Image, ImageDraw):
    validate_ranges(rows, len(samples) / SAMPLE_RATE)
    validate_candidates(rows)
    if len(samples) < BIN_SAMPLES:
        raise ValueError('RMS review needs at least 5 milliseconds of source audio')
    if not np.isfinite(samples).all():
        raise ValueError('Audio contains nonfinite samples')
    bins = samples[:len(samples) // BIN_SAMPLES * BIN_SAMPLES].reshape(-1, BIN_SAMPLES)
    rms = 20 * np.log10(np.maximum(np.sqrt(np.mean(bins * bins, axis=1)), 1e-10))
    indexes = []
    for index, row in enumerate(rows, 1):
        first = max(0, int(row['start'] / BIN_SECONDS))
        stop = min(len(rms), int(row['end'] / BIN_SECONDS))
        if stop <= first:
            raise ValueError(f'Range {index} contains no complete 5-millisecond RMS bin')
        indexes.append(range(first, stop))
    image = Image.new('RGB', (1800, 240 * len(rows)), 'white')
    draw = ImageDraw.Draw(image)
    for index, (row, bins_in_window) in enumerate(zip(rows, indexes)):
        low, high, top = row['start'], row['end'], index * 240

        def xy(time, db):
            return (90 + (time - low) / (high - low) * 1650,
                    top + 185 - (max(-80, min(0, float(db))) + 80) * 1.7)

        draw.text((10, top + 2), row['role'] + ' | Source context; not verified', fill='black')
        for db in [-60, -45, -30, -15, 0]:
            draw.line([xy(low, db), xy(high, db)], fill='#ddd')
            draw.text((10, xy(low, db)[1]), str(db), fill='black')
        points = [xy(j * BIN_SECONDS, rms[j]) for j in bins_in_window]
        if len(points) == 1:
            draw.point(points[0], fill='#176eb5')
        else:
            draw.line(points, fill='#176eb5', width=2)
        for time in np.arange(low, high, .25 if high - low < 6 else .5):
            draw.text((xy(time, -80)[0] - 15, top + 200), f'{time:.2f}', fill='black')
        for time in row.get('candidate_lines', []):
            draw.line([xy(time, -80), xy(time, 0)], fill='red', width=2)
    return image


def main(argv=None):
    args = arguments(__doc__, argv)
    try:
        validate_paths(args.input, args.ranges, args.output)
        rows = load_ranges(args.ranges)
        validate_candidates(rows)
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
