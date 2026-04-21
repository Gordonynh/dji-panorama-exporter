# Release Notes

## DJI Studio Toolkit Bundle v1.0.0

这是一套基于 DJI Studio 官方导出链的本地批量导出工具包。

它的目标很直接：
- 输入一个包含 `OSV` 的目录
- 输出官方 stitching/export 生成的全景 `MP4`
- 尽量减少人工操作

## 这版能做什么

- 批量导出 `OSV -> 全景 MP4`
- 支持 `6K` 和 `8K`
- 自动保留素材原始帧率
- 自动生成导出报告
- 自动生成源文件到成片文件的映射表
- 提供健康检查，方便更新或迁移后快速判断是否还能正常工作

## 这版已经验证过什么

- 在当前机器上完成了整批 `36` 条 `OSV` 的 `8K` 导出验证
- 健康检查通过
- 内部触发链可用
- 输出映射完整，`36/36` 对应成功

## 最适合谁用

- 需要把一批 DJI `OSV` 快速批量导出成全景视频的人
- 需要保留 DJI 官方 stitching/export 效果的人
- 希望把导出流程标准化、可复用的人

## 怎么开始

### 1. 先做健康检查

```bash
./bin/dji-healthcheck
```

### 2. 直接导出 8K

```bash
./bin/dji-8k /path/to/input_dir /path/to/output_dir
```

### 3. 跑完整流水线

```bash
./bin/dji-pipeline-8k /path/to/input_dir /path/to/output_dir --prefix run_name
```

## 如果后面失效了

优先看：
- `docs/README_DJI_STUDIO_RECOVERY.md`

通常最先需要确认的是：
- `DJI Studio` 还能不能被 attach
- 关键内部符号还在不在

## 包内重点文件

- 快速说明：`README.md`
- 主说明：`docs/README_DJI_STUDIO_EXPORT.md`
- 恢复说明：`docs/README_DJI_STUDIO_RECOVERY.md`
- 交付摘要：`docs/FINAL_DJI_STUDIO_DELIVERY.md`
- 版本快照：`VERSION.json`
- 变更记录：`CHANGELOG.md`
