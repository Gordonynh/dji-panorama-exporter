# DJIStudio Project

这是 `/Users/gordonyoung/Desktop/Projects/DJIStudio` 这个完整工程的项目说明。

## 目标

把当前已经验证通过的 DJI 官方全景导出链，整理成一个可维护、可迁移、可继续开发的本地项目。

## 当前结构

- `bin/`
  - 命令入口
- `scripts/`
  - 核心逻辑
- `docs/`
  - 使用、恢复、迁移、交付说明
  - 以及当前 runtime / 质量状态说明
- `config/dji_paths.json`
  - 项目级路径配置
- `vendor/`
  - 官方组件本地快照目录
- `output/`
  - 默认导出目录
- `examples/`
  - 预留样例目录

## 关键说明

### 1. 这不是完全脱离 DJI Studio 的重实现

当前这版项目更准确的定位是：
- **把 DJI Studio 官方导出链封装成一个完整工程**

它已经尽量减少了对“完整程序手工操作”的依赖，但真正执行 stitching/export 时，仍然依赖 DJI Studio 的私有实现。

### 2. `vendor/` 的作用

`vendor/` 用来保存官方组件快照，方便：
- 固定研究对象
- 对比版本差异
- 降低“全都指向 `/Applications`”的耦合

但要注意：
- 即使快照进了 `vendor/`，也不代表现在就能完全脱离官方 app 独立运行

### 3. 当前最合理的工程方向

- `vendor/` 仍然是最稳定的官方 oracle
- `runtime_candidate/` 现在已经从“可启动”推进到了“可真实高质量导出”
- `runtime_candidate/` 现在也支持后台隐藏启动，不需要把主窗口保持在前台
- NativeApp / 文件级导出工作流现在支持真正的“停止导出”：
  - 会回收当前 compose 任务
  - 会删除部分输出文件
  - 会清理临时 live 项目
- 运行中停止当前已完成 3 样本回归，验证的不是“queued stop”，而是任务实际进入 `state=1` 后的中断清理
- 下一步重点不再是“让它能导出”，而是：
  - 扩大 `runtime_candidate` 的素材回归范围
  - 再决定是否继续做更细粒度的 runtime 裁剪

## 当前状态文档

- runtime 验证状态：
  - [docs/RUNTIME_VALIDATION_STATUS.md](/Users/gordonyoung/Desktop/Projects/DJIStudio/docs/RUNTIME_VALIDATION_STATUS.md)
  - 当前已验证 `runtime_candidate` 默认构建可完成真实高质量导出
- 导出质量状态：
  - [docs/QUALITY_STATUS.md](/Users/gordonyoung/Desktop/Projects/DJIStudio/docs/QUALITY_STATUS.md)
  - 当前已验证 `vendor` 模式下自动导出可对齐手动“质量优先 + 高码率”

## 推荐命令

健康检查：

```bash
./bin/dji-healthcheck
```

8K 导出：

```bash
./bin/dji-8k /path/to/input_dir /path/to/output_dir
```

官方组件快照：

```bash
python3 ./scripts/snapshot_official_components.py
```

整包快照：

```bash
python3 ./scripts/snapshot_official_components.py --include-app-bundle
```

runtime 候选验证：

```bash
python3 ./scripts/validate_runtime_candidate.py
python3 ./scripts/dji_studio_validate_runtime_export.py
```

运行中停止回归：

```bash
python3 ./scripts/dji_studio_stop_regression.py \
  /path/to/a.OSV /path/to/b.OSV \
  --output-root ./output/stop_regression \
  --summary ./output/stop_regression_summary.json
```

后台隐藏启动的单项目导出：

```bash
python3 ./scripts/dji_studio_batch_internal_export.py \
  "/Users/gordonyoung/Library/Application Support/DJI Studio/project/67" \
  --output-dir ./output/hidden_export \
  --resolution-type 14 \
  --launch-if-needed
```

说明：
- 默认会在需要时自动拉起 `runtime_candidate`
- 启动后会立即隐藏进程，而不是让窗口保持在前台
- 如需回到可见启动，额外传 `--foreground-launch`
