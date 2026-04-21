#!/bin/zsh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
REPO="Gordonynh/dji-panorama-exporter"
TAG="${1:-v0.1.0}"
DMG_PATH="$ROOT/dist/release/DJI-Panorama-Exporter.dmg"
TITLE="DJI Panorama Exporter $TAG"
NOTES_FILE="$ROOT/dist/release/release-notes.md"

if [[ ! -f "$DMG_PATH" ]]; then
  echo "DMG not found: $DMG_PATH" >&2
  exit 1
fi

mkdir -p "$(dirname "$NOTES_FILE")"
cat > "$NOTES_FILE" <<NOTES
- Native macOS release build
- Bundles validated DJI runtime under the app package
- Supports 6K / 8K, 10-bit, denoise presets, and batch export
NOTES

if gh release view "$TAG" --repo "$REPO" >/dev/null 2>&1; then
  gh release upload "$TAG" "$DMG_PATH#DJI-Panorama-Exporter.dmg" --repo "$REPO" --clobber
else
  gh release create "$TAG" "$DMG_PATH#DJI-Panorama-Exporter.dmg" --repo "$REPO" --title "$TITLE" --notes-file "$NOTES_FILE"
fi
