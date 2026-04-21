# DJI Studio 批量导出说明

这套脚本已经把 `OSV -> 官方全景 MP4` 跑通，走的是 DJI Studio 官方 stitching/export 链路，不是自研拼接。

## 当前能力

- 自动扫描素材目录里的 `*.OSV`
- 自动匹配已有的 DJI Studio live 项目
- 缺项目时自动按官方导入态模板补建项目
- 自动注入官方导出队列
- 自动内部触发导出，不需要手动打开项目或点击导出
- 支持两档输出：
  - `6K`：`6000x3000`
  - `8K`：`7680x3840`
- 自动保留源素材帧率：
  - `60fps` 素材导出成 `60fps`
  - `50fps` 素材导出成 `50fps`

## 短命令包装

如果不想记完整脚本路径，可以直接用这些包装器：

- [/Users/gordonyoung/Offline-Document/bin/dji-export](/Users/gordonyoung/Offline-Document/bin/dji-export)
- [/Users/gordonyoung/Offline-Document/bin/dji-6k](/Users/gordonyoung/Offline-Document/bin/dji-6k)
- [/Users/gordonyoung/Offline-Document/bin/dji-8k](/Users/gordonyoung/Offline-Document/bin/dji-8k)
- [/Users/gordonyoung/Offline-Document/bin/dji-pipeline](/Users/gordonyoung/Offline-Document/bin/dji-pipeline)
- [/Users/gordonyoung/Offline-Document/bin/dji-pipeline-6k](/Users/gordonyoung/Offline-Document/bin/dji-pipeline-6k)
- [/Users/gordonyoung/Offline-Document/bin/dji-pipeline-8k](/Users/gordonyoung/Offline-Document/bin/dji-pipeline-8k)
- [/Users/gordonyoung/Offline-Document/bin/dji-healthcheck](/Users/gordonyoung/Offline-Document/bin/dji-healthcheck)
- [/Users/gordonyoung/Offline-Document/bin/dji-report](/Users/gordonyoung/Offline-Document/bin/dji-report)
- [/Users/gordonyoung/Offline-Document/bin/dji-map](/Users/gordonyoung/Offline-Document/bin/dji-map)

## 环境前提

- macOS
- 已安装 `DJI Studio.app`
- `DJI Studio` 首次导入链已可用
- 当前这套内部触发依赖可 attach 的 `DJI Studio`

说明：
- 如果后续重新安装或更新了 `DJI Studio`，导致内部触发失效，通常是签名恢复成官方原版了，需要重新恢复当前这套可调试状态。

## 最短命令

### 8K 批量导出

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k \
  --preset 8k
```

或者直接：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-8k \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k
```

### 6K 批量导出

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_6k \
  --preset 6k
```

或者直接：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-6k \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_6k
```

### 一条命令跑完整流水线

这个入口会顺序做：
- 健康检查
- 官方导出
- 导出报告
- 输入输出映射

文件：
- [/Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py)

8K：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k_pipeline \
  --preset 8k \
  --prefix avata360_8k
```

或者直接：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-pipeline-8k \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k_pipeline \
  --prefix avata360_8k
```

如果导出已经跑完，只想补报告和映射：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k_full \
  --skip-export \
  --prefix avata360_8k_existing
```

## 常用脚本

### 1. 一键导出入口

文件：
- [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py)

用途：
- 最简单入口，只要给 `input_dir`、`output_dir`、`preset`

参数：
- `input_dir`
- `output_dir`
- `--preset 6k|8k`
- `--pattern`，默认 `*.OSV`
- `--manifest`

### 2. 按素材目录自动匹配/补建 live 项目再导出

文件：
- [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export_source_dir.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export_source_dir.py)

用途：
- 扫描源目录
- 自动找 `~/Library/Application Support/DJI Studio/project/*/proj.db`
- 找不到时可自动新建 live 项目
- 然后批量注入并启动官方导出

关键参数：
- `input_dir`
- `--output-dir`
- `--resolution-type 12|14`
- `--create-missing`
- `--skip-existing`

### 3. 直接针对 live 项目批量导出

文件：
- [/Users/gordonyoung/Offline-Document/scripts/dji_studio_batch_internal_export.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_batch_internal_export.py)

用途：
- 你已经知道哪些 `project/<id>` 要导时，直接对 live 项目批量跑

### 4. 导出结果报告

文件：
- [/Users/gordonyoung/Offline-Document/scripts/dji_studio_report_exports.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_report_exports.py)

用途：
- 对导出的 `mp4` 做 `ffprobe`
- 输出 JSON/CSV 报告

示例：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_report_exports.py \
  /Users/gordonyoung/Offline-Document/exports/final_8k
```

### 5. 生成源文件到导出文件映射

文件：
- [/Users/gordonyoung/Offline-Document/scripts/dji_studio_map_exports.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_map_exports.py)

用途：
- 把源目录里的 `OSV` 和导出目录里的 `*_official.mp4` 对上
- 可带上报告里的分辨率、帧率、编码信息

示例：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_map_exports.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k \
  --report-json /Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.json
```

## 已验证结果

本次 `Avata360` 全量导出结果：
- 输出目录：
  - [/Users/gordonyoung/Offline-Document/exports/final_8k_full](/Users/gordonyoung/Offline-Document/exports/final_8k_full)
- 报告：
  - JSON: [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.json](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.json)
  - CSV: [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.csv](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.csv)

结果摘要：
- 共 `36` 条导出
- 全部为 `HEVC Main 10`
- 全部为 `yuv420p10le`
- 全部为官方全景成片
- `60fps` 源导出成 `7680x3840@60`
- `50fps` 源导出成 `7680x3840@50`

## 排障

### 1. 导出不启动

先确认：
- `DJI Studio` 正在运行
- 当前 app 仍然是可 attach 的那一版

### 2. 更新或重装后突然不工作

优先怀疑：
- `DJI Studio.app` 被恢复成官方签名原版
- 内部触发脚本无法再 attach

### 3. 某条素材没有对应 live 项目

用：
- `--create-missing`

脚本会自动基于 `project/24` 风格创建并安装新项目。

## 这次关键产物

- 一键入口：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py)
- 批量导出：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export_source_dir.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export_source_dir.py)
- 结果报告：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_report_exports.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_report_exports.py)
- 映射脚本：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_map_exports.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_map_exports.py)
- 总控流水线：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py)

## 本地安装短命令

如果你想在任何目录里直接敲这些命令，可以执行：

```bash
zsh /Users/gordonyoung/Offline-Document/scripts/install_dji_bin_links.sh
```

它会把命令链接到：
- `~/.local/bin`

## Makefile 入口

如果你更习惯 `make`，也可以直接用：
- [/Users/gordonyoung/Offline-Document/Makefile](/Users/gordonyoung/Offline-Document/Makefile)

示例：

```bash
make -C /Users/gordonyoung/Offline-Document healthcheck
make -C /Users/gordonyoung/Offline-Document export OUTPUT=/Users/gordonyoung/Offline-Document/exports/make_8k PRESET=8k
make -C /Users/gordonyoung/Offline-Document pipeline OUTPUT=/Users/gordonyoung/Offline-Document/exports/make_pipeline_8k PRESET=8k PREFIX=make_pipeline
```
