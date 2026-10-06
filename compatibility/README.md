# Android consumer compatibility harness

These are independent consumer builds, not showcase modules. The root showcase, its repositories, dependencies, wrapper and normal commands are unchanged. Nothing rebuilds or substitutes the SDK producer.

This increment tests **`com.complycube:complycube-sdk:1.7.2` from Maven Central**. `matrix.json` pins toolchains, Android requirements, dependencies, expected resolved versions, forbidden unshaded dependency families, the published SDK SHA-256 and CI device target. Exact release overrides are supported. No dynamic selectors, resolution forces, exclusions, packaging `pickFirst`, metadata suppression or added keep rules are used.

## What is being tested

| Scenario | Independent host | Difference from comparison row | Policy |
|---|---|---|---|
| A | baseline-host | SDK + Activity only | Blocking documented-baseline regression gate |
| B | modern-host | Same SDK + Activity, before targeted dependencies | Exploratory |
| C | modern-host | B + aligned Ktor 3.1.3 client family | Exploratory |
| D | modern-host | B + Compose BOM 2025.10.00 (Compose 1.9.3, Material3 1.4.0) | Exploratory |

Every row accepts `--control`: SDK dependency **and SDK integration/test sources are excluded**. C-control retains the real host Ktor client; D-control retains the host Material3 component. Compare A only with A-control for baseline diagnosis, and B/C/D within the modern toolchain for dependency-family comparisons. Do not attribute A/B differences solely to a dependency: their toolchains and Android requirements differ.

Baseline: Gradle 8.9, AGP 8.7.2, Kotlin 1.9.25, JDK 17.0.15+6, compile/target 34, min 21. This preserves the README's documented minimum, **not a verified minimum SDK consumer tuple**. `docs/compatibility-matrix.md` disagrees on AGP patch level, current showcase defaults differ, and KGP 1.9.25's fully supported AGP/Gradle range does not include this tuple. This discrepancy is recorded, not silently repaired.

Modern: Gradle 8.13, AGP 8.11.1, Kotlin 2.2.21, JDK 17.0.15+6, compile 36, target 35, min 24. The toolchain tuple is within the official AGP/KGP ranges. SDK compatibility is what the tests must establish. See [inspection and sources](docs/inspection.md).

## Prerequisites and exact commands

Use Python 3.9+, Temurin JDK 17.0.15+6, Android command-line tools, accepted SDK licenses, `platforms;android-34`, `platforms;android-36`, `build-tools;34.0.0`, and `build-tools;35.0.0`. Public network access to Google Maven, Maven Central, Gradle distributions and the plugin portal is required on a cold cache. No artifact-access credentials are required for the default public artifact. Authenticated SDK flows additionally require access to ComplyCube's service.

```bash
# macOS: select the pinned JDK 17.0.15+6; Linux: use your JDK 17 installation path.
export JAVA_HOME=$(/usr/libexec/java_home -v 17)
export ANDROID_HOME="$HOME/Library/Android/sdk"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$PATH"

python3 -m unittest discover -s compatibility/tests -v

# Always use a fresh output directory; stale evidence is rejected.
python3 compatibility/tools/run.py A --out compatibility/out/A
python3 compatibility/tools/run.py B --out compatibility/out/B
python3 compatibility/tools/run.py C --out compatibility/out/C
python3 compatibility/tools/run.py D --out compatibility/out/D

# With exactly one unlocked device attached (each invocation owns the test app):
python3 compatibility/tools/run.py C --device --out compatibility/out/C-device
python3 compatibility/tools/run.py C --control --device --out compatibility/out/C-control
python3 compatibility/tools/compare.py compatibility/out/C-device/result.json compatibility/out/C-control/result.json
```

Each run resolves and inspects both debug/release graphs, builds both application variants and an unminified black-box driver APK, and captures complete sanitized command output. Release uses R8, resource shrinking, the Android default optimization rules and **debug test signing**; there is no production signing. The same driver APK is installed against the debug and R8 application APKs. No credentials enter APKs.

