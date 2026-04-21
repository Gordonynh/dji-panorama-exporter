# DJI Studio 迁移说明

这份说明是给“把这套工具迁到另一台 Mac”准备的。

目标不是完整迁移整个工作目录，而是尽快恢复这条能力：
- `OSV -> DJI 官方全景 MP4`

## 迁移前提

新机器需要满足：
- macOS
- 已安装 `DJI Studio.app`
- 能正常打开一次 `DJI Studio`

## 建议一起带走的内容

### 1. 独立工具包

优先带走这个：
- [/Users/gordonyoung/Offline-Document/deliverables/dji_studio_toolkit_bundle.zip](/Users/gordonyoung/Offline-Document/deliverables/dji_studio_toolkit_bundle.zip)

### 2. 源素材

如果要直接复跑，需要带走源目录：
- `/path/to/your/OSV_dir`

### 3. 如果你想复用现有 live 项目

可额外备份：
- `~/Library/Application Support/DJI Studio/project`
- `~/Library/Application Support/DJI Studio/media_db`
- `~/Library/Application Support/DJI Studio/setting.ini`

但要注意：
- live 项目不是必须迁移
- 这套脚本本身支持按 `project/24` 风格自动补建缺失项目

所以更稳的策略通常是：
- 带走工具包
- 带走源素材
- 在新机器上重新生成 live 项目

## 新机器最小恢复步骤

### 1. 安装 DJI Studio

确保这个路径存在：
- `/Applications/DJI Studio.app`

### 2. 先手动打开一次 DJI Studio

这是为了让这些目录初始化出来：
- `~/Library/Application Support/DJI Studio`
- `~/Library/Application Support/DJI Studio/project`
- `~/Library/Application Support/DJI Studio/media_db`

### 3. 解压工具包

把下面这个包解压到你希望放置的位置：
- `dji_studio_toolkit_bundle.zip`

### 4. 先跑健康检查

```bash
./bin/dji-healthcheck
```

如果这一步不通过，不要先跑整批导出。

### 5. 先用一小条做冒烟验证

```bash
./bin/dji-8k /path/to/input_dir /path/to/output_dir
```

或者：

```bash
./bin/dji-pipeline-8k /path/to/input_dir /path/to/output_dir --prefix smoke_test
```

## 最关键的风险点

### 1. `DJI Studio` 可 attach 状态

这套链不是纯静态文件方案。  
它依赖内部触发：
- `ExportTabViewModel::autoCompose(true)`

所以如果新机器上：
- `lldb` 不能 attach 到 `DJIStudio`

那自动启动导出这一步就会失效。

这种情况下，先看：
- `README_DJI_STUDIO_RECOVERY.md`

### 2. `project/24` 模板

自动补建 live 项目依赖：
- `~/Library/Application Support/DJI Studio/project/24`

如果新机器没有这个项目，通常说明：
- 你还没走过一次正常导入链
- 或者支持目录还没初始化完整

### 3. Studio 版本差异

如果新机器上的 `DJI Studio` 版本和当前验证环境差别很大，优先检查：
- 健康检查是否通过
- 关键符号是否还在
- 6K/8K profile patch 是否仍生效

## 推荐迁移顺序

1. 安装 `DJI Studio`
2. 打开一次 `DJI Studio`
3. 解压工具包
4. 运行 `./bin/dji-healthcheck`
5. 跑一条小样本
6. 再跑整批

## 相关文档

- 主说明：[README_DJI_STUDIO_EXPORT.md](/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_EXPORT.md)
- 恢复说明：[README_DJI_STUDIO_RECOVERY.md](/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_RECOVERY.md)
- 最终交付摘要：[FINAL_DJI_STUDIO_DELIVERY.md](/Users/gordonyoung/Offline-Document/FINAL_DJI_STUDIO_DELIVERY.md)
