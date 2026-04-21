# Runtime Validation Status

## 当前状态

- `vendor/DJI Studio.app`
  - 可启动
  - 可真实导出
  - 已验证可对齐手动“质量优先 + 高码率”
- `runtime_candidate/DJI Studio.app`
  - 可启动
  - 可 attach
  - `autoCompose(true)` 可调用
  - 现在也已经能完成真实高质量导出

## 已验证结论

- `Sparkle.framework` 必须保留
- `libsentry.dylib` 必须保留
- `DJIStudioQuickLookHost.app` 不是启动硬依赖，且已验证可从默认 runtime 中移除
- 冷启动时，直接执行 `Contents/MacOS/DJIStudio` 不足以让队列进入可导出状态
- 冷启动时，`open -na <bundle>` 比直接执行二进制更接近正常桌面初始化路径
- 当前默认自动启动策略为：
  - 用 `open -na <bundle>` 启动 `runtime_candidate`
  - 启动后立即通过 `System Events` 将进程隐藏
  - 在保持 `visible=false / frontmost=false` 的情况下继续走内部导出链
- 仅恢复 `sqldrivers` 仍不足以恢复真实导出
- 恢复被裁掉的 Qt 插件组后，`runtime_candidate` 可以稳定进入真实导出
- 进一步单项验证表明：
  - `Contents/PlugIns/DJIStudioQuickLookHost.app` 可移除
  - `Contents/PlugIns/iconengines` 可移除
  - `Contents/PlugIns/networkinformation` 可移除
  - `Contents/PlugIns/geometryloaders` 可移除
  - `Contents/PlugIns/sceneparsers` 可移除
  - `Contents/Resources/resource/dashboard` 可移除
  - `Contents/PlugIns/styles` 可移除
  - `Contents/Resources/tracking` 可移除
  - `Contents/Resources/resource` 可移除
  - `Contents/Resources/filter` 可移除
  - `Contents/PlugIns/renderplugins` 可移除
  - `Contents/PlugIns/renderers` 可移除
  - `Contents/PlugIns/imageformats` 可移除
  - `Contents/PlugIns/multimedia` 可移除
  - `Contents/PlugIns/tls` 可移除
  - `Contents/PlugIns/quick` 当前必须保留
  - `Contents/PlugIns/sqldrivers` 当前必须保留
- 当前 `runtime_candidate` 默认构建策略已经调整为：
  - 移除确认无关的资源文件
  - 移除 `Resources/resource/dashboard`
  - 移除 `Resources/tracking`
  - 移除 `Resources/resource`
  - 移除 `Resources/filter`
  - 移除 `DJIStudioQuickLookHost.app`
  - 移除 `iconengines`
  - 移除 `networkinformation`
  - 移除 `geometryloaders`
  - 移除 `sceneparsers`
  - 移除 `styles`
  - 移除 `renderplugins`
  - 移除 `renderers`
  - 移除 `imageformats`
  - 移除 `multimedia`
  - 移除 `tls`
  - 保留 `quick`
  - 保留 `sqldrivers`

## 当前报告

- 启动验证：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_candidate_validation.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_candidate_validation.json)
- 旧的失败验证（修复前）：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_clean.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_clean.json)
- 最新成功验证（默认 `runtime_candidate` 构建）：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_hq.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_hq.json)
- 手动 vs `runtime_candidate` 高质量对比：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_runtime_candidate_quality_0039.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_runtime_candidate_quality_0039.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_runtime_candidate_quality_0039_default.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_runtime_candidate_quality_0039_default.json)
- 细粒度裁剪第一轮摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage1.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage1.json)
- 细粒度裁剪第二轮摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage2.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage2.json)
- 细粒度裁剪第三轮摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage3.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage3.json)
- 细粒度裁剪第四轮摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage4.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage4.json)
- 细粒度裁剪第五轮摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage5.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage5.json)
- 细粒度裁剪第六轮摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage6.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_prune_probe_summary_stage6.json)
- 新默认裁剪集回归验证：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v3.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v3.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v4.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v4.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v5.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v5.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6_project41.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6_project41.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6_project67.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6_project67.json)
- 多样本回归摘要：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_pruned_v6_regression_summary.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_pruned_v6_regression_summary.json)
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6_project41_preservefps.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/runtime_export_validation_runtime_candidate_pruned_v6_project41_preservefps.json)
- 后台隐藏启动导出验证：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/hidden_batch_test67_manifest.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/hidden_batch_test67_manifest.json)
  - 该验证对应的运行时进程已确认：
    - `visible=false`
    - `frontmost=false`
- 中断回归验证：
  - 早期取消验证：
    - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_v2_manifest.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_v2_manifest.json)
    - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_v2_progress.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_v2_progress.json)
  - `state=1` 运行中取消验证：
    - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_debug_manifest.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_debug_manifest.json)
    - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_debug_progress.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_debug_progress.json)
  - 3 样本 `state=1` 运行中取消回归摘要：
    - [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_multi_v2_summary.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/stop_regression_multi_v2_summary.json)

## 当前结论

对于样本 `DJI_20260403183452_0039_D.OSV`：

- `runtime_candidate` 默认构建可完成 `7680x3840 / 60 fps / Main 10 / yuv420p10le` 导出
- 当前验证成片：
  - 文件大小 `1,395,554,286` bytes
  - 视频比特率约 `349.6 Mbps`
- 与手动高质量导出相比，当前已经达到近似一致的质量档位
- 当前 `runtime_candidate` 体积约 `938,068,126` bytes
- 对 `project/24` 和 `project/67` 的多样本回归已经通过
- 后台隐藏启动下，`project/67` 已验证可完成 `8K / 50fps / Main 10 / 高码率` 导出
- `project/41` 的 `50fps` 保真问题已经修复
  - 根因是旧版注入链优先继承 DJI Studio 当前导出设置里的帧率
  - 现在默认改为优先保留源素材帧率，除非显式要求继承配置
  - 修复后 `DJI_20260329172046_0022_D.OSV` 已按 `50fps` 正常导出
- 停止链当前已经通过两类回归：
  - 任务尚未进入运行态时，停止会清除挂起 compose 任务、删除临时项目，并回收输出目录
  - 任务已经进入 `state=1` 且输出文件正在增长时，停止会：
    - 终止当前 runtime 进程
    - 删除对应 `composeList / exportDataTable` 记录
    - 删除部分输出文件
    - 清理临时 live 项目和 clone 目录
- 3 条不同样本的 `state=1` 中断回归现已全部通过：
  - `DJI_20260329151746_0001_D.OSV`
  - `DJI_20260329172046_0022_D.OSV`
  - `DJI_20260403183452_0039_D.OSV`
  - 三条都在进入 `state=1` 后被中断，且均无 compose 残留、无输出文件残留

## 下一步重点

- 继续确认更多素材在 `runtime_candidate` 下的稳定性
- 再决定是否继续做更细粒度的 runtime 裁剪
- 如果继续裁剪，必须以“真实导出验证”作为准入门槛，而不是只看能否启动
