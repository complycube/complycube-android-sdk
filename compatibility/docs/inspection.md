# Inspection record and version decisions

Inspection date: 2026-09-17. These observations refer to the **public Maven Central** artifact `com.complycube:complycube-sdk:1.7.2`, downloaded directly after updating this branch from `origin/main`. No private SDK or producer source was substituted. Machine-readable public publication/artifact observations are in [published-1.7.2.json](published-1.7.2.json). Scenario output contains the resolved consumer graph, which is different from a list of declared dependencies.

## Repository facts

* Root settings/defaults: Gradle 8.9, AGP 8.5.2, Kotlin 2.1.0, compile/target 34, min 24. SDK version defaults to 1.7.2, with Maven Central and Google repositories; the showcase also allows Maven local and JFrog build tooling.
* README's minimum table: Gradle 8.9 / AGP 8.7.2 / Kotlin 1.9.25 / JDK 17 / compile 34. The separate compatibility document says AGP minimum 8.7.0 and minSdk 21. It describes sample build support, not a complete SDK consumer guarantee. A uses the README toolchain with documented runtime minSdk 21, marks support unverified and keeps failures visible.
* Existing tag-triggered workflow mutates the showcase wrapper and supplies toolchain properties across a large matrix. It is preserved. The new workflow neither edits the root wrapper nor copies its version matrix.
* Integration entry is `ComplyCubeSdk.Builder` with a ComponentActivity or Fragment, stages or a workflow, `ClientAuth`, and Result callbacks. The sample demonstrates Document/Welcome/Complete stages. Credentials currently present in the sample are not copied, used, emitted into new reports or changed by this task.
* Showcase-only direct requests include AppCompat, ConstraintLayout, Navigation fragment/UI, Material Views, JUnit/Espresso, and JFrog plugins. Some names may also be transitive SDK dependencies; provenance must be read from the resolved graph rather than inferred from a catalog. No version catalog is present in this public repository. Producer catalog entries, if supplied later, are not artifact evidence.

## Published metadata versus embedded bytes

The public POM and Gradle module metadata do **not** declare Ktor transitively. They declare coroutines-slf4j 1.9.0 alongside serialization JSON 1.6.3, coroutines-guava 1.9.0, Compose 1.7.8, Material3 1.3.2, CameraX 1.4.0, Sentry 8.20.0, Places 3.5.0, Media3 1.4.1, ML Kit Play Services text/face modules, and MediaPipe tasks-vision 1.0.0. The full direct lists and constraints are retained in JSON. Deeper dependencies and actual selected versions come from Gradle, not from these requested versions.

The AAR contains `classes.jar`, `libs/classes.jar`, and `libs/ktor-shaded-2.3.13.jar`. The second JAR embeds FingerprintJS classes; the third contains the relocated Ktor implementation. The AAR contains `librenderscript-toolkit.so` for arm64-v8a, armeabi-v7a, x86 and x86_64. Native transitive dependencies are inventoried separately for each resolved consumer graph.

No original `io.ktor` class definitions or constant-pool references were found in the AAR's JARs. The embedded Ktor JAR contains 1,549 relocated class definitions under `com.complycube.shaded.ktor`; SDK networking references point to that relocated namespace. This is direct static evidence of relocation in the published 1.7.2 artifact. It does not by itself prove runtime compatibility with host Ktor 3, which is why scenario C still runs both host and SDK behavior under debug and R8.

The embedded Ktor JAR ships relocated service descriptors for `com.complycube.shaded.ktor.client.HttpClientEngineContainer` and `com.complycube.shaded.ktor.serialization.kotlinx.KotlinxSerializationExtensionProvider`, plus targeted relocated Ktor consumer rules. The harness inventories these separately from the host's legitimate `io.ktor` services and scans original/relocated constant-pool references. Fully obfuscated or unusually renamed packages require additional producer evidence; substring absence alone cannot prove isolation.

