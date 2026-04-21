# Quality Status

## 当前状态

自动导出链在 `vendor` 模式下，已经能够对齐手动高质量导出的关键质量参数。

当前自动链已经对齐：

- 分辨率：`7680x3840`
- 帧率：按素材原始帧率导出，例如 `60 fps` / `50 fps`
- `Main 10`
- `yuv420p10le`
- 高码率
- `降噪-质量优先`
- `BJ_AI` stitching 配置

当前仍未完成：

- 把同样的高质量导出能力迁移到 `runtime_candidate`
- 确认更多素材与更多导出预设下的完全一致性

## 已实现的工具

- 手动导出监听捕获：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_capture_quality_export.py](/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_capture_quality_export.py)
- 手动 / 自动成片对比：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_compare_quality.py](/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_compare_quality.py)
- 自动注入高质量导出配置：
  - [/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_inject_compose_task.py](/Users/gordonyoung/Desktop/Projects/DJIStudio/scripts/dji_studio_inject_compose_task.py)

## 已抓到的真实高质量配置

来源：
- [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/quality_capture_latest.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/quality_capture_latest.json)
- [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/quality_capture/4f6c33684a28954ade37648deb1a6138.proj](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/quality_capture/4f6c33684a28954ade37648deb1a6138.proj)

关键字段：

- `bitrateMap.frameRate = 349733025`
- `colorDepth = 10`
- `denoise = true`
- `denoiseType = "noise_reduction"`
- `function_used = ["NOISE_REDUCTION", "EXPORT_10BIT"]`
- `stitching_list = ["BJ_AI"]`
- `.proj profile.denoiseType = 1`
- `.proj profile.bitrate = 349733025`

## 当前对比样本

旧对比样本（修复前）：
- [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_auto_quality_0039.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_auto_quality_0039.json)

最新对比样本（修复后）：
- [/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_auto_quality_0039_patched.json](/Users/gordonyoung/Desktop/Projects/DJIStudio/output/manual_vs_auto_quality_0039_patched.json)

## 当前结论

对于样本 `DJI_20260403183452_0039_D.OSV`：

- 手动高质量导出：
  - `7680x3840`
  - `60 fps`
  - `Main 10`
  - 视频比特率约 `349.6 Mbps`
  - 文件大小 `1,395,611,195` bytes
- 自动高质量导出：
  - `7680x3840`
  - `60 fps`
  - `Main 10`
  - 视频比特率约 `349.6 Mbps`
  - 文件大小 `1,395,555,530` bytes

两者当前差异：

- 文件大小差 `55,665` bytes
- 视频比特率差约 `13,945 bps`

这说明当前 `vendor` 模式下的自动导出链，已经能够非常接近地复用手动“质量优先 + 高码率”的实际配置。
