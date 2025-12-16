# ----------------------------
# ComplyCube Sample App Doctor
# Windows PowerShell
# ----------------------------

$REQUIRED_JAVA_MAJOR = 17
$REQUIRED_GRADLE_WRAPPER = "8.9"
$REQUIRED_KOTLIN = "1.9.25"
$REQUIRED_COMPOSE_COMPILER = "1.5.15"
$REQUIRED_COMPILE_SDK = "34"
$REQUIRED_BUILD_TOOLS = "34.0.0"
$REQUIRED_NDK = "29.0.13113456"
$REQUIRED_CMAKE = "3.22.1"

$pass = 0
$warn = 0
$fail = 0

function Pass($msg) { $script:pass++; Write-Host "✅ PASS: $msg" }
function Warn($msg) { $script:warn++; Write-Host "⚠️  WARN: $msg" }
function Fail($msg) { $script:fail++; Write-Host "❌ FAIL: $msg" }
function Fix($msg)  { Write-Host "   ↳ Fix: $msg" }

function RepoRoot {
  try {
    $git = Get-Command git -ErrorAction Stop
    $root = git rev-parse --show-toplevel 2>$null
    if ($LASTEXITCODE -eq 0 -and $root) { return $root.Trim() }
  } catch {}
  return (Get-Location).Path
}

function Get-GradleWrapperVersion($root) {
  $wrapper = Join-Path $root "gradle\wrapper\gradle-wrapper.properties"
  if (-not (Test-Path $wrapper)) { return $null }
  $line = Select-String -Path $wrapper -Pattern "^distributionUrl=" -ErrorAction SilentlyContinue | Select-Object -First 1
  if (-not $line) { return $null }
  $url = $line.Line.Split("=",2)[1]
  if ($url -match "gradle-([0-9]+\.[0-9]+)") { return $Matches[1] }
  return $null
}

function Find-In-Repo($root, $pattern) {
  $files = Get-ChildItem -Path $root -Recurse -Include *.gradle, *.gradle.kts -ErrorAction SilentlyContinue
  foreach ($f in $files) {
    $hit = Select-String -Path $f.FullName -Pattern $pattern -ErrorAction SilentlyContinue
    if ($hit) { return $true }
  }
  return $false
}

Write-Host ""
Write-Host "ComplyCube Sample App Doctor (Windows)"
Write-Host "----------------------------------------"

$root = RepoRoot
Write-Host "Repo root: $root"
Write-Host "OS: Windows | Arch: $env:PROCESSOR_ARCHITECTURE"

Write-Host ""
Write-Host "Java (Build JDK)"
Write-Host "----------------------------------------"
try {
  $javaLine = & java -version 2>&1 | Select-Object -First 1
  if (-not $javaLine) { throw "no output" }

  # Extract quoted version
  if ($javaLine -match 'version "([^"]+)"') {
    $token = $Matches[1]
    $major = $null

    if ($token.StartsWith("1.")) {
      $major = [int]($token.Split(".")[1])
    } else {
      $major = [int]($token.Split(".")[0])
    }

    if ($major -lt $REQUIRED_JAVA_MAJOR) {
      Fail "Java major version is $major, but build requires JDK $REQUIRED_JAVA_MAJOR+"
      Fix "Install JDK $REQUIRED_JAVA_MAJOR and set Android Studio Gradle JDK to it (Settings → Build Tools → Gradle → Gradle JDK)."
    } else {
      Pass "Java major version is $major"
    }
  } else {
    Warn "Could not parse java version string: $javaLine"
    Fix "Ensure JDK $REQUIRED_JAVA_MAJOR is installed and on PATH."
  }
} catch {
  Fail "Java not found on PATH"
  Fix "Install JDK $REQUIRED_JAVA_MAJOR and set Android Studio Gradle JDK to it."
}

Write-Host ""
Write-Host "Gradle Wrapper"
Write-Host "----------------------------------------"
$wrapperVer = Get-GradleWrapperVersion $root
if (-not $wrapperVer) {
  Fail "Gradle wrapper not found or unreadable (gradle\wrapper\gradle-wrapper.properties)"
  Fix "Re-clone the repository and ensure wrapper files are present."
} else {
  if ($wrapperVer -ne $REQUIRED_GRADLE_WRAPPER) {
    Warn "Gradle wrapper is $wrapperVer (expected $REQUIRED_GRADLE_WRAPPER)"
    Fix "Use the repo wrapper anyway: .\gradlew <task>. Update REQUIRED_GRADLE_WRAPPER if the project was upgraded."
  } else {
    Pass "Gradle wrapper version is $wrapperVer"
  }
}