The driver (`shared/driver`, package `com.complycube.compat.driver`) is a standalone, self-instrumenting APK that runs in its own process. It starts the host by explicit Intent and observes it only through UI Automator, so it never loads or keeps alive host classes. A conventional in-app `androidTest` APK cannot be used here: AGP leaves out of the test APK every library already on the host's runtime classpath (Kotlin stdlib, and `androidx.test:monitor`, which the SDK declares as a runtime dependency) and expects the host APK to provide them. R8 removes those unused classes from the release host, so the instrumentation crashes before any assertion runs (`ClassNotFoundException` for `AndroidJUnitRunner` with the SDK, `kotlin.jvm.internal.Intrinsics` in the SDK-free control). The separate driver carries its own copies of all test libraries.

`--device` installs/replaces only `com.complycube.compat` and `com.complycube.compat.driver`. Use a dedicated device. The configured CI target is API 35 / x86_64; local reports capture the actual API/ABI and make no claims about other devices. Do not run simultaneous device invocations. Runtime coverage on minSdk 21/24 and other ABIs is **NOT_RUN** until separately executed.

Direct Gradle commands (no connection to root `settings.gradle`):

```bash
cd compatibility/baseline-host
./gradlew -Pscenario=A compatEvidence compatGraph :assembleDebug :driver:assembleDebug
./gradlew -Pscenario=A -PtestBuildType=release :assembleRelease :driver:assembleDebug
cd ../modern-host
./gradlew -Pscenario=C -Pcontrol=true compatEvidence compatInsight0
./gradlew -Pscenario=D assembleDebug
```

The evidence runner defaults to the debug application graph. Set `-PtestBuildType=release` for release resolution and the R8 application; the driver is always the unminified debug `:driver` APK by design. Both hosts have their own settings, wrapper JAR/scripts, and checksum-pinned distribution. They share only a small Gradle fixture and app/test source directories.

## Assertions and honest limits

* Every row clicks a host counter twice and verifies the changed state; D uses a real Compose Material3 button. The host applies system-bar and display-cutout insets: modern-host targets API 35, which enforces edge-to-edge, and a control drawn under the status bar is invisible to accessibility and UI Automator.
* C runs **application-side Ktor 3 Android engine** requests against a driver-owned loopback HTTP server. It deserializes JSON through ContentNegotiation, checks HTTP 400 handling, cancels a delayed request, and verifies the client still works. This code is in the app and is also exercised after R8. The fixture records that the intended endpoints were actually requested. This is not a MockEngine test.
* Authenticated `SdkChecks` uses documented `withWorkflowTemplateId` and `ClientAuth`. It asserts a unique title available only in the remotely loaded workflow, opens and dismisses a calibrated SDK selector, verifies the cancellation callback, returns to the host button, and repeats with a fresh session. C executes the host networking assertions before and after each SDK flow. D performs the same round trip with the host Material3 UI.
* No deterministic SDK network fault injector or cancel-in-flight hook was documented. **SDK networking error-path and in-flight cancellation checks are BLOCKED**, independently of the host HTTP tests and SDK user cancellation. A host test passing never marks SDK networking as passed. Full document upload/verification, camera capture and SDK success completion are not implemented.
* The authenticated UI contract has not been calibrated/executed without a synthetic account, active workflow and credentials. Visible labels are supplied from a reviewed workflow/device fixture; SDK test tags and backend payloads are not fabricated. Missing credentials produce BLOCKED, not skipped tests presented as PASS.

### Trusted synthetic workflow fixture

Configure an active remote workflow with a unique synthetic welcome title, then a document stage whose country or document selector can be opened and dismissed without capturing personal data. Verify the selector's actual accessibility texts on the target device. `Start verification` and `Yes, cancel` are English strings inspected in the published 1.7.2 AAR. Run in English; a different SDK release or customized branding may need a reviewed UI contract update.

On your backend, create synthetic clients and **four fresh, short-lived SDK tokens** scoped to `com.complycube.compat`: two entries for debug and two for release. Account API keys remain on the backend. Do not reuse the existing showcase credentials. Save this private file **outside the repository**, with owner-only permissions; it has this shape (placeholder values are deliberately not runnable credentials):

