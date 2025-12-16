#!/usr/bin/env bash
set -euo pipefail

VERSION="${1:?Usage: set-gradle-wrapper-version.sh <gradleVersion>}"
FILE="gradle/wrapper/gradle-wrapper.properties"

if [[ ! -f "$FILE" ]]; then
  echo "Missing $FILE"
  exit 1
fi

# Replace distributionUrl line
sed -i.bak -E "s#distributionUrl=.*#distributionUrl=https\\://services.gradle.org/distributions/gradle-${VERSION}-bin.zip#g" "$FILE"
rm -f "${FILE}.bak"

echo "Updated Gradle wrapper to ${VERSION}"
grep "distributionUrl=" "$FILE"
