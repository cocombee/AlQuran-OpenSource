# Local setup

Use Python 3.10 or newer and a dedicated local virtual environment. Install only the dependencies for the tools you use. External accounts, applications, media and model weights are not bundled.

| Tools | Dependencies |
| --- | --- |
| Narration client | Python standard library; your authorized ElevenLabs account/voice for network operations |
| Connected-group validator | Python standard library |
| Word recognition and analysis windows | NumPy, imageio-ffmpeg; recognition also uses CTranslate2, tokenizers, huggingface-hub and faster-whisper helper modules |
| Waveform plots | See the tool help and [review tools](review-tools.md) for the rendering dependencies and input format |
| Resolve transport | Compatible local Resolve installation with its official MCP executable |

Speech commands use an explicit `--runtime` directory containing the dependency modules. Recognition also takes a local `--model` path. If model files are absent it may download the selected public model; source audio stays local. Check the relevant model and dependency licenses. Supply explicit reviewed `--ranges` for long recordings; each recognition interval must be at most 30 seconds. No recognition timestamp is an approved edit boundary.

Use each tool's `--help` before running it. Paths in the README are illustrative and must be replaced with your own local paths. The tools do not automatically load `.env` files.

## Audition storage

Create a temporary audition directory outside the repository before generating. Keep pending audio and request receipts there, outside production media. The output prefix must be unused. Promote only an accepted complete reading after listening approval and preserve its provenance privately.

The client sends one paid take per command and does not retry automatically. Inspect an uncertain request in your service account before authorizing another. `check` performs read-only network requests; its account output is private.

## Offline checks

```sh
python -m unittest discover -s tests -v
```

Tests use synthetic inputs and mocks. They do not certify religious wording, provider availability, real audio quality or a live Resolve project. No paid request is needed to run them.
