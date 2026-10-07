# AlQuran Open Source

Open tools for producing carefully reviewed spoken Quran translation editions.

AlQuran's mission is to provide Quran recitation with narration of existing published translations free of charge to listeners. The initial production work is in Bahasa Indonesia. Malaysian listeners are an intended additional audience; a dedicated Bahasa Malaysia edition requires its own approved translation, narration and review.

This is a voice-production and accessibility project using existing translation sources. The potential reach includes Indonesia and Malaysia; population size is an audience estimate, and this release makes no claim of that many current users or completed coverage.

## What this release includes

Four tools extracted from the project's production workflow:

| Tool | Purpose |
| --- | --- |
| `tools/elevenlabs_client.py` | Inspect configured voice/model/account settings and request one narration audition with a provenance receipt. |
| `tools/recognize_word_identity.py` | Identify spoken words locally using FFmpeg and Whisper. Recognition supports review; it does not establish safe edit boundaries. |
| `tools/plan_analysis_windows.py` | Plan quiet-edge source windows for local speech analysis. These are analysis windows, not approved verse cuts. |
| `tools/resolve_mcp_client.py` | Send one tool request to an installed official DaVinci Resolve MCP executable. |

This initial release provides production utilities. It is not a finished Quran listening application and does not include published audio, translation corpora, voice models, private review records or media-library access.

## Requirements

- Python 3.10 or newer.
- The ElevenLabs client uses Python's standard library. Generation requires your own authorized voice and service account.
- Speech-analysis tools require NumPy, CTranslate2, tokenizers, huggingface-hub, faster-whisper and imageio-ffmpeg in a local Python runtime. Those dependencies and their model licenses apply separately.
- The Resolve helper requires a compatible local Resolve installation and its official MCP executable. Its current pipe reader uses POSIX `select`; this helper is intended for macOS/Linux. Windows support is a contribution opportunity.

## Start with the narration client

```sh
python tools/elevenlabs_client.py --help
python tools/elevenlabs_client.py audition --help
```

Configure `ELEVENLABS_API_KEY`, `ELEVENLABS_VOICE_ID` and optionally `ELEVENLABS_MODEL_ID` in your local environment. See `.env.example` for variable names; the scripts do not automatically load dotenv files. The inherited default model is `eleven_v4`; availability and request limits must be checked against your account before use.

`check` sends read-only service requests and may show account usage details. Keep its output private:

```sh
python tools/elevenlabs_client.py check
```

Place a prompt you have permission to use in `work/approved-prompt.txt`, create `outputs/`, then request one audition:

```sh
python tools/elevenlabs_client.py audition --prompt work/approved-prompt.txt --output-prefix outputs/audition
```

**Audition generation is a paid API operation.** Free access for listeners is the project's distribution goal; it does not make third-party production services free. The client sends one take, records the prompt hash and service request metadata, refuses to overwrite existing outputs and does not automatically retry paid requests.

## Production review

See [the workflow](docs/workflow.md) for source provenance, narration approval, complete-word boundaries and native playback review. Canonical translation text must remain distinguishable from any separately permitted speech adaptation. Arabic and translation meaning require qualified human review before publication.

## Contributing and licensing

Read [CONTRIBUTING.md](CONTRIBUTING.md). Original code and project-authored documentation in this release are provided under the [MIT License](LICENSE). Translation text, recitation recordings, generated audio, voices, service software and models have separate rights; see [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

The public tooling is intended to help other producers build accurate, affordable narration workflows. Initial priorities include portable configuration, Windows Resolve support, stronger offline tests and accessible listening interfaces.
