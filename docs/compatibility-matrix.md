# Compatibility Matrix

This page documents the **minimum** and **recommended** development tools
required to **build** and **run** the ComplyCube Android sample app.  It
consolidates version requirements from the sample project’s configuration and
official Android documentation.  Where the project pins a specific version
(for example, Gradle Wrapper or the Kotlin plugin), that version is used as
the recommended baseline.

## Key concepts

- **Build JDK** – the Java runtime used to **execute Gradle and the Android
  Gradle Plugin (AGP)**.  Even though the sample project compiles
  Kotlin/Java code targeting bytecode level 11, AGP 8.x **requires Java 17 to run**
  and will fail on older JDKs:contentReference[oaicite:0]{index=0}.
- **AGP** – the Android Gradle Plugin, which extends Gradle to build
  Android apps.  AGP versions dictate compatible Gradle, build-tools and JDK
  versions.  The project currently uses AGP 8.7.2.  According to the AGP 8.7
  release notes, AGP 8.7’s compatibility table lists **Gradle 8.9**,
  **SDK Build Tools 34.0.0**, **JDK 17** and default **NDK 27.0.12077973**:contentReference[oaicite:1]{index=1}.
- **Kotlin & Compose** – Jetpack Compose relies on a compiler extension that
  must align with the Kotlin version.  The Compose to Kotlin compatibility
  map lists that Compose compiler version **1.5.15** is compatible with
  **Kotlin 1.9.25**:contentReference[oaicite:2]{index=2}.  The sample project pins
  exactly these versions.
- **Android Studio** – the official IDE bundles the correct JDK and wraps
  Gradle/AGP.  Google has introduced a time-based compatibility policy:
  each Studio version supports **AGP versions released within the previous
  three years**, and Studio will ask you to upgrade AGP if it falls outside
  that window:contentReference[oaicite:3]{index=3}.  A table in the Studio release notes
  shows that **Android Studio 2024.2.1 (codename *Ladybug*) supports AGP
  versions 3.2 – 8.7**, while **2024.3.x (Meerkat) supports up to AGP 8.9**:contentReference[oaicite:4]{index=4}.
- **Android SDK** – compileSdk and build-tools versions must be installed in
  your Android SDK.  AGP 8.7 supports up to API 35:contentReference[oaicite:5]{index=5}, but
  the sample project uses **compileSdk 34** and therefore requires the
  **Android 14 (API 34) platform** and **Build Tools 34.0.0**:contentReference[oaicite:6]{index=6}.

## Minimum vs. recommended

The table below lists **Minimum** and **Recommended** versions.  “Minimum”
means the oldest environment we have validated against our project.  Clients
running older versions risk build errors or missing features.  “Recommended”
means the version currently used inside the ComplyCube sample project.  Keeping
your environment at the recommended level avoids most compatibility issues.

| Component | Minimum | Recommended | Notes |
| --- | --- | --- | --- |
| **Build JDK (runs Gradle/AGP)** | **17** | **17 (bundled with Android Studio 2024.2.1)** | AGP 8.7 requires JDK 17 to run; older JDKs (e.g., 11) will cause build failures:contentReference[oaicite:7]{index=7}. |
| **Bytecode target (Kotlin jvmTarget)** | **11** | **11** | The sample project compiles Kotlin/Java sources targeting Java 11 bytecode.  This does not affect the build JDK requirement. |
| **Gradle wrapper** | **8.9** | **8.9** | AGP 8.7’s compatibility table lists Gradle 8.9 as both the minimum and default version:contentReference[oaicite:8]{index=8}.  Use the project’s `./gradlew` to ensure the correct Gradle version. |
| **Android Gradle Plugin (AGP)** | **8.7.0** | **8.7.2** | The sample uses AGP 8.7.2.  All AGP 8.7.x versions require the same JDK and Gradle. |
| **Kotlin plugin** | **1.9.25** | **1.9.25** | Compose compiler 1.5.15 requires Kotlin 1.9.25:contentReference[oaicite:9]{index=9}.  Downgrading Kotlin will cause mismatched Compose binaries. |
| **Compose compiler extension** | **1.5.15** | **1.5.15** | From the Compose–Kotlin compatibility map, 1.5.15 is aligned with Kotlin 1.9.25:contentReference[oaicite:10]{index=10}. |
| **Android Studio** | **2024.2.1 (Ladybug)** | **2024.2.1 Patch 2 (latest stable in this line)** | Studio 2024.2.1 supports AGP up to 8.7:contentReference[oaicite:11]{index=11}.  The policy states each Studio release supports AGP versions from the previous three years:contentReference[oaicite:12]{index=12}. |
| **Android SDK – compileSdk / targetSdk** | **34** | **34** | AGP 8.7 supports up to API 35:contentReference[oaicite:13]{index=13}, but the sample compiles against API 34.  Ensure `platforms/android-34` is installed. |
| **Android Build Tools** | **34.0.0** | **34.0.0** | AGP 8.7’s compatibility table lists Build Tools 34.0.0 as minimum and default:contentReference[oaicite:14]{index=14}.  Install via SDK Manager if not present. |
| **Min SDK (runtime)** | **21** | **21** | The sample’s `minSdk` is 21.  Users running older devices will not be able to install the app. |
| **NDK** | **27.0.12077973** | **29.0.13113456** | AGP 8.7 defaults to NDK 27.0.12077973:contentReference[oaicite:15]{index=15}.  The sample pins NDK 29.0.13113456; either version works, but install at least one of them via SDK Manager. |
| **CMake** | **3.22.1** | **3.22.1** | The sample uses external native build with CMake 3.22.1.  Install the same version from the SDK Manager to avoid C++ toolchain errors. |

## How to use this matrix

1. **Verify your environment**: run the `scripts/doctor` tool included in this
   repository.  It checks your installed JDK, Gradle and Android SDK against
   the recommended versions and provides specific fix instructions when it
   detects mismatches.
2. **Meet at least the minimum versions**: if your toolchain is older than
   the “Minimum” column, upgrade your JDK/Gradle/AGP/Kotlin/Android Studio
   accordingly.  Building the sample on older versions is not supported and may
   lead to unpredictable build failures.
3. **Prefer the recommended versions**: the “Recommended” column reflects the
   versions used internally by the ComplyCube team.  Staying aligned with
   these versions reduces the chance of encountering bugs or missing features.
4. **Understand the compatibility policy**: Google’s time-based policy means
   future Android Studio releases will drop support for AGP versions older than
   three years:contentReference[oaicite:16]{index=16}.  Keeping your AGP and Studio up-to-date
   ensures continued IDE support.

## References

- **AGP 8.7 compatibility table** – lists Gradle 8.9, SDK Build Tools 34.0.0,
  NDK 27.0.12077973 and JDK 17:contentReference[oaicite:17]{index=17}.
- **Java versions in Android builds** – explains why AGP 8.x requires JDK 17
  regardless of your `jvmTarget`:contentReference[oaicite:18]{index=18}.
- **Compose–Kotlin compatibility map** – shows Compose compiler 1.5.15 works
  with Kotlin 1.9.25:contentReference[oaicite:19]{index=19}.
- **Android Studio/AGP compatibility policy and table** – states that Studio
  releases support AGP versions from the previous three years and lists which
  Studio versions support AGP 8.7:contentReference[oaicite:20]{index=20}.




