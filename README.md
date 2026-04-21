# DJI Panorama Exporter

Native macOS toolkit for converting DJI `OSV` panoramic source files into high-quality equirectangular MP4 using a bundled minimal DJI runtime.

## What It Does

- Imports DJI `OSV` files
- Creates temporary DJI live projects automatically
- Exports panoramic MP4 in `6K` or `8K`
- Preserves source frame rate (`50fps` / `60fps`)
- Supports `10-bit` export
- Supports denoise modes and bitrate presets
- Supports hidden/background runtime launch
- Supports cancellation of queued and running exports with cleanup
- Includes a native SwiftUI macOS front-end and scriptable CLI workflow

## Repository Layout

- `NativeApp/`
  - SwiftUI macOS app for drag-and-drop export
- `runtime_candidate/`
  - Minimal validated DJI runtime required to execute export jobs
- `scripts/`
  - Export orchestration, runtime validation, regression tests, smoke tests
- `bin/`
  - Convenience wrappers
- `docs/`
  - Validation notes, runtime status, quality notes, migration and recovery docs
- `config/`
  - Local path configuration

## Requirements

- macOS
- Python 3
- Swift toolchain if you want to build the native app locally
- Existing DJI support data under:
  - `~/Library/Application Support/DJI Studio`

## Quick Start

### Health Check

```bash
./bin/dji-healthcheck
```

### Export an Entire Directory in 8K

```bash
./bin/dji-8k /path/to/input_dir /path/to/output_dir
```

### Export an Entire Directory in 6K

```bash
./bin/dji-6k /path/to/input_dir /path/to/output_dir
```

### Build the Native App

```bash
cd NativeApp
swift build
```

### Run the Native App

```bash
cd NativeApp
swift run DJIStudioNativeApp
```

## Native App Features

- Drag files into the drop zone
- Click the drop zone to choose files
- Select `6K` / `8K`
- Select source frame rate or force a target frame rate
- Select bitrate mode: `low`, `medium`, `high`, `custom`
- Enable or disable denoise
- Choose denoise mode: `performance` / `quality`
- Enable or disable `10-Bit`
- Set queue parallelism for staging
- Watch per-file progress and logs
- Stop queued or running exports with cleanup
- Switch UI language inside the app

## CLI and Automation

Main wrappers:

- `./bin/dji-6k`
- `./bin/dji-8k`
- `./bin/dji-pipeline-6k`
- `./bin/dji-pipeline-8k`
- `./bin/dji-healthcheck`

Useful scripts:

- `scripts/dji_studio_export_files.py`
- `scripts/dji_studio_batch_internal_export.py`
- `scripts/dji_studio_validate_runtime_export.py`
- `scripts/dji_studio_stop_regression.py`
- `scripts/dji_native_app_smoke_test.py`

## Runtime Status

Current validated state:

- `runtime_candidate` can perform real high-quality export
- `runtime_candidate` supports hidden/background launch
- queued and running task cancellation has been regression-tested
- `50fps` and `60fps` source frame rates are preserved

See:

- `docs/RUNTIME_VALIDATION_STATUS.md`
- `docs/QUALITY_STATUS.md`

## Important Note

This repository does **not** reimplement DJI panoramic stitching from scratch.
It packages a validated minimal runtime and automation layer around DJI's private export pipeline.

## Current Constraints

- This workflow still depends on DJI support data stored on the local machine
- Runtime behavior is validated on macOS only
- The bundled runtime is minimized, but not trivial in size

