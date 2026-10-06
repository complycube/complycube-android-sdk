#!/usr/bin/env python3
"""Small, fail-closed consumer runner. Python standard library only."""
import argparse
import datetime
import fnmatch
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import xml.etree.ElementTree as ET

from inspect_artifacts import inspect_resolution

ROOT = Path(__file__).resolve().parents[1]
MATRIX = json.loads((ROOT / 'matrix.json').read_text())
STATUSES = ('PASS', 'FAIL', 'BLOCKED', 'NOT_RUN')
PHASES = ('resolution', 'scenario_validity', 'build_packaging', 'host_runtime', 'sdk_runtime', 'minified_runtime')


# Self-instrumenting driver package; see shared/driver/build.gradle.
DRIVER = 'com.complycube.compat.driver'


def harness_fingerprint():
    digest = hashlib.sha256()
    files = [ROOT / 'matrix.json'] + list((ROOT / 'shared').rglob('*'))
    for host in ('baseline-host', 'modern-host'):
        files += [ROOT / host / name for name in ('build.gradle', 'settings.gradle', 'gradle.properties', 'gradlew', 'gradle/wrapper/gradle-wrapper.properties', 'gradle/wrapper/gradle-wrapper.jar')]
    for file in sorted(files):
        if file.is_file():
            digest.update(str(file.relative_to(ROOT)).encode())
            digest.update(file.read_bytes())
    return digest.hexdigest()


def exact_version(value):
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9]+(?:[.-][A-Za-z0-9]+)*)?', value) or value.endswith('SNAPSHOT'):
        raise argparse.ArgumentTypeError('Use an exact immutable release version')
    return value