The POM and module metadata also declare **`androidx.test:monitor:1.7.2` at runtime scope**. This is test-instrumentation infrastructure, so every consumer app ships it on its runtime classpath. Consequences observed with this harness: AGP leaves `androidx.test:monitor` out of any consumer's in-app `androidTest` APK because the app already provides it, while R8 removes those unreferenced classes from the consumer's minified build. A consumer running conventional instrumentation tests against an R8 build of an app that includes the SDK therefore gets `ClassNotFoundException: androidx.test.runner.AndroidJUnitRunner` before any test runs (reproduced on API 36, scenario A, 6 October 2026). The SDK-free control fails the same way for Kotlin stdlib, so the general mechanism is an AGP/R8 limitation rather than an SDK defect; the SDK adds `androidx.test` to the set of affected libraries. Recorded for SDK follow-up (move to a test-only scope); no consumer keep rule or exclusion is applied. The harness avoids the issue with a standalone driver APK.

The shipped SDK manifest declares minSdk 21, includes producer-authored `tools:overrideLibrary` for MediaPipe, removes Sentry initialization/performance providers, and adds `${applicationId}.sdkinitializer`. The hosts add no overrideLibrary or Sentry overrides. Below-24 MediaPipe behavior and Sentry shared initialization therefore need real runtime checks. Consumer R8 rules are substantial and applied as published; the harness records them rather than adding broad rules to make a build pass.

## Official toolchain sources

Read on 2026-09-17:

* [AGP 8.7 compatibility](https://developer.android.com/build/releases/agp-8-7-0-release-notes): Gradle 8.9, JDK 17, Build Tools 34.0.0, maximum API 35. Supports the Android portion of A's tuple.
* [Kotlin Gradle plugin compatibility](https://kotlinlang.org/docs/gradle-configure-project.html): KGP 1.9.20–1.9.25 is fully supported only through Gradle 8.1.1 / AGP 8.1.0. Therefore A's full tuple is outside this range. KGP 2.2.20–2.2.21 supports Gradle 7.6.3–8.14 and AGP 7.3.1–8.11.1.
* [AGP 8.11 compatibility](https://developer.android.com/build/releases/agp-8-11-0-release-notes): Gradle 8.13, JDK 17, Build Tools 35.0.0, maximum API 36. This and the KGP table support the modern toolchain tuple.
* [Compose BOM mapping](https://developer.android.com/develop/ui/compose/bom/bom-mapping) and the [2025.10.00 BOM POM](https://dl.google.com/dl/android/maven2/androidx/compose/compose-bom/2025.10.00/compose-bom-2025.10.00.pom): Compose UI/Foundation/Runtime/Material 1.9.3, Material3 1.4.0. The Compose compiler plugin uses the pinned consumer Kotlin version. No producer Kotlin upgrade is involved.
* [Android SDK requirements](https://docs.complycube.com/documentation/sdks/mobile-integrations/android-sdk): Android API 21+, AndroidX, Kotlin 1.7+. It does **not** specify an exact minimum AGP/Gradle consumer tuple. The producer's Kotlin version cannot fill that gap.
* [Workflow integration](https://docs.complycube.com/documentation/sdks/mobile-integrations/android-sdk/workflow-integration): documented `withWorkflowTemplateId`, backend-created short-lived SDK tokens scoped to the app ID, Result callbacks, and remote workflow sessions. The actual public 1.7.2 Builder signatures were inspected with `javap` to confirm these methods and `Result.Canceled` spelling; the guide's Kotlin callback example has inconsistent `Cancelled` spelling.
* [Legacy stage and event documentation](https://docs.complycube.com/documentation/sdks/legacy-integration/android-sdk): documents Document selection/country selection and events. It provides no deterministic SDK networking test engine or fault injection API.

No unsupported combinations are repaired by changing versions. All scenarios declare expected selected family versions; a mismatch invalidates that intended scenario without asserting that Gradle's ordinary selection is itself a compatibility bug.

## CI action pins

Official upstream v4 tag SHAs were resolved during implementation. Only checkout, JDK setup and text-artifact upload actions are used, with no PR write privileges or third-party emulator action:

* [actions/checkout at 11d5960](https://github.com/actions/checkout/tree/11d5960a326750d5838078e36cf38b85af677262)
* [actions/setup-java at cf277c6](https://github.com/actions/setup-java/tree/cf277c60eb25467037889841efdb72551f06f6c3)
* [actions/upload-artifact at ea165f8](https://github.com/actions/upload-artifact/tree/ea165f8d65b6e75b540449e92b4886f43607fa02)

Review these fixed revisions when updating them. Public jobs have no credential fixture; trusted execution requires a default-branch manual dispatch and a protected environment. Test binaries and raw credentialed output are not uploaded.
