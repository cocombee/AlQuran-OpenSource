# SPDX-License-Identifier: MIT
"""One-shot client for Blackmagic's installed local Resolve MCP, no dependencies.

Input is a JSON object with name/arguments. Resolve scripts use run_script unless
filesystem access inside Resolve is actually needed. Never changes Codex config.
"""
import json
import os
from pathlib import Path
import select
import subprocess
import sys
import time

def call(name, arguments):
    binary = os.environ.get('RESOLVE_MCP_BINARY')
    if not binary and sys.platform == 'darwin':
        binary = '/Applications/DaVinci Resolve/DaVinci Resolve.app/Contents/Applications/ResolveMCP'
    if not binary or not Path(binary).is_file():
        raise RuntimeError('Set RESOLVE_MCP_BINARY to the installed official ResolveMCP executable')
    proc = subprocess.Popen([binary], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                            stderr=subprocess.DEVNULL, text=True, encoding='utf-8',
                            env={**os.environ, 'BMD_IS_MCPB': '1'})
    def request(ident, method, params):
        proc.stdin.write(json.dumps(dict(jsonrpc='2.0', id=ident, method=method, params=params)) + '\n')
        proc.stdin.flush()
        deadline = time.monotonic() + arguments.get('timeout', 10) + 20
        while time.monotonic() < deadline:
            if not select.select([proc.stdout], [], [], 1)[0]:
                if proc.poll() is not None:
                    raise RuntimeError('Resolve MCP exited')
                continue
            line = proc.stdout.readline()
            if not line:
                continue
            reply = json.loads(line)
            if reply.get('id') != ident:
                continue
            if 'error' in reply:
                raise RuntimeError(reply['error'])
            return reply['result']
        raise TimeoutError('Resolve MCP response timed out; inspect actual state before retrying a mutation')
    try:
        request(1, 'initialize', {})
        proc.stdin.write('{"jsonrpc":"2.0","method":"notifications/initialized"}\n')
        proc.stdin.flush()
        reply = request(2, 'tools/call', dict(name=name, arguments=arguments))
        if reply.get('isError'):
            raise RuntimeError(reply)
        return reply
    finally:
        proc.terminate()
        proc.wait(timeout=5)

if __name__ == '__main__':
    request = json.load(sys.stdin)
    print(json.dumps(call(request['name'], request.get('arguments', {})), ensure_ascii=False))