$gradlew = Join-Path $root "gradlew.bat"
if (Test-Path $gradlew) {
  Pass "gradlew.bat present (use .\gradlew.bat, not system Gradle)"
} else {
  Fail "gradlew.bat missing"
  Fix "Re-clone the repo or restore gradlew.bat from version control."
}

# Write-Host ""
# Write-Host "Project versions (Kotlin / Compose / SDK)"
# Write-Host "----------------------------------------"
# if (Find-In-Repo $root ("kotlin-gradle-plugin:" + [regex]::Escape($REQUIRED_KOTLIN))) {
#   Pass "Kotlin plugin appears to be $REQUIRED_KOTLIN"
# } else {
#   Warn "Could not confirm Kotlin plugin version $REQUIRED_KOTLIN from Gradle files"
#   Fix "Check classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:$REQUIRED_KOTLIN' in root build.gradle."
# }
#
# if (Find-In-Repo $root ("kotlinCompilerExtensionVersion\s*=\s*`"" + [regex]::Escape($REQUIRED_COMPOSE_COMPILER) + "`"")) {
#   Pass "Compose compiler extension appears to be $REQUIRED_COMPOSE_COMPILER"
# } else {
#   Warn "Could not confirm Compose compiler extension $REQUIRED_COMPOSE_COMPILER"
#   Fix "Check composeOptions { kotlinCompilerExtensionVersion = `"$REQUIRED_COMPOSE_COMPILER`" }"
# }
#
# if (Find-In-Repo $root ("compileSdk\s*=\s*" + [regex]::Escape($REQUIRED_COMPILE_SDK))) {
#   Pass "compileSdk appears to be $REQUIRED_COMPILE_SDK"
# } else {
#   Warn "Could not confirm compileSdk $REQUIRED_COMPILE_SDK"
#   Fix "Check your module build.gradle defaultConfig / android block."
# }

Write-Host ""
Write-Host "Android SDK (platforms/build-tools/ndk/cmake)"
Write-Host "----------------------------------------"
$sdkRoot = $env:ANDROID_SDK_ROOT
if (-not $sdkRoot) { $sdkRoot = $env:ANDROID_HOME }

if (-not $sdkRoot) {
  Warn "ANDROID_SDK_ROOT / ANDROID_HOME not set"
  Fix "Set ANDROID_SDK_ROOT (recommended) or ANDROID_HOME to your Android SDK path. Android Studio typically manages this."
} else {
  Pass "Android SDK path: $sdkRoot"

  $platform = Join-Path $sdkRoot ("platforms\android-" + $REQUIRED_COMPILE_SDK)
  if (Test-Path $platform) {
    Pass "Platform android-$REQUIRED_COMPILE_SDK installed"
  } else {
    Fail "Missing Android platform android-$REQUIRED_COMPILE_SDK"
    Fix "Android Studio → SDK Manager → SDK Platforms → install Android $REQUIRED_COMPILE_SDK."
  }

  $buildTools = Join-Path $sdkRoot ("build-tools\" + $REQUIRED_BUILD_TOOLS)
  if (Test-Path $buildTools) {
    Pass "Build-tools $REQUIRED_BUILD_TOOLS installed"
  } else {
    Fail "Missing Build-tools $REQUIRED_BUILD_TOOLS"
    Fix "Android Studio → SDK Manager → SDK Tools → install Build-tools $REQUIRED_BUILD_TOOLS."
  }

  $ndk = Join-Path $sdkRoot ("ndk\" + $REQUIRED_NDK)
  if (Test-Path $ndk) {
    Pass "NDK $REQUIRED_NDK installed"
  } else {
    Warn "NDK $REQUIRED_NDK not found (native builds/tests may fail)"
    Fix "Android Studio → SDK Manager → SDK Tools → NDK (Side by side) → install $REQUIRED_NDK."
  }

  $cmake = Join-Path $sdkRoot ("cmake\" + $REQUIRED_CMAKE)
  if (Test-Path $cmake) {
    Pass "CMake $REQUIRED_CMAKE installed"
  } else {
    Warn "CMake $REQUIRED_CMAKE not found (native builds/tests may fail)"
    Fix "Android Studio → SDK Manager → SDK Tools → CMake → install $REQUIRED_CMAKE."
  }
}

Write-Host ""
Write-Host "Summary"
Write-Host "----------------------------------------"
Write-Host "PASS: $pass | WARN: $warn | FAIL: $fail"

if ($fail -gt 0) {
  Write-Host ""
  Fail "Doctor found blocking issues. Fix FAIL items above and re-run."
  exit 1
}

if ($warn -gt 0) {
  Write-Host ""
  Warn "Doctor found warnings. The project may still build, but recommended fixes will reduce issues."
  exit 0
}

Write-Host ""
Pass "All checks passed. You should be able to sync and run the sample app."
exit 0
