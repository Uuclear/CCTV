#!/usr/bin/env bash
# 构建幕色 release APK 并复制到 dist/
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
export ANDROID_HOME="${ANDROID_HOME:-$HOME/android-sdk}"
./gradlew :app:assembleRelease
mkdir -p dist
cp -f app/build/outputs/apk/release/app-release.apk "dist/muse-walls-v1.0.0.apk"
ls -lh "dist/muse-walls-v1.0.0.apk"
echo "产物: $ROOT/dist/muse-walls-v1.0.0.apk"
