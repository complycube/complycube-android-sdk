#!/usr/bin/env python3
"""CI's credential-free gate is explicitly narrower than overall compatibility."""
import argparse
import json
from pathlib import Path


def gate(result, runtime=False):
    required = ['resolution', 'scenario_validity', 'build_packaging']
    failures = [name for name in required if result['phases'][name]['status'] != 'PASS']
    if runtime:
        for variant in ('debug', 'release'):
            if result.get('variants', {}).get(variant, {}).get('host_runtime', {}).get('status') != 'PASS':
                failures.append(f'{variant}.host_runtime')
    return failures


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('result', type=Path)
    parser.add_argument('--runtime', action='store_true')
    args = parser.parse_args()
    result = json.loads(args.result.read_text())
    failures = gate(result, args.runtime)
    print('Credential-free gate: ' + ('FAIL: ' + ', '.join(failures) if failures else 'PASS'))
    print('Overall compatibility remains ' + result['overall'])
    raise SystemExit(bool(failures))
