# AlQuran Open Source

Open production tools for carefully reviewed Quran recitation and spoken translation editions, intended to be free for listeners.

The project brings together source provenance, narration auditions, word-level review and DaVinci Resolve editing. Current production work uses Bahasa Indonesia. A dedicated Bahasa Malaysia edition is a future step requiring its own approved translation source and review.

**Current stage:** production tooling and an editorial workflow. This repository contains reusable software and current production rules; the listening application and public edition catalogue are future work. Recordings, translation corpora and private production records are managed separately.

## What is implemented

| Tool | Purpose |
| --- | --- |
| [`elevenlabs_client.py`](tools/elevenlabs_client.py) | Check configured service settings and request one authorized narration audition with a private provenance receipt. |
| [`recognize_word_identity.py`](tools/recognize_word_identity.py) | Identify spoken words locally with FFmpeg and Whisper to support human review. |
| [`plan_analysis_windows.py`](tools/plan_analysis_windows.py) | Find quiet-edge windows for speech analysis; these are candidate analysis intervals, not approved verse cuts. |
| [`resolve_mcp_client.py`](tools/resolve_mcp_client.py) | Send one tool request to an installed DaVinci Resolve MCP executable. |
| [`check_connected_groups.py`](tools/check_connected_groups.py) | Validate the evidence required before accepting connected-verse groups. |
| [`plot_audio_review_windows.py`](tools/plot_audio_review_windows.py) | Plot source windows for detailed audio review. |
| [`plot_mirrored_audio_review.py`](tools/plot_mirrored_audio_review.py) | Compare review windows using mirrored waveforms. |

A technically valid map or successful API request does not establish correct wording or listening approval. The [production workflow](docs/production-workflow.md) and [current production rules](docs/production-rules.md) describe those separate review gates.

## Get started

Python 3.10 or newer is required. The narration client and Resolve transport use the standard library. Speech and visualization tools need their separately installed dependencies; see [setup](docs/setup.md).

```sh
python tools/elevenlabs_client.py --help
python tools/elevenlabs_client.py audition --help
```

Set `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` and, if needed, `ELEVENLABS_MODEL_ID` in your local environment. [`.env.example`](.env.example) lists the variables; the scripts do not load dotenv files automatically. Use your own authorized voice. The inherited model default is `eleven_v4`; check availability and request limits for your account before generating.

```sh
python tools/elevenlabs_client.py check
```

`check` makes read-only service requests and can display account details. Keep that output private.

For an explicitly authorized audition, create a temporary directory **outside this repository**, then substitute its path below. Keep the approved prompt in local storage as well:

```sh
python tools/elevenlabs_client.py audition --prompt /path/to/approved-prompt.txt --output-prefix /path/to/temporary-auditions/audition
```

**Generation is a paid API operation.** The client sends one take, refuses existing output names and never automatically retries a paid request. Keep audition audio and its receipt together privately. Move only the accepted reading to production storage after listening approval; the client does not edit a Resolve timeline.

## How the project works

1. Identify the source edition, verse range and distribution permissions.
2. Preserve canonical text separately from approved spoken adaptations.
3. Authorize a narration request, listen and select an accepted reading.
4. Verify complete words and source boundaries using recognition, waveforms and listening.
5. Apply approved edits in Resolve while preserving existing manual work.
6. Verify native playback and obtain final listening approval before publishing an edition.

See [architecture](docs/architecture.md), [current status and roadmap](docs/project-status.md), and the detailed [workflow](docs/production-workflow.md).

## Development

Use synthetic or independently licensed fixtures. Offline tests must not generate paid audio or edit an active Resolve project.

```sh
python -m unittest discover -s tests -v
```

Submit focused pull requests following [CONTRIBUTING.md](CONTRIBUTING.md). `main` has active deletion and force-push protections; contributor changes require an approved pull request. The repository owner retains the existing direct-update exception.

## License and source rights

Original code and project-authored documentation use the [MIT License](LICENSE). Translation editions, recitations, voices, models and proprietary services have separate rights. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

This is the canonical public repository for AlQuran's reusable tools and documentation. Private account settings, media and production history are not required to browse or contribute to it.
