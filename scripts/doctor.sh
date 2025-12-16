#!/usr/bin/env bash
set -euo pipefail

# ----------------------------
# ComplyCube Sample App Doctor
# macOS / Linux
# ----------------------------

REQUIRED_JAVA_MAJOR=17
REQUIRED_GRADLE_WRAPPER="8.9"
REQUIRED_AGP_DEFAULT="8.7.2"
REQUIRED_KOTLIN="1.9.25"
REQUIRED_COMPOSE_COMPILER="1.5.15"
REQUIRED_COMPILE_SDK="34"
REQUIRED_BUILD_TOOLS="34.0.0"
REQUIRED_NDK="29.0.13113456"
REQUIRED_CMAKE="3.22.1"

SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="${SCRIPT_DIR}"

if command -v git >/dev/null 2>&1 && git -C "${SCRIPT_DIR}" rev-parse --show-toplevel >/dev/null 2>&1; then
  ROOT_DIR="$(git -C "${SCRIPT_DIR}" rev-parse --show-toplevel)"
fi

PASS_COUNT=0
WARN_COUNT=0
FAIL_COUNT=0

bold() { printf "\033[1m%s\033[0m\n" "$1"; }
ok()   { PASS_COUNT=$((PASS_COUNT+1)); printf "✅ PASS: %s\n" "$1"; }
warn() { WARN_COUNT=$((WARN_COUNT+1)); printf "⚠️  WARN: %s\n" "$1"; }
fail() { FAIL_COUNT=$((FAIL_COUNT+1)); printf "❌ FAIL: %s\n" "$1"; }

fix() {
  printf "   ↳ Fix: %s\n" "$1"
}

section() {
  echo ""
  bold "$1"
  echo "----------------------------------------"
}

# -------- helpers --------
extract_java_major() {
  if ! command -v java >/dev/null 2>&1; then
    echo ""
    return
  fi

  # java -version output examples:
  # openjdk version "17.0.10"  or  java version "1.8.0_..."
  local v
  v="$(java -version 2>&1 | head -n 1)"

  # Try to extract first quoted token
  local token
  token="$(echo "$v" | sed -n 's/.*version "\(.*\)".*/\1/p')"
  if [[ -z "${token}" ]]; then
    echo ""
    return
  fi

  if [[ "${token}" == 1.* ]]; then
    # Java 8 style 1.8.x -> major 8
    echo "${token}" | cut -d. -f2
  else
    echo "${token}" | cut -d. -f1
  fi
}

find_in_repo() {
  # $1 = grep pattern
  # Searches *.gradle and *.gradle.kts (fast enough)
  local pattern="$1"
  grep -R --line-number --no-messages -E "$pattern" \
    "$ROOT_DIR" \
    --include="*.gradle" \
    --include="*.gradle.kts" || true
}

get_gradle_wrapper_version() {
  local f="${ROOT_DIR}/gradle/wrapper/gradle-wrapper.properties"
  [[ -r "$f" ]] || return 0

  local url
  url="$(awk -F= '/^distributionUrl=/{print $2}' "$f" | tr -d '\r')"
  [[ -n "$url" ]] || return 0

  # Extract "8.9" from ".../gradle-8.9-bin.zip"
  if [[ "$url" =~ gradle-([0-9.]+)- ]]; then
    echo "${BASH_REMATCH[1]}"
  fi
}


# -------- checks --------
section "Environment"
echo "Repo root: $ROOT_DIR"
echo "OS: $(uname -s) | Arch: $(uname -m)"

section "Java (Build JDK)"
JAVA_MAJOR="$(extract_java_major)"
if [[ -z "${JAVA_MAJOR}" ]]; then
  fail "Java not found on PATH"
  fix "Install JDK ${REQUIRED_JAVA_MAJOR} and set Android Studio Gradle JDK to it (Settings → Build Tools → Gradle → Gradle JDK)."
else
  if [[ "${JAVA_MAJOR}" -lt "${REQUIRED_JAVA_MAJOR}" ]]; then
    fail "Java major version is ${JAVA_MAJOR}, but build requires JDK ${REQUIRED_JAVA_MAJOR}+"
    fix "Install JDK ${REQUIRED_JAVA_MAJOR} and point Android Studio Gradle JDK to it. Also ensure your terminal uses it (JAVA_HOME)."
  else
    ok "Java major version is ${JAVA_MAJOR}"
  fi
fi

section "Gradle Wrapper"
WRAPPER_VER="$(get_gradle_wrapper_version)"
if [[ -z "${WRAPPER_VER}" ]]; then
  fail "Gradle wrapper not found or unreadable (gradle/wrapper/gradle-wrapper.properties)"
  fix "Ensure the repo includes gradle wrapper files. Re-clone the repository if needed."
else
  if [[ "${WRAPPER_VER}" != "${REQUIRED_GRADLE_WRAPPER}" ]]; then
    warn "Gradle wrapper is ${WRAPPER_VER} (expected ${REQUIRED_GRADLE_WRAPPER})"
    fix "Use the repository wrapper anyway: ./gradlew <task>. If the project was upgraded, update this script's REQUIRED_GRADLE_WRAPPER."
  else
    ok "Gradle wrapper version is ${WRAPPER_VER}"
  fi
fi

if [[ -f "$ROOT_DIR/gradlew" ]]; then
  ok "gradlew present (use ./gradlew, not a system Gradle)"
