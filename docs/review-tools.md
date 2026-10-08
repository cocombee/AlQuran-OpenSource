# Source review tools

These tools support source-specific review. A plot or a complete evidence record does not independently establish correct words, approved edit boundaries or listening approval. They do not generate narration, export audio slices or change Resolve timelines.

## Connected-group evidence

`check_connected_groups.py` uses Python's standard library:

```sh
python tools/check_connected_groups.py path/to/review.json
```

It checks that every internal boundary in a multi-ayah group has a unique review tied to the same recording hash, actual outgoing/incoming word fields, word/context and signed-waveform evidence, a continuous-delivery decision, no ASR timing as an edit anchor, and a finite source-review window of at most eight seconds. The evidence references are checked for presence; the tool does not open them or certify their contents.

The document accepts `rows` (preferred) or `groups`. Groups use `ayah` or `from_ayah`, and `to_ayah`. The recording hash is `source_sha256`, with `sources.Arabic.sha256` as a fallback. Each multi-ayah group supplies `internal_boundary_reviews`, one for each `after_ayah` from its first ayah through the ayah before its last. Review fields are:

| Field | Required value |
| --- | --- |
| `source_sha256` | Same recording hash as the document |
| `decision` | `continuous` |
| `outgoing_word`, `incoming_word` | Nonblank text identifying the observed words |
| `word_context_evidence`, `signed_review_evidence` | Nonblank text or a nonempty list/object of review references |
| `reason` | `actual_voiced_join_without_independent_stop` |
| `ASR_timing_used` | `false` |
| `source_review_window` | `[start, end]` in source seconds, with `0 <= start < end` and duration at most eight seconds |

Single-ayah groups require no internal-boundary reviews. A document with neither collection is treated as empty. Successful validation exits `0`; invalid input exits `2`. Checks remain active with Python optimization enabled.

## Waveform plots

Both plotters need **NumPy, Pillow and imageio-ffmpeg**, in addition to Python 3.10+:

```sh
python -m pip install numpy Pillow imageio-ffmpeg
```

Dependencies can be installed in the current Python environment, or supplied using `--runtime path/to/dependency-directory`. FFmpeg is obtained through imageio-ffmpeg. Inputs must be local audio files. The complete source is decoded in memory, so available memory must accommodate it.

Create a JSON list of review windows. This example contains fictional labels and times:

```json
[
  {
    "role": "Synthetic review window",
    "start": 0.0,
    "end": 1.0,
    "markers": [{"seconds": 0.5, "label": "Acoustic observation"}]
  }
]
```

Choose windows within your source's duration, create the output directory, then run:

```sh
python tools/plot_audio_review_windows.py --input source.wav --ranges windows.json --output outputs/rms-review.png
python tools/plot_mirrored_audio_review.py --input source.wav --ranges windows.json --output outputs/signed-review.png
```

- **RMS context:** decodes mono audio at 16 kHz, computes 5 ms RMS bins and plots decibel context. Optional `candidate_lines` is a list of times inside the window; these are visual candidates, never approved boundaries. A window must contain at least one complete RMS bin.
- **Signed waveform:** decodes mono audio at 48 kHz and retains the positive maximum and negative minimum per display column. Each row scales to its own peak; rows therefore cannot establish relative loudness. It accepts labeled acoustic `markers`, with optional `color` and `label_y` (0–249). Markers outside a particular window are ignored. Legacy `candidate_lines` is rejected for this view.

Both accept the same `--input`, `--ranges`, `--output` and optional `--runtime` flags. Ranges need a nonblank `role` and finite times satisfying `0 <= start < end <= source duration`. Empty lists, reversed/out-of-source windows and nonfinite samples fail clearly. Output directories must exist. Existing output images are replaced; the output may not alias the source audio or ranges file. Failures exit `1` and do not certify the input.

Source labels and evidence can be sensitive. Use fictional fixtures in contributions, and review exported images before sharing.

## Offline tests

```sh
python -B -m unittest discover -s tests -p 'test_*.py'
python -B -O -m unittest discover -s tests -p 'test_*.py'
```

The new tests use fictional review records and generated waveforms. Validator/input checks use the standard library; rendering checks require NumPy and Pillow and report skips if these are absent. They cover invalid bounds, optimization-safe rejection, waveform polarity, one-sample windows, source-file protection and decoder error handling. No service requests, real source recordings or live Resolve session are used.
