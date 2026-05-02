#!/bin/bash
set -e

WORKFLOW_NAME="DS-Translator"
BUILD_DIR="build"
OUTPUT="${WORKFLOW_NAME}.alfredworkflow"

rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

cp info.plist translate.py "$BUILD_DIR/"
[ -f icon.png ] && cp icon.png "$BUILD_DIR/"

cd "$BUILD_DIR"
zip -r "../${OUTPUT}" . -x ".*"
cd ..

rm -rf "$BUILD_DIR"

echo "✅  Built ${OUTPUT}"
echo "Double-click the file to install in Alfred."
