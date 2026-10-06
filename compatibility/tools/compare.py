#!/usr/bin/env python3
"""Compare one SDK run with its matching SDK-free control without inferring causation."""
import argparse
import json
from pathlib import Path


def compare(sdk, control):
    if sdk['scenario'] != control['scenario'] or sdk['control'] or not control['control']:
        raise ValueError('Supply an SDK run and its matching scenario control')
    if sdk['requested_toolchain'] != control['requested_toolchain'] or sdk['device'] != control['device']:
        raise ValueError('Controls must have the same toolchain and device tuple')
    findings = []
    for name in ('build_packaging', 'host_runtime', 'minified_runtime'):
        if sdk['phases'][name]['status'] == 'FAIL':
            classification = ('HOST_FAILURE_ALSO_PRESENT_WITHOUT_SDK' if control['phases'][name]['status'] == 'FAIL'
                              else 'SDK_ASSOCIATED_DIFFERENCE_REQUIRES_INVESTIGATION')
            findings.append({'phase': name, 'classification': classification,
                'reason': 'Compare exact errors and flows before calling this a reproduced incompatibility.'})
    return {'scenario': sdk['scenario'], 'findings': findings,
            'reproduced_sdk_host_incompatibility': False}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('sdk', type=Path)
    parser.add_argument('control', type=Path)
    args = parser.parse_args()
    print(json.dumps(compare(json.loads(args.sdk.read_text()), json.loads(args.control.read_text())), indent=2))
