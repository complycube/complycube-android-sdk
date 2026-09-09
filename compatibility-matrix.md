# Compatibility Matrix

> Generated from release-tag CI results. Every row uses the exact SDK version shown; no floating or historical SDK versions are substituted.

A passing row verifies that the sample application compiled and packaged with that exact combination. Unlisted combinations are **not tested**, not automatically incompatible. Gate rows are release requirements; canary rows provide early warning and do not block a release.

`assemble` builds the debug APK. `full` also builds the release APK, runs unit tests, and runs Android lint.

## Build combinations

No verified release results are available yet. The next semantic-version release tag will populate this report.

## Scope

These checks verify dependency resolution, compilation, tests/lint where marked `full`, and APK packaging. They do not by themselves prove runtime behavior on every Android device or OS version.
