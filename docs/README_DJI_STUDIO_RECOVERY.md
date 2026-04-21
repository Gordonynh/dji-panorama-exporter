# DJI Studio 恢复与排障

这份说明是给“原来能跑，后来突然不能跑”的情况准备的。

最常见场景：
- `DJI Studio` 更新后，脚本突然不能自动启动导出
- 重装 `DJI Studio` 后，内部触发失效
- 导出入口脚本还能跑，但卡在“无法 attach / 无法启动”

## 先跑健康检查

先不要直接猜问题，先跑这个：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_healthcheck.py
```

输出文件：
- [/Users/gordonyoung/Offline-Document/exports/dji_studio_live/healthcheck.json](/Users/gordonyoung/Offline-Document/exports/dji_studio_live/healthcheck.json)

这个检查是无副作用的，不会触发导出。

它会确认：
- `DJI Studio.app` 是否存在
- `DJI Studio` 是否正在运行
- `lldb` 能不能 attach 到 `DJIStudio`
- 关键符号是否还在：
  - `ExportTabViewModel::autoCompose(bool)`
  - `ExportTabViewModel` 构造函数
  - `pc_editor::ComposeManager::startCompose(...)`
- `project/24` 模板是否还在
- `media_db/data.db` 是否正常

## 最常见故障：Studio 更新后不能 attach

症状：
- 内部触发脚本失败
- 健康检查里的 `attach_test.ok = false`

原因：
- `DJI Studio.app` 被恢复成官方签名版本
- 当前 app 没有保留我们用于调试/内部触发的状态

这时通常不是数据库坏了，也不是项目坏了，而是：
- **内部触发链断了**

## 恢复顺序

### 1. 先确认 Studio 本体和支持目录都在

要确认这些路径存在：
- `/Applications/DJI Studio.app`
- `~/Library/Application Support/DJI Studio`
- `~/Library/Application Support/DJI Studio/project/24`

### 2. 先打开一次 DJI Studio

很多检查依赖 app 正在运行。

### 3. 再跑健康检查

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_healthcheck.py
```

重点看：
- `running_pid`
- `attach_test.ok`
- `symbols.ok`

### 4. 如果 attach 失败

优先怀疑：
- `DJI Studio` 更新/重装后签名恢复
- 当前这台机器的调试能力被系统收回

你需要重新把 `DJI Studio` 恢复到我们当前这套可 attach 状态。

实操上，最关键的是：
- `lldb` 能 attach 到运行中的 `DJIStudio`

只要这一步恢复了，内部触发脚本一般就会跟着恢复。

## 如果只是项目不全

症状：
- 脚本能跑
- 但某些源目录素材没有对应 live 项目

直接用：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/recover_test \
  --preset 8k
```

当前默认会走自动补建项目链。

## 验证导出链恢复成功

恢复后建议先跑一小条：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py \
  /Users/gordonyoung/Offline-Document/Avata360 \
  /Users/gordonyoung/Offline-Document/exports/recover_smoke \
  --preset 8k
```

然后再生成报告：

```bash
python3 /Users/gordonyoung/Offline-Document/scripts/dji_studio_report_exports.py \
  /Users/gordonyoung/Offline-Document/exports/recover_smoke
```

## 当前这套链路依赖什么

这套自动导出不是纯数据库方案，它依赖：
- 有效的 DJI Studio live 项目
- 可用的 compose draft 注入
- 进程内内部触发：
  - `ExportTabViewModel::autoCompose(true)`

所以如果以后再出问题，优先级是：
1. 先看 attach
2. 再看关键符号
3. 再看 live 项目模板
4. 最后才看导出任务注入

## 相关文件

- 健康检查脚本：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_healthcheck.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_healthcheck.py)
- 主入口：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export.py)
- 批量导出：
  - [/Users/gordonyoung/Offline-Document/scripts/dji_studio_export_source_dir.py](/Users/gordonyoung/Offline-Document/scripts/dji_studio_export_source_dir.py)
- 主说明：
  - [/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_EXPORT.md](/Users/gordonyoung/Offline-Document/README_DJI_STUDIO_EXPORT.md)
