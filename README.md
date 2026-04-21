# DJI OSV Export Runtime

Native macOS toolkit for exporting DJI `OSV` panoramic source files to high-quality equirectangular MP4 using a bundled minimal DJI runtime.

## What this repository contains

- `runtime_candidate/`
  - minimal validated DJI runtime required to execute export jobs
- `NativeApp/`
  - SwiftUI macOS front-end for drag-and-drop export
- `scripts/`
  - Python automation, export orchestration, runtime validation, and regression tooling
- `docs/`
  - engineering notes, runtime validation status, and usage documentation
- `bin/`
  - convenience wrappers

## What this repository does

- Creates temporary DJI Studio live projects from OSV files
- Exports 6K / 8K panoramic MP4
- Preserves source frame rate (`50fps` / `60fps`)
- Supports high-quality export settings including 10-bit output
- Runs with the bundled `runtime_candidate` instead of requiring an installed `DJI Studio.app`
- Supports hidden/background runtime launch
- Supports cancellation of queued and running exports with cleanup

## Requirements

- macOS
- Python 3
- Swift toolchain (only if building the NativeApp locally)
- Existing DJI support data under:
  - `~/Library/Application Support/DJI Studio`

## Quick start

Health check:

```bash
./bin/dji-healthcheck
```

8K export:

```bash
./bin/dji-8k /path/to/input_dir /path/to/output_dir
```

Native app build:

```bash
cd NativeApp
swift build
```

## Important note

This repository bundles a minimized runtime needed to execute the export workflow. It does **not** reimplement DJI stitching logic from scratch.
