import io
import argparse
import json
from pathlib import Path
import struct
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from inspect_artifacts import collisions, inventory, publication, utf8_constants
from gate import gate
from compare import compare
from run import MATRIX, aggregate, exact_version, instrument_result, phase, redact, validate_resolution, classify_failure


def jar(entries):
    target = io.BytesIO()
    with zipfile.ZipFile(target, 'w') as archive:
        for name, data in entries.items(): archive.writestr(name, data)
    return target.getvalue()


def class_bytes(*strings):
    # Enough of a real JVM class-file header/constant pool for the inventory parser.
    return b'\xca\xfe\xba\xbe\0\0\0\x34' + struct.pack('>H', len(strings) + 1) + b''.join(
        b'\x01' + struct.pack('>H', len(s.encode())) + s.encode() for s in strings)


class DiagnosticsTests(unittest.TestCase):
    def test_nested_jar_original_and_relocated_are_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'sdk.aar'
            file.write_bytes(jar({'classes.jar': jar({'sdk/Main.class': class_bytes('Lio/ktor/client/HttpClient;', 'Lvendor/shaded/io/ktor/client/HttpClient;')}),
                'libs/network.jar': jar({'vendor/shaded/io/ktor/client/HttpClient.class': class_bytes('vendor/shaded/io/ktor/client/HttpClient'),
                                        'META-INF/services/vendor.Engine': 'vendor.shaded.Engine'}),
                'jni/arm64-v8a/libshared.so': b'native', 'proguard.txt': '-keep class sdk.Public',
                'AndroidManifest.xml': '<manifest xmlns:android="http://schemas.android.com/apk/res/android"><application><provider android:name="sdk.Provider" android:authorities="${applicationId}.provider"/></application></manifest>'}))
            result = inventory(file, 'vendor:sdk:1.0.0')
        self.assertEqual(result['ktor']['original_classes'], [])
        self.assertEqual(len(result['ktor']['relocated_candidates']), 1)
        self.assertEqual(len(result['ktor']['original_references']), 1)
        self.assertEqual(len(result['ktor']['relocated_reference_candidates']), 2)
        self.assertEqual(result['native'][0]['abi'], 'arm64-v8a')
        self.assertTrue(result['services'])
        self.assertTrue(result['consumer_rules'])
        self.assertEqual(result['providers'][0]['authority'], 'com.complycube.compat.provider')

    def test_host_ktor_not_attributed_to_sdk(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'host.jar'
            file.write_bytes(jar({'io/ktor/client/Client.class': class_bytes('io/ktor/client/Client')}))
            host = inventory(file, 'io.ktor:ktor-client-core-jvm:3.1.3')
            file.write_bytes(jar({'sdk/Main.class': class_bytes('java/lang/Object')}))
            sdk = inventory(file, 'vendor:sdk:1.0.0')
        self.assertEqual(len(host['ktor']['original_classes']), 1)
        self.assertFalse(sdk['ktor']['original_classes'])

    def test_collisions_include_origins_and_abi(self):
        with tempfile.TemporaryDirectory() as directory:
            file = Path(directory) / 'lib.jar'
            file.write_bytes(jar({'same/Class.class': class_bytes('java/lang/Object'), 'META-INF/LICENSE': 'license', 'jni/x86_64/libx.so': b'a'}))
            first, second = inventory(file, 'a:one:1'), inventory(file, 'b:two:1')
        candidates = collisions([first, second])
        self.assertEqual({c['kind'] for c in candidates}, {'classes', 'native', 'resources'})
        self.assertTrue(all(len(c['origins']) == 2 and not c['proven_runtime_failure'] for c in candidates))
        second['native'][0]['abi'] = 'arm64-v8a'
        self.assertFalse(any(c['kind'] == 'native' for c in collisions([first, second])))

    def test_manifest_removal_not_provider_collision(self):
        empty = {k: [] for k in ('classes', 'resources', 'android_resources', 'providers', 'native')}
        first, second = dict(empty), dict(empty)
        first['providers'] = [{'authority': 'same', 'origin': 'a', 'directive': 'remove'}]
        second['providers'] = [{'authority': 'same', 'origin': 'b', 'directive': None}]
        self.assertEqual(collisions([first, second]), [])

    def test_pom_constraints_not_dependencies(self):
        with tempfile.TemporaryDirectory() as directory:
            (Path(directory) / 'sdk.pom').write_text('<project xmlns="http://maven.apache.org/POM/4.0.0"><dependencyManagement><dependencies><dependency><artifactId>constraint</artifactId></dependency></dependencies></dependencyManagement><dependencies><dependency><artifactId>runtime</artifactId></dependency></dependencies></project>')
            result = publication(directory)
        self.assertEqual(result['pom_dependencies'], [{'artifactId': 'runtime'}])
        self.assertEqual(result['pom_constraints'], [{'artifactId': 'constraint'}])

    def test_redaction_preserves_json_and_removes_credentials(self):
        data = {'sdkToken': 'opaque-test-secret', 'clientId': 'synthetic-client',
                'log': 'Bearer secret-value https://person:password@repo.test eyJhbGc.abc.def', 'error': 'Missing class Error'}
        output = redact(json.dumps(data), ['opaque-test-secret', 'synthetic-client'])
        parsed = json.loads(output)
        for secret in ('opaque-test-secret', 'synthetic-client', 'secret-value', 'person:password', 'eyJhbGc.abc.def'):
            self.assertNotIn(secret, output)
        self.assertEqual(parsed['error'], 'Missing class Error')

    def test_aggregate_never_passes_blocked_or_empty(self):
        self.assertEqual(aggregate([phase('PASS'), phase('BLOCKED')]), 'BLOCKED')
        self.assertEqual(aggregate([phase('PASS'), phase('NOT_RUN')]), 'NOT_RUN')
        self.assertEqual(aggregate([phase('FAIL'), phase('BLOCKED')]), 'FAIL')
        self.assertEqual(aggregate([]), 'NOT_RUN')

    def test_instrumentation_zero_exit_is_not_enough(self):
        for output in ('OK (0 tests)', 'INSTRUMENTATION_FAILED', 'Process crashed', '', 'FAILURES!!!\nOK (1 test)'):
            self.assertEqual(instrument_result(0, output)['status'], 'FAIL')
        self.assertEqual(instrument_result(0, 'OK (1 test)')['status'], 'PASS')
        self.assertEqual(instrument_result(1, 'OK (1 test)')['status'], 'FAIL')

    def test_exact_versions_only(self):
        self.assertEqual(exact_version('1.7.2-rc.1'), '1.7.2-rc.1')
        for version in ('+', '1.+', 'latest.release', '[1,2)', '1.7.2-SNAPSHOT', '1.7.2;echo oops'):
            with self.assertRaises(argparse.ArgumentTypeError): exact_version(version)

    def resolution(self):
        scenario = MATRIX['scenarios']['C']
        tools = dict(MATRIX['toolchains'][scenario['host']])
        tools['jdk'] = '17.0.15'
        return scenario, {'toolchain': tools, 'components': ['com.complycube:complycube-sdk:1.7.2', 'io.ktor:ktor-client-core-jvm:3.1.3',
              'androidx.compose.ui:ui-android:1.7.8', 'androidx.compose.material3:material3-android:1.3.2']}

    def test_actual_versions_required(self):
        scenario, data = self.resolution()
        inspect = {'sdk': {'sha256': 'expected'}}
        self.assertEqual(validate_resolution(data, scenario, False, data['components'][0], 'expected', inspect)['status'], 'PASS')
        data['components'].append('io.ktor:ktor-client-logging-jvm:2.3.13')
        self.assertEqual(validate_resolution(data, scenario, False, data['components'][0], 'expected', inspect)['status'], 'FAIL')

    def test_missing_dependency_and_wrong_checksum_fail(self):
        scenario, data = self.resolution()
        result = validate_resolution(data, scenario, False, data['components'][0], 'expected', {'sdk': {'sha256': 'wrong'}})
        self.assertEqual(result['status'], 'FAIL')
        data['components'] = []
        self.assertEqual(validate_resolution(data, scenario, False, 'sdk', None, {'sdk': None})['status'], 'FAIL')

    def test_control_rejects_sdk_leak(self):
        scenario, data = self.resolution()
        self.assertEqual(validate_resolution(data, scenario, True, None, None, {'sdk': None})['status'], 'FAIL')
        data['components'] = [c for c in data['components'] if not c.startswith('com.complycube:')]
        self.assertEqual(validate_resolution(data, scenario, True, None, None, {'sdk': None})['status'], 'PASS')

    def test_sdk_only_scenario_rejects_unshaded_ktor(self):
        scenario = MATRIX['scenarios']['B']
        tools = dict(MATRIX['toolchains'][scenario['host']])
        tools['jdk'] = tools['jdkVersion']
        sdk = 'com.complycube:complycube-sdk:1.7.2'
        components = [sdk, 'androidx.compose.ui:ui-android:1.7.8',
                      'androidx.compose.material3:material3-android:1.3.2']
        data = {'toolchain': tools, 'components': components}
        inspection = {'sdk': {'sha256': MATRIX['sdk']['sha256']}}
        self.assertEqual(validate_resolution(data, scenario, False, sdk, MATRIX['sdk']['sha256'], inspection)['status'], 'PASS')
        data['components'].append('io.ktor:ktor-client-core-jvm:2.3.13')
        result = validate_resolution(data, scenario, False, sdk, MATRIX['sdk']['sha256'], inspection)
        self.assertEqual(result['status'], 'FAIL')
        self.assertIn('Forbidden dependency family', result['reason'])

    def test_ci_gate_preserves_incomplete_overall(self):
        result = {'overall': 'BLOCKED', 'phases': {p: phase('PASS') for p in ('resolution', 'scenario_validity', 'build_packaging')},
                  'variants': {'debug': {'host_runtime': phase('PASS')}, 'release': {'host_runtime': phase('PASS')}}}
        self.assertEqual(gate(result, True), [])
        self.assertEqual(result['overall'], 'BLOCKED')
        result['phases']['scenario_validity'] = phase('FAIL')
        self.assertIn('scenario_validity', gate(result, True))

    def test_controls_do_not_prove_sdk_incompatibility(self):
        sdk = {'scenario': 'C', 'control': False, 'requested_toolchain': {}, 'device': None,
               'phases': {p: phase('FAIL') for p in ('build_packaging', 'host_runtime', 'minified_runtime')}}
        control = dict(sdk, control=True)
        result = compare(sdk, control)
        self.assertFalse(result['reproduced_sdk_host_incompatibility'])
        self.assertTrue(all(f['classification'] == 'HOST_FAILURE_ALSO_PRESENT_WITHOUT_SDK' for f in result['findings']))
        with self.assertRaises(ValueError): compare(sdk, dict(control, scenario='D'))

    def test_failure_classification_does_not_blame_sdk(self):
        self.assertEqual(classify_failure('UnknownHostException'), 'MISSING_ENVIRONMENT_OR_ARTIFACT_ACCESS')
        self.assertEqual(classify_failure('compiled with an incompatible version of Kotlin'), 'UNSUPPORTED_HOST_COMBINATION')
        self.assertEqual(classify_failure('Duplicate class'), 'UNATTRIBUTED_FAILURE_REQUIRES_CONTROL_COMPARISON')


if __name__ == '__main__': unittest.main()
