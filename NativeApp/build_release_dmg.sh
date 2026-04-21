#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
APP_NAME="DJI Panorama Exporter"
EXECUTABLE_NAME="DJIStudioNativeApp"
BUNDLE_ID="com.gordonyoung.djipanoramaexporter"
NATIVE_APP_DIR="$ROOT/NativeApp"
BUILD_DIR="$NATIVE_APP_DIR/.build/release"
DIST_DIR="$ROOT/dist/release"
APP_BUNDLE="$DIST_DIR/$APP_NAME.app"
DMG_STAGING="$DIST_DIR/dmg"
DMG_PATH="$DIST_DIR/DJI-Panorama-Exporter.dmg"
PROJECT_PAYLOAD="$APP_BUNDLE/Contents/Resources/project"

rm -rf "$APP_BUNDLE" "$DMG_STAGING" "$DMG_PATH"
mkdir -p "$APP_BUNDLE/Contents/MacOS" "$APP_BUNDLE/Contents/Resources" "$DIST_DIR"

cd "$NATIVE_APP_DIR"
swift build -c release

cp "$BUILD_DIR/$EXECUTABLE_NAME" "$APP_BUNDLE/Contents/MacOS/$EXECUTABLE_NAME"
chmod +x "$APP_BUNDLE/Contents/MacOS/$EXECUTABLE_NAME"

cat > "$APP_BUNDLE/Contents/Info.plist" <<PLIST
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>CFBundleDevelopmentRegion</key>
    <string>en</string>
    <key>CFBundleExecutable</key>
    <string>$EXECUTABLE_NAME</string>
    <key>CFBundleIdentifier</key>
    <string>$BUNDLE_ID</string>
    <key>CFBundleInfoDictionaryVersion</key>
    <string>6.0</string>
    <key>CFBundleName</key>
    <string>$APP_NAME</string>
    <key>CFBundlePackageType</key>
    <string>APPL</string>
    <key>CFBundleShortVersionString</key>
    <string>0.1.0</string>
    <key>CFBundleVersion</key>
    <string>1</string>
    <key>LSMinimumSystemVersion</key>
    <string>14.0</string>
    <key>NSPrincipalClass</key>
    <string>NSApplication</string>
</dict>
</plist>
PLIST

mkdir -p "$PROJECT_PAYLOAD"
rsync -a "$ROOT/scripts" "$PROJECT_PAYLOAD/"
rsync -a "$ROOT/config" "$PROJECT_PAYLOAD/"
rsync -a "$ROOT/runtime_candidate" "$PROJECT_PAYLOAD/"
cp "$ROOT/README.md" "$PROJECT_PAYLOAD/README.md"
cp "$ROOT/README.zh-CN.md" "$PROJECT_PAYLOAD/README.zh-CN.md"
cat > "$PROJECT_PAYLOAD/config/dji_paths.json" <<JSON
{
  "component_mode": "runtime_candidate"
}
JSON

xattr -c "$APP_BUNDLE" 2>/dev/null || true
find "$APP_BUNDLE" -type d -exec xattr -c {} + 2>/dev/null || true
find "$APP_BUNDLE" -type f -exec xattr -c {} + 2>/dev/null || true
codesign --force --deep --sign - "$APP_BUNDLE"

mkdir -p "$DMG_STAGING"
ln -s /Applications "$DMG_STAGING/Applications"
cp -R "$APP_BUNDLE" "$DMG_STAGING/"

hdiutil create -volname "$APP_NAME" -srcfolder "$DMG_STAGING" -ov -format UDZO "$DMG_PATH"

printf 'APP=%s\nDMG=%s\n' "$APP_BUNDLE" "$DMG_PATH"
