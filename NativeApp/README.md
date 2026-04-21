# DJIStudioNativeApp

Native macOS SwiftUI front-end for the DJIStudio export workflow.

## What it does

- Drag OSV files into a native macOS window
- Click the drop area to choose files, or drag OSV files into it
- Choose output directory and 6K/8K preset
- Set frame rate, bitrate mode, custom bitrate, denoise, denoise mode, 10-bit, and parallel count
- Watch per-file export progress in the file list
- Switch UI language inside the app
- Run the existing high-quality export workflow
- Create temporary live DJI Studio projects for the selected OSV files
- Clean up temporary live projects and clone directories after export
- Stop an active export and clean up the partially generated task/output

## Supported UI languages

- English
- 中文(简体)
- 中文(繁體)
- 日本語
- 한국어
- Français
- Deutsch
- Español
- Português (Brasil)
- Русский
- Italiano
- العربية

## Build

```bash
cd /Users/gordonyoung/Desktop/Projects/DJIStudio/NativeApp
swift build
```

## Run

```bash
cd /Users/gordonyoung/Desktop/Projects/DJIStudio/NativeApp
swift run DJIStudioNativeApp
```

## Notes

- The app uses the Python workflow in:
  - `/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_export_files.py`
- By default it resolves the project root by checking:
  1. `DJI_STUDIO_PROJECT_ROOT`
  2. current working directory
  3. the compiled source location
  4. `/Users/gordonyoung/Desktop/Projects/DJIStudio`
- Runtime export still depends on the validated DJI private runtime in this project.
- Files missing from DJI Studio `copy_info.json` will currently fail during temporary project creation.
- Native app strings are localized inside the Swift app. System dialogs such as `NSOpenPanel` still follow the macOS system language.
- Parallel count currently controls how many files are staged into each export batch. The underlying DJI export runtime still processes one task at a time per hidden runtime instance.
- Stopping an export is now a real cancellation path:
  - queued tasks are removed from `composeList`
  - running tasks terminate the current hidden runtime
  - partial outputs are deleted
  - temporary live projects are cleaned up
- This stop path has also been regression-tested against multiple samples after they entered `state=1`, not just while queued.
