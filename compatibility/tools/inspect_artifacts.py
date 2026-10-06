#!/usr/bin/env python3
"""Inventory original Maven AAR/JARs, including nested JARs; never decompile or execute them."""
import argparse
from collections import Counter, defaultdict
import hashlib
import io
import json
from pathlib import Path
import re
import struct
import xml.etree.ElementTree as ET
import zipfile

ANDROID = '{http://schemas.android.com/apk/res/android}'
TOOLS = '{http://schemas.android.com/tools}'

def sha256(data):
    return hashlib.sha256(data).hexdigest()


def utf8_constants(data):
    """Parse JVM constant-pool UTF8 entries (not accidental byte substrings)."""
    if data[:4] != b'\xca\xfe\xba\xbe':
        raise ValueError('Invalid class file')
    count = struct.unpack_from('>H', data, 8)[0]
    pos, index, values = 10, 1, []
    widths = {3: 4, 4: 4, 5: 8, 6: 8, 7: 2, 8: 2, 9: 4, 10: 4, 11: 4,
              12: 4, 15: 3, 16: 2, 17: 4, 18: 4, 19: 2, 20: 2}
    while index < count:
        tag = data[pos]
        pos += 1
        if tag == 1:
            length = struct.unpack_from('>H', data, pos)[0]
            pos += 2
            values.append(data[pos:pos + length].decode('utf-8', errors='replace'))
            pos += length
        else:
            pos += widths[tag]
            if tag in (5, 6):
                index += 1
        index += 1
    return values


def inventory(path, coordinate):
    path = Path(path)
    result = {'coordinate': coordinate, 'sha256': sha256(path.read_bytes()),
              'classes': [], 'packages': {}, 'nested_jars': [], 'native': [],
              'resources': [], 'android_resources': [], 'providers': [],
              'services': {}, 'consumer_rules': {}, 'metadata': {}, 'manifest': None,
              'ktor': {'original_classes': [], 'relocated_candidates': [],
                       'original_references': [], 'relocated_reference_candidates': []}, 'limitations': []}

    def scan(data, origin):
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            for info in archive.infolist():
                name = info.filename
                if info.is_dir():
                    continue
                location = f'{coordinate}!{origin}{name}'
                if name.endswith('.jar'):
                    result['nested_jars'].append(origin + name)
                    scan(archive.read(info), origin + name + '!')
                elif name.endswith('.class'):
                    result['classes'].append({'name': name, 'origin': location})
                    normalized = name.replace('.', '/')
                    if name.startswith('io/ktor/'):
                        result['ktor']['original_classes'].append(location)
                    elif '/ktor/' in normalized or 'ktor' in name.lower():
                        result['ktor']['relocated_candidates'].append(location)
                    try:
                        constants = utf8_constants(archive.read(info))
                        original, relocated = set(), set()
                        for value in constants:
                            original.update(re.findall(r'(?<![\w/$])(?:L)?io[/.]ktor[/.][\w/.$]+', value))
                            if 'ktor' in value.lower() and not re.search(r'(?<![\w/$])(?:L)?io[/.]ktor[/.]', value):
                                # Only type/package-like strings; no arbitrary embedded text or secrets.
                                relocated.update(re.findall(r'[\w/$]*ktor[\w/.$]*', value))
                        if original:
                            result['ktor']['original_references'].append({'origin': location, 'references': sorted(original)})
                        if relocated:
                            result['ktor']['relocated_reference_candidates'].append({'origin': location, 'references': sorted(relocated)})
                    except (ValueError, KeyError, IndexError, struct.error) as error:
                        result['limitations'].append(f'Class constant-pool parse failed: {location}: {type(error).__name__}')
                elif name.endswith('.so'):
                    parts = name.split('/')
                    result['native'].append({'path': name, 'abi': parts[-2], 'name': parts[-1],
                                             'origin': location, 'sha256': sha256(archive.read(info))})
                elif name.startswith('META-INF/services/'):
                    result['services'][location] = archive.read(info).decode('utf-8', errors='replace')
                    result['resources'].append({'name': name, 'origin': location})
                elif name in ('proguard.txt', 'consumer-rules.pro') or name.startswith('META-INF/proguard/'):
                    result['consumer_rules'][location] = archive.read(info).decode('utf-8', errors='replace')
                elif name.endswith('aar-metadata.properties'):
                    result['metadata'][name] = archive.read(info).decode('utf-8', errors='replace')
                elif name == 'AndroidManifest.xml':
                    try:
                        text = archive.read(info).decode('utf-8')
                        manifest = ET.fromstring(text)
                        result['manifest'] = text
                        for provider in manifest.iter('provider'):
                            for authority in provider.get(ANDROID + 'authorities', '').split(';'):
                                if authority:
                                    result['providers'].append({'authority': authority.replace('${applicationId}', 'com.complycube.compat'),
                                        'class': provider.get(ANDROID + 'name'), 'directive': provider.get(TOOLS + 'node'), 'origin': location})
                    except (UnicodeDecodeError, ET.ParseError):
                        result['limitations'].append(f'Binary/unreadable manifest: {location}; inspect AGP merged manifest')
                elif name == 'R.txt':
                    for line in archive.read(info).decode('utf-8', errors='replace').splitlines():
                        parts = line.split()
                        if len(parts) >= 3 and parts[1] != 'styleable':
                            result['android_resources'].append({'name': parts[1] + '/' + parts[2], 'origin': location})
                elif (origin or path.suffix == '.jar') and not name.startswith('META-INF/'):
                    result['resources'].append({'name': name, 'origin': location})
                elif name.startswith(('assets/', 'res/', 'META-INF/')):
                    result['resources'].append({'name': name, 'origin': location})
    scan(path.read_bytes(), '')
    result['packages'] = dict(sorted(Counter(x['name'].rsplit('/', 1)[0] for x in result['classes']).items()))
    return result