def redact(text, secrets=()):
    for secret in sorted(set(secrets), key=len, reverse=True):
        if len(secret) >= 4:
            text = text.replace(secret, '[REDACTED]')
    text = re.sub(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+', '[REDACTED_JWT]', text)
    text = re.sub(r'(?i)(Bearer\s+)[^\s"<>]+', r'\1[REDACTED]', text)
    text = re.sub(r'(?i)((?:sdkToken|token|clientId|api[_-]?key|password|authorization)["\s]*[:=]["\s]*)[^\s,"<>}&]+', r'\1[REDACTED]', text)
    text = re.sub(r'(https?://)[^/@\s]+:[^/@\s]+@', r'\1[REDACTED]@', text)
    return text.replace(str(Path.home()), '$HOME')


def phase(status='NOT_RUN', reason='Not requested', evidence=None):
    assert status in STATUSES
    return {'status': status, 'reason': reason, 'evidence': evidence or []}


def aggregate(values):
    statuses = [v['status'] for v in values]
    for status in ('FAIL', 'BLOCKED', 'NOT_RUN'):
        if status in statuses:
            return status
    return 'PASS' if statuses else 'NOT_RUN'


def validate_resolution(data, scenario, control, sdk, expected_hash, inspection):
    problems = []
    components = data['components']
    expected = dict(scenario['expected'])
    forbidden = list(scenario.get('forbidden', []))
    if control:
        # No SDK family expectation in a control unless the host requested it.
        expected = {k: v for k, v in expected.items()
                    if (scenario['family'] == 'ktor' and k.startswith('io.ktor:')) or
                       (scenario['family'] == 'compose' and k.startswith('androidx.compose'))}
        # Only modules deliberately requested by the Compose control are required.
        if scenario['family'] == 'compose':
            expected.pop('androidx.compose.material:material-android', None)
        if any(c.startswith('com.complycube:') for c in components):
            problems.append('SDK leaked into SDK-free control')
    else:
        if sdk not in components:
            problems.append('Exact requested SDK coordinate did not resolve')
        artifact = inspection.get('sdk')
        if not artifact:
            problems.append('Resolved SDK AAR missing from inspection')
        elif expected_hash and artifact['sha256'] != expected_hash:
            problems.append('SDK checksum differs from pinned publication')
    for pattern, version in expected.items():
        matches = [c for c in components if len(c.split(':')) == 3 and fnmatch.fnmatchcase(':'.join(c.split(':')[:2]), pattern)]
        if not matches:
            problems.append(f'Missing expected dependency {pattern}:{version}')
        for component in matches:
            if component.rsplit(':', 1)[1] != version:
                problems.append(f'Expected {pattern}:{version}, selected {component}')
    for pattern in forbidden:
        matches = [c for c in components if len(c.split(':')) == 3 and fnmatch.fnmatchcase(':'.join(c.split(':')[:2]), pattern)]
        if matches:
            problems.append(f'Forbidden dependency family resolved for isolated scenario {pattern}: {", ".join(matches)}')
    tools = MATRIX['toolchains'][scenario['host']]
    for key in ('gradle', 'agp', 'kotlin', 'buildTools'):
        if str(data['toolchain'][key]) != str(tools[key]):
            problems.append(f'Wrong {key}: {data["toolchain"][key]} (expected {tools[key]})')
    if data['toolchain']['jdk'] != tools['jdkVersion']:
        problems.append('Build JDK differs from pinned patch version')
    for key in ('compileSdk', 'minSdk', 'targetSdk'):
        if str(data['toolchain'][key]).removeprefix('android-') != str(tools[key]):
            problems.append(f'Wrong {key}')
    return phase('FAIL' if problems else 'PASS', '; '.join(problems) if problems else 'Exact intended versions and SDK checksum verified', ['resolution.json', 'inspection.json'])


def instrument_result(code, output):
    # ADB may exit 0 for instrumentation failures, crashes, and zero tests.
    if code == 0 and re.search(r'OK \([1-9]\d* tests?\)', output) and not re.search(r'FAILURES|INSTRUMENTATION_FAILED|Process crashed|shortMsg=', output):
        return phase('PASS', 'Instrumented assertions passed')
    return phase('FAIL', 'Instrumentation failed, crashed, or did not execute assertions')


def classify_failure(text):
    if re.search(r'UnknownHostException|Could not resolve host|Network is unreachable|Connect timed out|Read timed out|Could not GET|Could not HEAD|SDK location not found|No space left|401 Unauthorized|403 Forbidden', text):
        return 'MISSING_ENVIRONMENT_OR_ARTIFACT_ACCESS'
    if re.search(r'compiled with an incompatible version of Kotlin|requires.*(compile|Android Gradle|API)|Minimum supported Gradle|uses-sdk:minSdkVersion', text, re.I):
        return 'UNSUPPORTED_HOST_COMBINATION'
    return 'UNATTRIBUTED_FAILURE_REQUIRES_CONTROL_COMPARISON'


def render(result):
    lines = [f'# Consumer scenario {result["scenario"]}{" SDK-free control" if result["control"] else ""}', '',
             f'Overall: **{result["overall"]}**. Policy: {result["policy"]}.', '',
             f'SDK: `{result["sdk"] or "excluded"}`', '',
             '| Check | Status | Reason |', '|---|---|---|']
    for name, value in result['phases'].items():
        lines.append(f'| {name} | {value["status"]} | {value["reason"].replace("|", "/").replace(chr(10), " ")} |')
    lines += ['', 'SDK network error / in-flight cancellation: **' + result['sdk_network_error_and_inflight_cancellation']['status'] + '** — ' + result['sdk_network_error_and_inflight_cancellation']['reason'], '', '## Limits', '', result['support'], '',
              'No overall compatibility PASS is possible with a required blocked or unexecuted runtime check.',
              'Static collisions are candidates, not reproduced runtime failures. Normal version selection is not itself an incompatibility.', '',
              '## Evidence', '']
    lines += [f'- [{p}]({p})' for p in result.get('evidence', [])]
    return '\n'.join(lines) + '\n'


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('scenario', choices=MATRIX['scenarios'])
    parser.add_argument('--control', action='store_true')
    parser.add_argument('--sdk-version', type=exact_version, default=MATRIX['sdk']['version'])
    parser.add_argument('--sdk-sha256')
    parser.add_argument('--device', action='store_true', help='Run on exactly one attached device')
    parser.add_argument('--credentials', type=Path, help='Private JSON, fresh sessions for both debug and release; never built into APK')
    parser.add_argument('--out', type=Path)
    parser.add_argument('--offline', action='store_true')
    parser.add_argument('--timeout', type=int, default=900)
    args = parser.parse_args(argv)
    if args.credentials and (not args.device or args.control):
        parser.error('--credentials requires --device and an SDK scenario')
    if args.sdk_sha256 and not re.fullmatch('[a-fA-F0-9]{64}', args.sdk_sha256):
        parser.error('SDK SHA-256 must contain exactly 64 hexadecimal characters')
    scenario = MATRIX['scenarios'][args.scenario]
    host = ROOT / scenario['host']
    out = (args.out or ROOT / 'out' / (args.scenario + ('-control' if args.control else ''))).resolve()
    if out.exists() and any(out.iterdir()):
        parser.error('Output must be empty; use a new directory to avoid stale evidence')
    out.mkdir(parents=True, exist_ok=True)
    secrets = [value for key, value in os.environ.items() if re.search('TOKEN|PASSWORD|SECRET|API_KEY|CLIENT_ID', key)]
    credentials = None
    credential_error = None
    if args.credentials:
        try:
            credentials = json.loads(args.credentials.read_text())
            tokens = []
            for variant in ('debug', 'release'):
                fixture = credentials[variant]
                for name in ('workflowTemplateId', 'remoteWelcomeTitle', 'selectorOpenText', 'selectorVisibleText'):
                    if not fixture.get(name): raise ValueError(f'Missing {variant}.{name}')
                if len(fixture['sessions']) != 2: raise ValueError('Two fresh sessions per variant required')
                for session in fixture['sessions']:
                    for name in ('sdkToken', 'clientId'):
                        if not session.get(name): raise ValueError(f'Missing session {name}')
                        secrets.append(session[name])
                    tokens.append(session['sdkToken'])
                secrets.append(fixture['workflowTemplateId'])
            if len(set(tokens)) != 4: raise ValueError('Four distinct fresh SDK tokens are required')
        except (OSError, ValueError, KeyError, TypeError) as error:
            credentials = None
            credential_error = f'Private credential fixture unavailable or invalid ({type(error).__name__}); provide the documented schema and four fresh sessions'
    sdk = f'{MATRIX["sdk"]["group"]}:{MATRIX["sdk"]["artifact"]}:{args.sdk_version}'
    expected_hash = args.sdk_sha256 or (MATRIX['sdk']['sha256'] if args.sdk_version == MATRIX['sdk']['version'] else None)
    result = {'schema': 1, 'scenario': args.scenario, 'control': args.control, 'policy': scenario['policy'],
              'sdk': None if args.control else sdk, 'sdk_sha256': None,
              'timestamp': datetime.datetime.now(datetime.timezone.utc).isoformat(),
              'harness_sha256': harness_fingerprint(),
              'support': MATRIX['toolchains'][scenario['host']]['support'],
              'requested_toolchain': MATRIX['toolchains'][scenario['host']],
              'expected_dependencies': scenario['expected'],
              'forbidden_dependencies': scenario.get('forbidden', []), 'device': None,
              'phases': {p: phase() for p in PHASES}, 'variants': {}, 'classifications': [], 'commands': []}

    def write(path, text):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(redact(text, secrets))

    def command(argv, name, cwd=host, input_data=None):
        # Credentials are transported on stdin only; never render argv containing secrets.
        env = os.environ.copy()
        for key in list(env):
            if re.search('TOKEN|PASSWORD|SECRET|API_KEY|CLIENT_ID', key): env.pop(key)
        try:
            proc = subprocess.run([str(a) for a in argv], cwd=cwd, env=env, input=input_data,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT, timeout=args.timeout)
            code, output = proc.returncode, proc.stdout.decode('utf-8', errors='replace')
        except (FileNotFoundError, subprocess.TimeoutExpired) as error:
            code, output = 127, f'{type(error).__name__}: command unavailable or exceeded {args.timeout}s\n'
            if isinstance(error, subprocess.TimeoutExpired) and error.stdout:
                output += error.stdout.decode('utf-8', errors='replace')
        write(out / name, output)
        result['commands'].append({'argv': [str(a) for a in argv], 'exit_code': code, 'log': name})
        return code, output

    gradle = [str(host / 'gradlew'), '--no-daemon', '--console=plain', '--stacktrace', f'-Pscenario={args.scenario}',
              f'-Pcontrol={str(args.control).lower()}', f'-PsdkVersion={args.sdk_version}']
    if args.offline: gradle.append('--offline')
    adb = str(Path(os.environ.get('ANDROID_HOME', os.environ.get('ANDROID_SDK_ROOT', '/missing-android-sdk'))) / 'platform-tools/adb')
    java = str(Path(os.environ['JAVA_HOME']) / 'bin/java') if os.environ.get('JAVA_HOME') else 'java'
    code, java_output = command([java, '-version'], 'java.txt')
    correct_java = code == 0 and re.search(r'version "17[.\"]', java_output)
    device_ok = False
    if args.device:
        code, devices = command([adb, 'devices'], 'devices.txt')
        connected = [line.split()[0] for line in devices.splitlines() if line.endswith('\tdevice')]
        if code == 0 and len(connected) == 1:
            # Remove identifying serials from evidence.
            secrets.append(connected[0])
            write(out / 'devices.txt', 'One attached device\n')
            _, api = command([adb, 'shell', 'getprop', 'ro.build.version.sdk'], 'device-api.txt')
            _, abi = command([adb, 'shell', 'getprop', 'ro.product.cpu.abi'], 'device-abi.txt')
            result['device'] = {'api': api.strip(), 'abi': abi.strip()}
            device_ok = api.strip().isdigit() and int(api.strip()) >= MATRIX['toolchains'][scenario['host']]['minSdk']
            _, lock_state = command([adb, 'shell', 'dumpsys', 'window', 'policy'], 'device-lock.txt')
            locked = bool(re.search(r'showing=true|mKeyguardUnlocked=\s*false', lock_state))
            write(out / 'device-lock.txt', f'Keyguard locked: {locked}\n')
            device_ok = device_ok and not locked
            if not device_ok: result['classifications'].append('MISSING_ENVIRONMENT_OR_CREDENTIALS')
    if not correct_java:
        result['phases'] = {p: phase('BLOCKED', 'JAVA_HOME must point to JDK 17 for the pinned consumer tuple', ['java.txt']) for p in PHASES}
    else:
        for variant in ('debug', 'release'):
            print(f'{args.scenario}{"-control" if args.control else ""}: {variant} resolution/build', flush=True)
            folder = out / variant
            folder.mkdir()
            props = [f'-PtestBuildType={variant}', f'-PevidenceDir={folder}']
            vr = {'resolution': phase(), 'scenario_validity': phase(), 'build_packaging': phase(),
                  'host_runtime': phase('BLOCKED', 'An unlocked attached device and successful build are required'),
                  'sdk_runtime': phase('NOT_RUN' if args.control else 'BLOCKED', 'Not applicable: SDK-free control' if args.control else (credential_error or 'Fresh short-lived credentials, synthetic remote workflow, calibrated selector UI and device required'))}
            code, text = command(gradle + props + ['compatEvidence', 'compatGraph'] + [f'compatInsight{i}' for i in range(len(MATRIX['insight']))], f'{variant}/dependencies.txt')
            resolution_path = folder / 'resolution.json'
            if code == 0 and resolution_path.exists():
                data = json.loads(resolution_path.read_text())
                result['actual_toolchain'] = data['toolchain']
                vr['resolution'] = phase('PASS', 'Runtime graph resolved through Maven', [f'{variant}/dependencies.txt'])
                try:
                    inspection = inspect_resolution(data, folder)
                    write(folder / 'inspection.json', json.dumps(inspection, indent=2))
                    result['sdk_sha256'] = inspection['sdk']['sha256'] if inspection['sdk'] else None
                    vr['scenario_validity'] = validate_resolution(data, scenario, args.control, sdk, expected_hash, inspection)
                    if inspection['collision_candidates'] or (inspection['sdk'] and inspection['sdk']['ktor']['original_references']):
                        result['classifications'].append('STATIC_FINDING_REQUIRING_INVESTIGATION')
                except Exception as error:
                    vr['scenario_validity'] = phase('FAIL', f'Artifact inspection incomplete: {type(error).__name__}: {error}')
                write(resolution_path, json.dumps(data, indent=2))
            else:
                classification = classify_failure(text)
                result['classifications'].append(classification)
                status = 'BLOCKED' if classification == 'MISSING_ENVIRONMENT_OR_ARTIFACT_ACCESS' else 'FAIL'
                vr['resolution'] = phase(status, 'Resolution failed; see complete sanitized output', [f'{variant}/dependencies.txt'])
                vr['scenario_validity'] = phase('BLOCKED', 'Cannot verify intended versions without resolved artifacts')
            title = variant.capitalize()
            # Root-qualified: the host variant under test plus the standalone debug driver APK.
            tasks = [f':assemble{title}', ':driver:assembleDebug']
            code, text = command(gradle + props + tasks, f'{variant}/build.txt')
            vr['build_packaging'] = phase('PASS' if code == 0 else ('BLOCKED' if classify_failure(text) == 'MISSING_ENVIRONMENT_OR_ARTIFACT_ACCESS' else 'FAIL'),
                'Application and driver APK built' if code == 0 else 'Build failed; see full output', [f'{variant}/build.txt'])
            if code: result['classifications'].append(classify_failure(text))
            build = host / 'build' / (args.scenario + ('-control' if args.control else ''))
            for pattern in ('**/manifest-merger-*-report.txt', '**/manifest-merger-blame-*-report.txt', '**/merged_manifests/**/AndroidManifest.xml',
                            '**/merged_manifest/**/AndroidManifest.xml', '**/mapping/**/configuration.txt', '**/mapping/**/missing_rules.txt',
                            '**/incremental/merge*JavaResource/merger.xml', '**/incremental/merge*NativeLibs/merger.xml'):
                for file in build.glob(pattern):
                    if file.is_file(): write(folder / 'packaging' / file.relative_to(build), file.read_text(errors='replace'))
            if code == 0 and args.device and device_ok:
                apps = list((build / 'outputs/apk' / variant).glob('*.apk'))
                tests = list((build / 'driver/outputs/apk/debug').glob('*.apk'))
                install_ok = len(apps) == len(tests) == 1
                if install_ok:
                    for label, apk in [('app', apps[0]), ('test', tests[0])]:
                        install_code, _ = command([adb, 'install', '-r', '-t', apk], f'{variant}/install-{label}.txt')
                        install_ok = install_ok and install_code == 0
                if install_ok:
                    base = [adb, 'shell', 'am', 'instrument', '-w', '-r', '-e', 'family', scenario['family'], '-e', 'class']
                    runner = f'{DRIVER}/androidx.test.runner.AndroidJUnitRunner'
                    code, text = command(base + ['com.complycube.compat.tests.HostChecks', runner], f'{variant}/host-runtime.txt')
                    vr['host_runtime'] = instrument_result(code, text)
                    vr['host_runtime']['evidence'] = [f'{variant}/host-runtime.txt']
                    if credentials:
                        # Private file in the test APK sandbox, not app resources or Gradle args.
                        command([adb, 'shell', 'run-as', DRIVER, 'mkdir', '-p', 'files'], f'{variant}/credential-setup.txt')
                        transfer, _ = command([adb, 'shell', 'run-as', DRIVER, 'sh', '-c', '"cat > files/credentials.json"'],
                            f'{variant}/credential-transfer.txt', input_data=json.dumps(credentials[variant]).encode())
                        try:
                            if transfer != 0:
                                vr['sdk_runtime'] = phase('BLOCKED', 'Cannot deliver private runtime credential fixture')
                            else:
                                code, text = command(base + ['com.complycube.compat.tests.SdkChecks', runner], f'{variant}/sdk-runtime.txt')
                                vr['sdk_runtime'] = instrument_result(code, text)
                                vr['sdk_runtime']['evidence'] = [f'{variant}/sdk-runtime.txt']
                        finally:
                            command([adb, 'shell', 'run-as', DRIVER, 'rm', '-f', 'files/credentials.json'], f'{variant}/credential-cleanup.txt')
                            command([adb, 'shell', 'am', 'force-stop', 'com.complycube.compat'], f'{variant}/stop.txt')
                else:
                    vr['host_runtime'] = phase('FAIL', 'APK installation failed or output APK missing')
            result['variants'][variant] = vr
        for name in ('resolution', 'scenario_validity', 'build_packaging'):
            values = [v[name] for v in result['variants'].values()]
            result['phases'][name] = phase(aggregate(values), '; '.join(f'{k}: {v[name]["reason"]}' for k, v in result['variants'].items()))
        result['phases']['host_runtime'] = result['variants']['debug']['host_runtime']
        result['phases']['sdk_runtime'] = result['variants']['debug']['sdk_runtime']
        release_checks = [result['variants']['release']['host_runtime']]
        if not args.control: release_checks.append(result['variants']['release']['sdk_runtime'])
        result['phases']['minified_runtime'] = phase(aggregate(release_checks), 'R8 release: ' + '; '.join(c['reason'] for c in release_checks))
    if result['harness_sha256'] != harness_fingerprint():
        result['phases']['scenario_validity'] = phase('FAIL', 'Harness source/config changed during the run; rerun with stable inputs')
    result['sdk_network_error_and_inflight_cancellation'] = phase('NOT_RUN' if args.control else 'BLOCKED',
        'Not applicable' if args.control else 'No documented deterministic SDK network fault/cancellation hook; remote workflow load and user cancellation cover only part of SDK networking')
    required = [v for k, v in result['phases'].items() if not (args.control and k == 'sdk_runtime')]
    if not args.control: required.append(result['sdk_network_error_and_inflight_cancellation'])
    result['overall'] = aggregate(required)
    if any(v['status'] == 'BLOCKED' for v in required):
        result['classifications'].append('MISSING_ENVIRONMENT_CREDENTIALS_OR_SUPPORTED_HOOK')
    result['classifications'] = sorted(set(result['classifications']))
    result['evidence'] = sorted(str(p.relative_to(out)) for p in out.rglob('*') if p.is_file())
    # Final pass ensures Gradle-written metadata and copied text are sanitized too.
    for file in out.rglob('*'):
        if file.is_file(): write(file, file.read_text(errors='replace'))
    write(out / 'result.json', json.dumps(result, indent=2) + '\n')
    write(out / 'summary.md', render(result))
    print(f'Overall {result["overall"]}; evidence: {out}')
    # Exploratory outcomes are still nonzero. CI job separation controls policy, not suppression.
    return 1 if any(v['status'] == 'FAIL' for v in required) else (2 if result['overall'] in ('BLOCKED', 'NOT_RUN') else 0)


if __name__ == '__main__':
    sys.exit(main())
