# SPDX-License-Identifier: MIT
"""Direct ElevenLabs client. Default checks are read-only; no dependencies required."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import sys
import urllib.error
import urllib.request

TASK_ROOT = Path(__file__).resolve().parent.parent
KEY_FILE = TASK_ROOT / '.elevenlabs.local.json'
VOICE_ID = os.environ.get('ELEVENLABS_VOICE_ID', '').strip()
MODEL_ID = os.environ.get('ELEVENLABS_MODEL_ID', 'eleven_v4').strip()
# Verified against /v1/models and official Eleven v4 docs on 2026-10-05.
MODEL_REQUEST_CHARACTER_LIMIT = 10000
VOICE_SETTINGS = {'stability': 0.5, 'similarity_boost': 0.75}


def api_key():
    if not VOICE_ID:
        raise RuntimeError('Set ELEVENLABS_VOICE_ID to a voice you are authorized to use; no request sent.')
    key = os.environ.get('ELEVENLABS_API_KEY', '').strip()
    if not key and KEY_FILE.is_file():
        if KEY_FILE.stat().st_mode & 0o077:
            raise RuntimeError('Local credential file must have owner-only permissions (0600).')
        key = json.loads(KEY_FILE.read_text())['api_key'].strip()
    if not key:
        raise RuntimeError('No ElevenLabs API key configured; no request sent.')
    return key


def request(path, body=None):
    headers = {'xi-api-key': api_key(), 'Accept': 'application/json' if body is None else 'audio/mpeg'}
    payload = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        payload = json.dumps(body).encode('utf-8')
    req = urllib.request.Request('https://api.elevenlabs.io/v1/' + path,
                                 data=payload, headers=headers,
                                 method='GET' if body is None else 'POST')
    try:
        with urllib.request.urlopen(req, timeout=180) as response:
            data = response.read()
            metadata = {k: response.headers.get(k) for k in ['request-id', 'character-cost', 'content-type']}
            return (json.loads(data) if body is None else data), metadata
    except urllib.error.HTTPError as error:
        # No automatic retries: a generation might already have been charged.
        raise RuntimeError('ElevenLabs returned HTTP %s; inspect the account request log before retrying.' % error.code) from None
    except urllib.error.URLError:
        raise RuntimeError('API connection failed; inspect the account request log before retrying a generation.') from None


def check():
    subscription, _ = request('user/subscription')
    models, _ = request('models')
    voice, _ = request('voices/' + VOICE_ID)
    model = next((m for m in models if m['model_id'] == MODEL_ID), None)
    if model is None or not model.get('can_do_text_to_speech'):
        raise RuntimeError('Regular Eleven v4 is not available for text-to-speech through this API connection.')
    if voice.get('voice_id') != VOICE_ID:
        raise RuntimeError('Voice identity mismatch; generation blocked.')
    return {'authenticated': True, 'read_only': True, 'generation_requests': 0,
            'model_id': MODEL_ID, 'model_name': model.get('name'),
            'voice_id': VOICE_ID, 'voice_name': voice.get('name'),
            'voice_settings': VOICE_SETTINGS, 'voice_category': voice.get('category'),
            'voice_sharing': {k: voice.get('sharing', {}).get(k) for k in ['rate', 'voice_mixing_allowed']} if voice.get('sharing') else None,
            'subscription': {k: subscription.get(k) for k in ['tier', 'status', 'character_count', 'character_limit', 'currency']},
            'output_format': 'mp3_44100_128'}


def audition(prompt_path, output_prefix, takes):
    text = Path(prompt_path).read_text(encoding='utf-8').strip()
    if not text or len(text) > MODEL_REQUEST_CHARACTER_LIMIT:
        raise RuntimeError('Approved input must contain 1–10,000 characters including all cues for verified Eleven v4.')
    prefix = Path(output_prefix).resolve()
    if TASK_ROOT not in prefix.parents:
        raise RuntimeError('Audition outputs must stay inside the canonical task.')
    destinations = [Path(str(prefix) + ' - Generation %s.mp3' % n) for n in range(1, takes + 1)]
    receipt_path = Path(str(prefix) + ' - API Receipt.json')
    if any(p.exists() for p in destinations + [receipt_path]):
        raise RuntimeError('Output already exists; choose a new audition version.')
    if not prefix.parent.is_dir():
        raise RuntimeError('Output directory must already exist.')
    receipt = {'prompt_file': str(Path(prompt_path).resolve().relative_to(TASK_ROOT)),
               'prompt_sha256': hashlib.sha256(text.encode()).hexdigest(),
               'characters_per_request': len(text), 'verified_model_character_limit': MODEL_REQUEST_CHARACTER_LIMIT, 'requested_takes': takes,
               'model_id': MODEL_ID, 'voice_id': VOICE_ID, 'voice_settings': VOICE_SETTINGS,
               'output_format': 'mp3_44100_128', 'takes': [],
               'human_approval': 'pending', 'timeline_placement': 'not performed'}
    receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    for number, destination in enumerate(destinations, 1):
        audio, metadata = request('text-to-speech/' + VOICE_ID + '?output_format=mp3_44100_128',
                                  {'text': text, 'model_id': MODEL_ID, 'voice_settings': VOICE_SETTINGS})
        if not audio or 'audio/' not in (metadata.get('content-type') or ''):
            raise RuntimeError('Unexpected response; inspect the request log before retrying.')
        with destination.open('xb') as output:
            output.write(audio)
        receipt['takes'].append({'generation': number, 'file': str(destination.relative_to(TASK_ROOT)),
                                 'bytes': len(audio), 'sha256': hashlib.sha256(audio).hexdigest(),
                                 'response': metadata})
        receipt_path.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
        print(json.dumps(receipt['takes'][-1]), flush=True)
    return receipt


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='operation', required=True)
    sub.add_parser('check', help='Read-only authentication, model, voice and subscription checks.')
    generate = sub.add_parser('audition', help='One paid generation; another requires explicit user instruction.')
    generate.add_argument('--prompt', required=True)
    generate.add_argument('--output-prefix', required=True)
    generate.add_argument('--takes', type=int, choices=[1], default=1)
    args = parser.parse_args()
    try:
        result = check() if args.operation == 'check' else audition(args.prompt, args.output_prefix, args.takes)
        print(json.dumps(result, indent=2))
    except (RuntimeError, OSError, KeyError, ValueError) as error:
        print(str(error), file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
