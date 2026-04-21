# DJI Panorama Exporter

[English](README.md) | [中文](README.zh-CN.md)

一个用于将大疆 `OSV` 全景源文件快速导出为高质量等距柱状投影 MP4 的原生 macOS 工具包，内置经过验证的最小 DJI 运行时。

## 项目功能

- 导入 DJI `OSV` 文件
- 自动创建临时 DJI live 项目
- 导出 `6K` 或 `8K` 全景 MP4
- 保留源素材帧率（`50fps` / `60fps`）
- 支持 `10-bit` 导出
- 支持降噪模式和码率预设
- 支持隐藏/后台方式启动运行时
- 支持取消排队中或运行中的导出任务，并自动清理残留
- 同时提供原生 SwiftUI macOS 前端和可脚本化的 CLI 工作流

## 仓库结构

- `NativeApp/`
  - 用于拖拽导出的 SwiftUI macOS 应用
- `runtime_candidate/`
  - 执行导出任务所需的最小化、已验证 DJI 运行时
- `scripts/`
  - 导出编排、运行时验证、回归测试、冒烟测试脚本
- `bin/`
  - 便捷命令封装
- `docs/`
  - 验证记录、运行时状态、画质说明、迁移与恢复文档
- `config/`
  - 本地路径配置

## 运行要求

- macOS
- Python 3
- 如果需要本地构建原生 App，还需要 Swift toolchain
- 机器上需要已有 DJI 支持数据目录：
  - `~/Library/Application Support/DJI Studio`

## 快速开始

### 健康检查

```bash
./bin/dji-healthcheck
```

### 整个目录导出为 8K

```bash
./bin/dji-8k /path/to/input_dir /path/to/output_dir
```

### 整个目录导出为 6K

```bash
./bin/dji-6k /path/to/input_dir /path/to/output_dir
```

### 构建原生 App

```bash
cd NativeApp
swift build
```

### 运行原生 App

```bash
cd NativeApp
swift run DJIStudioNativeApp
```

## 原生 App 功能

- 将文件拖入上传框
- 点击上传框选择文件
- 选择 `6K` / `8K`
- 选择保留源帧率，或强制指定目标帧率
- 选择码率模式：`low`、`medium`、`high`、`custom`
- 开启或关闭降噪
- 选择降噪模式：`performance` / `quality`
- 开启或关闭 `10-Bit`
- 设置任务分批并行数量
- 查看每个文件的进度与日志
- 停止排队中或运行中的导出任务，并自动清理
- 在 App 内切换界面语言

## CLI 与自动化

主要命令：

- `./bin/dji-6k`
- `./bin/dji-8k`
- `./bin/dji-pipeline-6k`
- `./bin/dji-pipeline-8k`
- `./bin/dji-healthcheck`

常用脚本：

- `scripts/dji_studio_export_files.py`
- `scripts/dji_studio_batch_internal_export.py`
- `scripts/dji_studio_validate_runtime_export.py`
- `scripts/dji_studio_stop_regression.py`
- `scripts/dji_native_app_smoke_test.py`

## 运行时状态

当前已验证状态：

- `runtime_candidate` 可以执行真实的高质量导出
- `runtime_candidate` 支持隐藏/后台启动
- 排队中和运行中的任务取消链已完成回归验证
- `50fps` 和 `60fps` 源素材帧率都可以保真导出

可参考：

- `docs/RUNTIME_VALIDATION_STATUS.md`
- `docs/QUALITY_STATUS.md`

## 重要说明

这个仓库**不是**从零开始重写 DJI 的全景拼接算法。
它提供的是围绕 DJI 私有导出链路构建的一套最小化、已验证运行时与自动化封装。

## 当前限制

- 这套流程仍依赖本机已有的 DJI 支持数据
- 运行时行为目前只在 macOS 上完成验证
- 内置运行时已经裁剪，但体积仍然不小