else
  fail "gradlew missing"
  fix "Re-clone the repo (wrapper scripts are required) or restore gradlew from version control."
fi

#section "Project versions (AGP / Kotlin / Compose / SDK)"
#AGP_VERSION="${AGP_VERSION:-}"
#if [[ -n "$AGP_VERSION" ]]; then
#  ok "AGP_VERSION env var is set to ${AGP_VERSION}"
#else
#  # Try to detect default from build.gradle: def agpVersion = ... ?: '8.7.2'
#  AGP_LINE="$(find_in_repo "agpVersion.*\\?:\\s*'([0-9]+\\.[0-9]+\\.[0-9]+)'")"
#  if [[ -n "$AGP_LINE" ]]; then
#    ok "AGP default appears configured in Gradle (expected default ${REQUIRED_AGP_DEFAULT})"
#  else
#    warn "Could not detect AGP default in Gradle files"
#    fix "Ensure buildscript defines AGP version (or set AGP_VERSION env var)."
#  fi
#fi
#
#KOTLIN_LINE="$(find_in_repo "kotlin-gradle-plugin:${REQUIRED_KOTLIN}")"
#if [[ -n "$KOTLIN_LINE" ]]; then
#  ok "Kotlin plugin appears to be ${REQUIRED_KOTLIN}"
#else
#  warn "Could not confirm Kotlin plugin version ${REQUIRED_KOTLIN} from Gradle files"
#  fix "Check classpath 'org.jetbrains.kotlin:kotlin-gradle-plugin:${REQUIRED_KOTLIN}' in the root build.gradle."
#fi
#
#COMPOSE_LINE="$(find_in_repo "kotlinCompilerExtensionVersion\\s*=\\s*\"${REQUIRED_COMPOSE_COMPILER}\"")"
#if [[ -n "$COMPOSE_LINE" ]]; then
#  ok "Compose compiler extension appears to be ${REQUIRED_COMPOSE_COMPILER}"
#else
#  warn "Could not confirm Compose compiler extension ${REQUIRED_COMPOSE_COMPILER}"
#  fix "Check composeOptions { kotlinCompilerExtensionVersion = \"${REQUIRED_COMPOSE_COMPILER}\" }"
#fi
#
#COMPILE_SDK_LINE="$(find_in_repo "compileSdk\\s*=\\s*${REQUIRED_COMPILE_SDK}")"
#if [[ -n "$COMPILE_SDK_LINE" ]]; then
#  ok "compileSdk appears to be ${REQUIRED_COMPILE_SDK}"
#else
#  warn "Could not confirm compileSdk ${REQUIRED_COMPILE_SDK}"
#  fix "Check your module build.gradle defaultConfig / android block."
#fi

section "Android SDK (platforms/build-tools/ndk/cmake)"
SDK_ROOT="${ANDROID_SDK_ROOT:-${ANDROID_HOME:-}}"
if [[ -z "$SDK_ROOT" ]]; then
  warn "ANDROID_SDK_ROOT / ANDROID_HOME not set"
  fix "Set ANDROID_SDK_ROOT (recommended) or ANDROID_HOME to your Android SDK location. Android Studio usually manages this automatically."
else
  ok "Android SDK path: $SDK_ROOT"

  if [[ -d "$SDK_ROOT/platforms/android-${REQUIRED_COMPILE_SDK}" ]]; then
    ok "Platform android-${REQUIRED_COMPILE_SDK} installed"
  else
    fail "Missing Android platform android-${REQUIRED_COMPILE_SDK}"
    fix "Android Studio → SDK Manager → SDK Platforms → install Android ${REQUIRED_COMPILE_SDK}."
  fi

  if [[ -d "$SDK_ROOT/build-tools/${REQUIRED_BUILD_TOOLS}" ]]; then
    ok "Build-tools ${REQUIRED_BUILD_TOOLS} installed"
  else
    fail "Missing Build-tools ${REQUIRED_BUILD_TOOLS}"
    fix "Android Studio → SDK Manager → SDK Tools → install Build-tools ${REQUIRED_BUILD_TOOLS}."
  fi

  if [[ -d "$SDK_ROOT/ndk/${REQUIRED_NDK}" ]]; then
    ok "NDK ${REQUIRED_NDK} installed"
  else
    warn "NDK ${REQUIRED_NDK} not found (native builds/tests may fail)"
    fix "Android Studio → SDK Manager → SDK Tools → NDK (Side by side) → install ${REQUIRED_NDK}."
  fi

  if [[ -d "$SDK_ROOT/cmake/${REQUIRED_CMAKE}" ]]; then
    ok "CMake ${REQUIRED_CMAKE} installed"
  else
    warn "CMake ${REQUIRED_CMAKE} not found (native builds/tests may fail)"
    fix "Android Studio → SDK Manager → SDK Tools → CMake → install ${REQUIRED_CMAKE}."
  fi
fi

section "Summary"
echo "PASS: ${PASS_COUNT} | WARN: ${WARN_COUNT} | FAIL: ${FAIL_COUNT}"

if [[ "${FAIL_COUNT}" -gt 0 ]]; then
  echo ""
  fail "Doctor found blocking issues. Fix FAIL items above and re-run."
  exit 1
fi

if [[ "${WARN_COUNT}" -gt 0 ]]; then
  echo ""
  warn "Doctor found warnings. The project may still build, but recommended fixes will reduce issues."
  exit 0
fi

echo ""
ok "All checks passed. You should be able to sync and run the sample app."
exit 0
