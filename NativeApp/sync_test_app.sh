#!/bin/zsh
set -euo pipefail
ROOT='/Users/gordonyoung/Desktop/Projects/DJIStudio/NativeApp'
APP_DIR="$ROOT/TestApp/DJIStudioNativeApp.app"
BIN_SRC="$ROOT/.build/debug/DJIStudioNativeApp"
rm -rf "$APP_DIR"
mkdir -p "$APP_DIR/Contents/MacOS" "$APP_DIR/Contents/Resources"
cat > "$APP_DIR/Contents/Info.plist" <<'PLIST'
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>CFBundleDevelopmentRegion</key><string>en</string>
<key>CFBundleExecutable</key><string>DJIStudioNativeApp</string>
<key>CFBundleIdentifier</key><string>local.codex.DJIStudioNativeApp</string>
<key>CFBundleInfoDictionaryVersion</key><string>6.0</string>
<key>CFBundleName</key><string>DJIStudioNativeApp</string>
<key>CFBundlePackageType</key><string>APPL</string>
<key>CFBundleShortVersionString</key><string>1.0</string>
<key>CFBundleVersion</key><string>1</string>
<key>LSMinimumSystemVersion</key><string>13.0</string>
<key>NSHighResolutionCapable</key><true/>
</dict></plist>
PLIST
cp "$BIN_SRC" "$APP_DIR/Contents/MacOS/DJIStudioNativeApp"
codesign --force --deep --sign - "$APP_DIR"
codesign --verify --deep --strict "$APP_DIR"
echo "$APP_DIR"
