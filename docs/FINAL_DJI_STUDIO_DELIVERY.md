# DJI Studio 官方批量全景导出交付摘要

## 目标

把 `OSV` 批量导出成 DJI 官方 stitching/export 生成的全景 `MP4`，并尽量去掉人工操作。

## 最终结果

这套链已经实现：

- 自动扫描源目录中的 `OSV`
- 自动匹配或补建 DJI Studio live 项目
- 自动注入官方导出队列
- 自动调用 DJI Studio 内部启动导出
- 批量导出 `6K/8K` 全景 `MP4`
- 自动保留源素材帧率
- 自动生成导出报告与源文件映射

## 已验证结果

### `Avata360` 全量 8K

- 源目录：
  - [/Users/gordonyoung/Offline-Document/Avata360](/Users/gordonyoung/Offline-Document/Avata360)
- 输出目录：
  - [/Users/gordonyoung/Offline-Document/exports/final_8k_full](/Users/gordonyoung/Offline-Document/exports/final_8k_full)
- 数量：
  - `36 / 36` 成功
- 规格：
  - `HEVC`
  - `Main 10`
  - `yuv420p10le`
  - `7680x3840`
  - `60fps` 源导出成 `60fps`
  - `50fps` 源导出成 `50fps`

## 最常用入口

### 1. 一键导出

- 脚本：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py)
- 包装命令：
  - [/Users/gordonyoung/Offline-Document/bin/dji-export](/Users/gordonyoung/Offline-Document/bin/dji-export)

示例：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-export \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k_again \
  --preset 8k
```

### 2. 一键流水线

- 脚本：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_pipeline.py)
- 包装命令：
  - [/Users/gordonyoung/Offline-Document/bin/dji-pipeline](/Users/gordonyoung/Offline-Document/bin/dji-pipeline)

示例：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-pipeline \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k_pipeline \
  --preset 8k \
  --prefix avata360_8k
```

### 3. 健康检查

- 脚本：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_healthcheck.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_healthcheck.py)
- 包装命令：
  - [/Users/gordonyoung/Offline-Document/bin/dji-healthcheck](/Users/gordonyoung/Offline-Document/bin/dji-healthcheck)

示例：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-healthcheck
```

### 4. 导出报告

- 包装命令：
  - [/Users/gordonyoung/Offline-Document/bin/dji-report](/Users/gordonyoung/Offline-Document/bin/dji-report)

示例：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-report \
  /Users/gordonyoung/Offline-Document/exports/final_8k_full
```

### 5. 输入输出映射

- 包装命令：
  - [/Users/gordonyoung/Offline-Document/bin/dji-map](/Users/gordonyoung/Offline-Document/bin/dji-map)

示例：

```bash
/Users/gordonyoung/Offline-Document/bin/dji-map \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/final_8k_full \
  --report-json /Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.json
```

## 关键报告

- 主说明：
  - [/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_EXPORT.md](/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_EXPORT.md)
- 恢复说明：
  - [/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_RECOVERY.md](/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_RECOVERY.md)
- 全量导出报告 JSON：
  - [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.json](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.json)
- 全量导出报告 CSV：
  - [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.csv](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_report.csv)
- 全量映射 JSON：
  - [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_mapping.json](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_mapping.json)
- 全量映射 CSV：
  - [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_mapping.csv](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/final_8k_full_mapping.csv)
- 当前健康检查：
  - [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/healthcheck.json](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/healthcheck.json)

## 核心实现点

1. 不是自研拼接，而是走 DJI Studio 官方导出链
2. 内部启动调用已抓到并接入：
   - `ExportTabViewModel::autoCompose(true)`
3. `compose draft` 会在注入时自动 patch 成目标导出 profile
4. 导出分辨率映射：
   - `12 -> 6000x3000`
   - `14 -> 7680x3840`

## 当前限制

- 这套链依赖当前机器上的 DJI Studio 可 attach 状态
- 如果 DJI Studio 更新、重装或签名恢复，内部触发可能失效
- 失效后先跑健康检查，再按恢复说明处理