```json
{
  "debug": {
    "workflowTemplateId": "REPLACE_WITH_SYNTHETIC_TEMPLATE",
    "remoteWelcomeTitle": "UNIQUE_REMOTE_SYNTHETIC_TITLE",
    "selectorOpenText": "REPLACE_WITH_OBSERVED_TRIGGER_TEXT",
    "selectorVisibleText": "REPLACE_WITH_OBSERVED_SELECTOR_CONTENT",
    "sessions": [
      {"clientId": "FRESH_CLIENT_1", "sdkToken": "FRESH_TOKEN_1"},
      {"clientId": "FRESH_CLIENT_2", "sdkToken": "FRESH_TOKEN_2"}
    ]
  },
  "release": {
    "workflowTemplateId": "REPLACE_WITH_SYNTHETIC_TEMPLATE",
    "remoteWelcomeTitle": "UNIQUE_REMOTE_SYNTHETIC_TITLE",
    "selectorOpenText": "REPLACE_WITH_OBSERVED_TRIGGER_TEXT",
    "selectorVisibleText": "REPLACE_WITH_OBSERVED_SELECTOR_CONTENT",
    "sessions": [
      {"clientId": "FRESH_CLIENT_3", "sdkToken": "FRESH_TOKEN_3"},
      {"clientId": "FRESH_CLIENT_4", "sdkToken": "FRESH_TOKEN_4"}
    ]
  }
}
```

```bash
python3 compatibility/tools/run.py C --device --credentials /private/path/credentials.json --out compatibility/out/C-auth
# Generate four NEW tokens before D; never reuse C's fixture.
python3 compatibility/tools/run.py D --device --credentials /private/path/fresh-credentials.json --out compatibility/out/D-auth
```

Credentials are sent on stdin to a private file in the driver APK's sandbox; the test passes runtime Intent extras to the app. They are not Gradle properties, source constants, command arguments or APK assets. The file is deleted and the app stopped afterward. Clear/uninstall `com.complycube.compat` and `com.complycube.compat.driver` when done. No logcat, screenshots, UI dumps, customer content or APKs are uploaded. Known fixture secrets, authorization headers, JWTs and local home paths are redacted from text evidence. Review local evidence before sharing; redaction is not a promise that arbitrary third-party logs are safe.

## Reading the evidence

`result.json` and `summary.md` separate:

1. Dependency resolution from **scenario validity** (all expected selected versions and pinned SDK hash).
2. Debug/release build and packaging.
3. Host runtime, SDK runtime, and minified runtime.

Statuses are `PASS`, `FAIL`, `BLOCKED`, or `NOT_RUN`. Missing/wrong versions invalidate the intended combination, even if assembly succeeds. Normal selection is not automatically an SDK incompatibility. No overall PASS is emitted while any required runtime/fault check is blocked or unexecuted.

Example format, **illustrative, not a claimed result**:

```json
{"scenario":"C","overall":"BLOCKED","phases":{
  "resolution":{"status":"PASS"},"scenario_validity":{"status":"PASS"},
  "build_packaging":{"status":"PASS"},"host_runtime":{"status":"PASS"},
  "sdk_runtime":{"status":"BLOCKED"},"minified_runtime":{"status":"BLOCKED"}
}}
```

Each variant retains:

* `resolution.json`: direct requests, every requested→selected edge, resolved component/artifact coordinates, actual Gradle/AGP/Kotlin/JDK/Android tuple.
* `sdk.pom` / `sdk.module`: actual Maven publication metadata, separate from the graph.
* `dependencies.txt`: full graph and individually named dependencyInsight task sections for all targeted families.
* `inspection.json`: artifact SHA-256s, SDK-only original/possible relocated Ktor classes and constant-pool references, every embedded JAR, class/package inventory, service descriptors, consumer R8 rules, manifest/provider declarations, native library name/hash/ABI, and originating artifacts for collision candidates.
* `build.txt`, packaging merger/blame reports, merged manifests, native/Java resource merger diagnostics when AGP emits them, and R8 configuration/missing-rule files when available.
* Runtime test output and actual device API/ABI, when executed.

The inventory distinguishes the SDK's own bytes from legitimate host Ktor 3 classes. Original and relocated names are checked separately. Name-based scans cannot prove isolation after arbitrary obfuscation; candidate collisions (especially Android overlays, license files and merged service descriptors) require build/runtime evidence. Producer-supplied manifest merge directives and consumer keep rules are **recorded as shipped**, not copied into host fixes.

