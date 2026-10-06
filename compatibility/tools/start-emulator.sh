#!/usr/bin/env bash
# Disposable CI device; never wipes an existing developer AVD.
set -euo pipefail
export PATH="$ANDROID_HOME/cmdline-tools/latest/bin:$ANDROID_HOME/platform-tools:$PATH"
sdkmanager "platforms;android-34" "platforms;android-36" "build-tools;34.0.0" "build-tools;35.0.0" "system-images;android-35;google_apis;x86_64"
echo no | avdmanager create avd --name consumer-compat-ci --package "system-images;android-35;google_apis;x86_64"
"$ANDROID_HOME/emulator/emulator" -avd consumer-compat-ci -no-window -no-audio -no-boot-anim -no-snapshot -gpu swiftshader_indirect > "$RUNNER_TEMP/emulator.log" 2>&1 &
adb wait-for-device
for attempt in $(seq 1 120); do
  if [[ "$(adb shell getprop sys.boot_completed | tr -d '\r')" == "1" ]]; then
    adb shell input keyevent 82
    exit 0
  fi
  sleep 2
done
echo "Emulator did not boot within four minutes" >&2
exit 1
