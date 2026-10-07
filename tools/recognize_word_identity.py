# SPDX-License-Identifier: MIT
"""Local FFmpeg decoding and CTranslate2 Whisper word identification only.

Uses installed helper modules directly so a PyAV decoder is not required.
Runtime and model caches are supplied as local command arguments, not Git paths.
"""
import argparse
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

p = argparse.ArgumentParser()
p.add_argument('--runtime', required=True)
p.add_argument('--model', required=True)
p.add_argument('--model-repo', default='Systran/faster-whisper-small')
p.add_argument('--input', required=True)
p.add_argument('--output', required=True)
p.add_argument('--language', default='id')
p.add_argument('--cuts', default='0,24')
p.add_argument('--ranges', help='JSON list of named source ranges in seconds; analyze in memory without exporting clips')
a = p.parse_args()
sys.path.insert(0, a.runtime)
import numpy as np
import ctranslate2
import imageio_ffmpeg
import tokenizers
from huggingface_hub import snapshot_download

def helper(name):
    spec = importlib.util.spec_from_file_location(name, Path(a.runtime) / 'faster_whisper' / (name + '.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

model_dir = Path(a.model)
if not (model_dir / 'model.bin').exists() or not any((model_dir / v).exists() for v in ['vocabulary.txt', 'vocabulary.json']):
    print('Downloading public Whisper model; audio stays local.', flush=True)
    snapshot_download(a.model_repo, local_dir=str(model_dir),
                      allow_patterns=['model.bin', 'config.json', 'tokenizer.json', 'preprocessor_config.json', 'vocabulary.txt', 'vocabulary.json'])
model = ctranslate2.models.Whisper(str(model_dir), device='cpu', compute_type='int8', intra_threads=8)
extractor = helper('feature_extractor').FeatureExtractor(feature_size=model.n_mels)
tok = helper('tokenizer').Tokenizer(tokenizers.Tokenizer.from_file(str(model_dir / 'tokenizer.json')),
                                    multilingual=True, task='transcribe', language=a.language)
raw = subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-v', 'error', '-i', a.input,
                      '-f', 'f32le', '-ac', '1', '-ar', '16000', '-'], check=True, stdout=subprocess.PIPE).stdout
y = np.frombuffer(raw, dtype='<f4')
duration = len(y) / 16000
cuts = [float(t) for t in a.cuts.split(',') if float(t) < duration] + [duration]
intervals = json.loads(Path(a.ranges).read_text(encoding='utf-8')) if a.ranges else [
    {'start': begin, 'end': end} for begin, end in zip(cuts, cuts[1:])]
output = {'backend': 'CTranslate2 Whisper / local FFmpeg', 'model_repo': a.model_repo, 'language': a.language,
          'duration_seconds': duration, 'segments': [], 'usage':'Word identity only; not cut boundaries, markers, timing, phoneme completeness or listening approval'}
for interval in intervals:
    begin, end = interval['start'], interval['end']
    assert 0 <= begin < end <= duration and end - begin <= 30, 'Invalid analysis interval'
    wave = y[round(begin * 16000):round(end * 16000)]
    mel = extractor(wave)
    frames = min(mel.shape[-1], 3000)
    mel = np.pad(mel[:, :3000], ((0, 0), (0, max(0, 3000-mel.shape[-1]))))
    features = ctranslate2.StorageView.from_array(np.ascontiguousarray(mel[None], dtype=np.float32))
    encoded = model.encode(features)
    generated = model.generate(encoded, [tok.sot_sequence + [tok.no_timestamps]], beam_size=5,
                               return_no_speech_prob=True)[0]
    tokens = [t for t in generated.sequences_ids[0] if t < tok.eot]
    text = tok.decode(tokens)
    output['segments'].append({**interval, 'text': text,
                               'no_speech_probability': generated.no_speech_prob})
    print(f'{interval.get("role", "")} {begin:.2f}-{end:.2f}: {text}', flush=True)
Path(a.output).write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding='utf-8')
print('Saved word-identity recognition only; no ASR boundary/timing output.', flush=True)
