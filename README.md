
# ComplyCube Example App

This repository provides a pre-built UI that uses the ComplyCube SDK. It guides you through the ComplyCube identity verification process, which includes collecting client ID documents, proof of address documents, and biometric selfies.

> :information_source: Please get in touch with your **Account Manager** or **[support](https://support.complycube.com/hc/en-gb/requests/new)** to get access to our NFC-enabled Mobile SDK.

## Before you start (quick checklist)

Most “can’t run the project” issues come from environment mismatch. Please check these first:

### 1) Android Studio version

Use **Android Studio Ladybug (2024.2.1) or newer** for best compatibility with this repo’s AGP. ([Android Developers](https://developer.android.com/build/releases/gradle-plugin "Android Gradle plugin 8.13 release notes  |  Android Studio  |  Android Developers"))

### 2) JDK (must be 17)

This project uses **Android Gradle Plugin 8.7.x**, which requires **JDK 17**. ([Android Developers](https://developer.android.com/build/releases/past-releases/agp-8-7-0-release-notes "Android Gradle Plugin 8.7.0 (October 2024)  |  Android Developers"))

✅ Confirm:

-   `java -version` shows **17.x**
- Android Studio: **Settings → Build, Execution, Deployment → Build Tools → Gradle → Gradle JDK = 17**

> Note: Your module may compile Java/Kotlin to target 11 (`jvmTarget = "11"`), but the **build toolchain** still needs **JDK 17**. ([Android Developers](https://developer.android.com/build/releases/past-releases/agp-8-7-0-release-notes "Android Gradle Plugin 8.7.0 (October 2024)  |  Android Developers"))

### 3) Gradle / AGP versions

This repo is set up for:

-   **Gradle wrapper:** 8.9 ([Android Developers](https://developer.android.com/build/releases/past-releases/agp-8-7-0-release-notes "Android Gradle Plugin 8.7.0 (October 2024)  |  Android Developers"))
-   **AGP:** 8.7.2
-   **Kotlin plugin:** 1.9.25
-   **Compose compiler extension:** 1.5.15 (pairs with Kotlin 1.9.25) ([Android Developers](https://developer.android.com/jetpack/androidx/releases/compose-kotlin "Compose to Kotlin Compatibility Map  |  Jetpack  |  Android Developers"))


### 4) Android SDK components (via SDK Manager)

Install:

-   **Android SDK Platform 34**
-   **Build Tools 34.0.0** ([Android Developers](https://developer.android.com/build/releases/past-releases/agp-8-7-0-release-notes "Android Gradle Plugin 8.7.0 (October 2024)  |  Android Developers"))
-   **NDK 29.0.13113456** (project pins an NDK version)
-   **CMake 3.22.1** (project references this version)


Android Studio → **SDK Manager**:

- SDK Platforms → Android 14 (API 34)
- SDK Tools → Android SDK Build-Tools 34.0.0, NDK, CMake

## Run the Doctor script (recommended)

Before opening the project, run the doctor script to validate your environment.

### macOS / Linux

```bash  
chmod +x scripts/doctor.sh ./scripts/doctor.sh  
```  

### Windows (PowerShell)

```powershell  
powershell -ExecutionPolicy Bypass -File .\scripts\doctor.ps1  
```  

### What the output means

- ✅ **PASS**: This requirement is satisfied.
- ⚠️ **WARN**: Not guaranteed to break the build, but may cause issues (recommended to fix).
- ❌ **FAIL**: This will block Gradle sync/build. Fix it before continuing.


### How to fix FAIL/WARN items

Each FAIL/WARN line includes a **Fix** line (↳ Fix: …) explaining exactly what to change in Android Studio or what to install.



## To run the app

1. Synchronize your Gradle project to install the required dependencies.
2. [Create a Client ID](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide#id-2.-create-a-client).
3. [Generate an SDK token](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide#id-3.-generate-an-sdk-token).
4. In the `FirstFragment.kt` file, replace `CLIENT_ID` and `SDK_TOKEN` with the generated values from the previous steps.
5. Run the app.

> :information_source: If you're using an updated SDK version and run into any issues, please clear your `%USERPROFILE%\.gradle\caches` or `~/.gradle/caches` folder

## Troubleshooting (most common fixes)

### “AGP requires Java 17” / Gradle sync fails

- Set **Gradle JDK = 17** in Android Studio
- Ensure `JAVA_HOME` points to JDK 17 (especially on CI)


AGP 8.7 requires JDK 17. ([Android Developers](https://developer.android.com/build/releases/past-releases/agp-8-7-0-release-notes "Android Gradle Plugin 8.7.0 (October 2024)  |  Android Developers"))

### “Unsupported Gradle version” / wrapper mismatch

Use the wrapper included in the repo:

```bash  
./gradlew --version
```  

AGP 8.7 expects Gradle 8.9. ([Android Developers](https://developer.android.com/build/releases/past-releases/agp-8-7-0-release-notes "Android Gradle Plugin 8.7.0 (October 2024)  |  Android Developers"))

### Compose compiler / Kotlin mismatch errors

This repo expects:

- Kotlin **1.9.25**
- Compose compiler extension **1.5.15**

These versions are compatible together. ([Android Developers](https://developer.android.com/jetpack/androidx/releases/compose-kotlin "Compose to Kotlin Compatibility Map  |  Jetpack  |  Android Developers"))

### “NDK/CMake not found” / native build errors

Install the pinned versions from **SDK Manager**:

- NDK **29.0.13113456**
- CMake **3.22.1**

Then re-sync Gradle.

### Dependency resolution / weird build cache issues

Try:

```bash  
./gradlew --stop./gradlew clean
```  

If it still fails:

- Delete `~/.gradle/caches` (macOS/Linux) or `%USERPROFILE%\.gradle\caches` (Windows)
- Re-sync

## Getting help faster (what to send us)

If you still can’t run the sample, please include:
- Android Studio version
-   `java -version`
-   `./gradlew --version`
- The **full Gradle sync/build error log** (not screenshots)


## Integrating our SDK

For detailed instructions on integrating our SDK, please refer to our [integration guide](https://docs.complycube.com/documentation/guides/mobile-sdk-guide/mobile-sdk-integration-guide).

For an overview of our core platform and its multiple features, please refer to our [user guide](https://docs.complycube.com) or browse the [API reference](https://docs.complycube.com/api-reference) for fine-grained documentation of all our services.

## Compatibility (Minimum / Recommended)

> Build **JDK** is the Java version used to run Gradle/AGP.  
> **jvmTarget** is the bytecode target we compile to (we target Java 11).

| Item | Minimum | Recommended |
|---|---:|---:|
| Build JDK (Gradle/AGP runtime) | 17 | 17 (Android Studio embedded JDK) |
| Gradle Wrapper | 8.9 | 8.9 |
| Android Gradle Plugin (AGP) | 8.7.2 | 8.7.2 |
| Kotlin | 1.9.25 | 1.9.25 |
| Compose Compiler Extension | 1.5.15 | 1.5.15 |
| Android Studio | Ladybug 2024.2.1 | Ladybug 2024.2.1 Patch 2 |
| Android SDK Platform (compileSdk) | 34 | 34 |
| Android Build Tools | 34.0.0 | 34.0.0 |
| NDK | 29.0.13113456 | 29.0.13113456 |
| CMake | 3.22.1 | 3.22.1 |

For the full compatibility matrix and troubleshooting guidance, see:
➡️ **[Compatibility Matrix](docs/compatibility-matrix.md)**

## About ComplyCube

[ComplyCube](https://www.complycube.com/en) is a leading SaaS & API platform recognized for its AI-powered solutions in Identity Verification (IDV), Anti-Money Laundering (AML), and Know Your Customer (KYC) compliance. Serving a diverse range of sectors, including financial services, transport, healthcare, e-commerce, cryptocurrency, FinTech, telecoms, and more, ComplyCube has established itself as a major player in the IDV market globally.

The platform is ISO-certified and acclaimed for its rapid omnichannel integration capabilities and the comprehensive scope of its services. It offers a variety of Low/No-Code solutions, powerful API, Mobile SDKs, Client Libraries, and seamless CRM integrations.