Exit codes: 0 all required checks PASS; 1 at least one FAIL; 2 incomplete/BLOCKED. `gate.py result.json --runtime` explicitly checks the narrower credential-free CI contract (valid resolution, both builds, host tests in both variants). Its success is never an overall compatibility claim. Exploratory failures are retained as failing jobs, separate from baseline policy. `compare.py` labels failures also present in matching controls and requires investigation of differing failures; it never auto-declares a reproduced SDK incompatibility.

## Testing a release / adding a scenario

```bash
python3 compatibility/tools/run.py C --sdk-version 1.7.3 --sdk-sha256 REPLACE_WITH_64_HEX_PUBLIC_AAR_HASH --out compatibility/out/C-1.7.3
# Or omit --sdk-sha256 for a first observation: the resolved hash is still recorded.
# SDK version must be exact and published; a missing/private artifact is a blocker.
```

Repeat all relevant rows and controls for a new release. Reinspect metadata and embedded packages before updating expected selections. The default 1.7.2 checksum is enforced only for 1.7.2; an override is always recorded. Gradle direct builds also accept `-PsdkVersion=1.7.3`.

To add a dependency scenario: add a matrix row on an existing host with `compareTo`, one family, explicit versions and expected selected modules; add only the dependencies and small source/test fixture needed by that family. Add a matching control run. Align related modules with a regular published BOM or explicit family versions; never force away a finding. If the family requires another toolchain, create another independent build/wrapper and establish its SDK-only comparison first.

Prioritized backlog, based on actual 1.7.2 publication/artifact evidence (all **NOT_IMPLEMENTED / NOT_RUN**):

1. **Coroutines and serialization**: public SDK dependencies and direct networking/model references; test cancellation/JSON and host operation after SDK closure, with aligned core/Android/Guava and serialization modules. Do not label Ktor's incidental transitive updates as this separate scenario.
2. **CameraX and Sentry**: published CameraX 1.4.0 and Sentry 8.20.0; the SDK manifest removes Sentry auto-init providers. Test both initialization orders and camera/host telemetry after SDK closure; use a device with a camera and a synthetic Sentry transport/account. Do not assume process-global state is isolated by shading.
3. **Places and Media3**: published Places 3.5.0 and Media3 1.4.1. Separately test autocomplete and deterministic local playback, host→SDK and SDK→host. Places needs an authorized test key/service; keep it outside the public app.
4. **ML Kit, MediaPipe and native coexistence**: published ML Kit and MediaPipe, embedded RenderScript toolkit for four ABIs. Test actual load/inference with synthetic fixtures, ABI-specific collision/load order and 16 KB page-size devices. Packaging success alone does not prove JNI coexistence. Producer's minSdk override requires explicit below-24 runtime evidence, not a host override.

Static finding recorded for SDK follow-up (not a harness scenario): the SDK publishes `androidx.test:monitor` at runtime scope. See [inspection](docs/inspection.md) for the consumer instrumentation-test impact on R8 builds.

No React Native, Flutter or iOS coverage is included.

## Public CI

`.github/workflows/consumer-compatibility.yml` is separate from the existing showcase workflow. Relevant PRs run Python diagnostics and A/A-control debug + R8 builds and credential-free device assertions. Manual runs add B/C/D with controls. All permissions are read-only; official actions are commit-pinned (SHAs resolved from upstream v4 tags; see sources). There is no `pull_request_target` and no PR job receives secrets.

For trusted tests, configure the `compatibility-trusted` environment with required reviewers and default-branch deployment restrictions. Store a freshly generated synthetic fixture as `COMPAT_CREDENTIAL_FIXTURE`, then dispatch from the default branch with `trusted_credentials=true` and `trusted_scenario=C` or `D`. Tokens can expire during builds; such failures require a new fixture, never an embedded account key. That job uploads only sanitized JSON/Markdown summaries, never APKs or credentialed raw evidence. Broader SDK error/cancel-in-flight coverage remains BLOCKED even after the implemented round trip passes.