def collisions(inventories):
    result = []
    for kind, key in [('classes', 'name'), ('resources', 'name'), ('android_resources', 'name'),
                      ('providers', 'authority'), ('native', 'name')]:
        entries = defaultdict(set)
        for artifact in inventories:
            for item in artifact[kind]:
                if kind == 'providers' and item.get('directive') in ('remove', 'removeAll'):
                    continue
                name = (item['abi'] + '/' if kind == 'native' else '') + item[key]
                entries[name].add(item['origin'])
        for name, origins in sorted(entries.items()):
            if len(origins) > 1:
                result.append({'kind': kind, 'name': name, 'origins': sorted(origins),
                               'classification': 'STATIC_FINDING_REQUIRING_INVESTIGATION',
                               'proven_runtime_failure': False})
    return result


def publication(directory):
    directory = Path(directory)
    output = {}
    pom = directory / 'sdk.pom'
    module = directory / 'sdk.module'
    if pom.exists():
        ns = {'m': 'http://maven.apache.org/POM/4.0.0'}
        root = ET.parse(pom).getroot()
        output['pom_sha256'] = sha256(pom.read_bytes())
        output['pom_dependencies'] = [{n.tag.split('}')[-1]: n.text for n in dep}
            for dep in root.findall('./m:dependencies/m:dependency', ns)]
        output['pom_constraints'] = [{n.tag.split('}')[-1]: n.text for n in dep}
            for dep in root.findall('./m:dependencyManagement/m:dependencies/m:dependency', ns)]
    if module.exists():
        output['module_sha256'] = sha256(module.read_bytes())
        output['module_variants'] = json.loads(module.read_text()).get('variants', [])
    return output


def inspect_resolution(resolution, directory):
    artifacts = []
    for artifact in resolution['artifacts']:
        if Path(artifact['file']).suffix in ('.aar', '.jar'):
            artifacts.append(inventory(artifact['file'], artifact['coordinate']))
    sdk = next((a for a in artifacts if a['coordinate'] == resolution['sdk']), None)
    return {'sdk': sdk, 'publication': publication(directory),
            'artifacts': artifacts, 'collision_candidates': collisions(artifacts),
            'interpretation': 'Static candidates only; Android resource overlays and shared service descriptors may be intentional. Obfuscation can hide relocated names. Absence of matches is not proof of isolation.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('resolution', type=Path)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    args.out.write_text(json.dumps(inspect_resolution(json.loads(args.resolution.read_text()), args.resolution.parent), indent=2) + '\n')
