# Runtime Minimization Plan

## 目标

把当前项目内的 `vendor/DJI Studio.app` 从“完整 app 快照”逐步收缩为“最小可运行 runtime”。

注意：
- 这一步的目标不是重写 DJI 私有导出链
- 而是保留必要组件，去掉明显无关的部分

## 当前判断

### 必需层

这些是当前导出链明显直接依赖的：

- `Contents/MacOS/DJIStudio`
- `Contents/Frameworks/DualStitcher.framework`
- `Contents/Frameworks/MKMediaEditor.framework`
- `Contents/Frameworks/libpano_selfcali.dylib`
- `Contents/Frameworks/libMNN.3.1.2.dylib`
- `Contents/Frameworks/libdInfer.dylib`
- `Contents/Frameworks/ml_fis.framework`
- `Contents/Frameworks/openmcv2.framework`
- `Contents/Frameworks/MltNDMac.framework`
- `Contents/Frameworks/nd_filtermac.framework`
- `Contents/Frameworks/MltTonalEnhance.framework`
- `Contents/Frameworks/ToneEnhancement.framework`
- `Contents/Frameworks/MltVfi.framework`
- `Contents/Frameworks/vfi_filter.framework`
- `Contents/Frameworks/libvideo_analysis.dylib`
- `Contents/Resources/Media`
- `Contents/Resources/filter`
- `Contents/Resources/qml`
- `Contents/Resources/qml.enc`
- `Contents/Resources/qml_config.enc`
- `Contents/Resources/qml_controls.enc`
- `Contents/Resources/qt.conf`
- `Contents/Resources/resource`
- `Contents/PlugIns/platforms`
- `Contents/PlugIns/quick`

### 很可能可移除

这些更像外围能力，而不是全景导出最短路径：

- `Contents/Resources/appcast.xml`
- `Contents/Resources/UserGuideVideo.mp4`
- `Contents/Resources/ThirdCopyright.txt`
- `Contents/Resources/filter`
- `Contents/Resources/resource`
- `Contents/Resources/resource/dashboard`
- `Contents/Resources/tracking`
- `Contents/PlugIns/DJIStudioQuickLookHost.app`
- `Contents/PlugIns/iconengines`
- `Contents/PlugIns/networkinformation`
- `Contents/PlugIns/geometryloaders`
- `Contents/PlugIns/sceneparsers`
- `Contents/PlugIns/styles`
- `Contents/PlugIns/renderplugins`
- `Contents/PlugIns/renderers`
- `Contents/PlugIns/imageformats`
- `Contents/PlugIns/multimedia`
- `Contents/PlugIns/tls`

### 需要实验验证

这部分不能先猜删：

- `Contents/Frameworks/Sparkle.framework`
- `Contents/Frameworks/libsentry.dylib`
- `Contents/Frameworks/libPerfMonitorSDK.dylib`
- `Contents/Frameworks/libalibabacloud-oss-cpp-sdk.dylib`
- 全套 `Qt*` frameworks 是否能进一步压缩
- `DJIStudioQuickLookHost.app` 是否仍然需要
- `audiohighlight.framework`
- `libssl.3.dylib`
- `libcrypto.3.dylib`
- `libquazip1-qt6.1.4.0.dylib`
- `libeffect.dylib`
- `libfreetype.6.dylib`
- `libml_vot.dylib`
- `libmac_x86.dylib`
- `Contents/PlugIns/sqldrivers`

## 建议步骤

1. 先复制一份 `runtime_candidate/`
2. 按“很可能可移除”清单做第一轮裁剪
3. 跑健康检查和最小导出冒烟测试
4. 记录缺失依赖，再回补
5. 收敛出第一版 `runtime_min/`

## 当前实验结论

- 删除 `Contents/Frameworks/libsentry.dylib` 后，启动会立刻失败
- 删除 `Contents/Frameworks/Sparkle.framework` 后，启动会立刻失败
- 这说明主程序在 dyld 装载阶段就硬依赖这两项，暂时都必须保留
- 删除 `Contents/PlugIns/DJIStudioQuickLookHost.app` 后，主程序仍可启动到稳定超时阶段
- 这说明 `DJIStudioQuickLookHost.app` 不是启动硬依赖，但是否影响导出仍需单独验证
- 仅“直接执行 `Contents/MacOS/DJIStudio`”不足以可靠启动导出队列
- 通过 `open -na <bundle>` 冷启动完整 `vendor` app 后，再触发内部 `autoCompose(true)`，队列可以开始消费
- 曾经的 `runtime_candidate` 虽然可以启动、可 attach、可命中 `autoCompose(true)`，但不会把新注入任务从 `state=0` 推进到运行态
- 最新实验表明，这个问题与被移除的插件组直接相关
- 仅恢复 `sqldrivers` 不足以恢复真实导出
- 恢复以下插件组后，`runtime_candidate` 可以完成真实高质量导出：
  - `Contents/PlugIns/networkinformation`
  - `Contents/PlugIns/sqldrivers`
  - `Contents/PlugIns/geometryloaders`
  - `Contents/PlugIns/sceneparsers`
  - `Contents/PlugIns/iconengines`
- `Contents/PlugIns/DJIStudioQuickLookHost.app` 删除后，仍可完成真实导出
- `Contents/PlugIns/iconengines` 删除后，仍可完成真实导出
- `Contents/PlugIns/networkinformation` 删除后，仍可完成真实导出
- `Contents/PlugIns/geometryloaders` 删除后，仍可完成真实导出
- `Contents/PlugIns/sceneparsers` 删除后，仍可完成真实导出
- `Contents/Resources/resource/dashboard` 删除后，仍可完成真实导出
- `Contents/Resources/resource` 删除后，仍可完成真实导出
- `Contents/Resources/filter` 删除后，仍可完成真实导出
- `Contents/PlugIns/styles` 删除后，仍可完成真实导出
- `Contents/Resources/tracking` 删除后，仍可完成真实导出
- `Contents/PlugIns/renderplugins` 删除后，仍可完成真实导出
- `Contents/PlugIns/renderers` 删除后，仍可完成真实导出
- `Contents/PlugIns/imageformats` 删除后，仍可完成真实导出
- `Contents/PlugIns/multimedia` 删除后，仍可完成真实导出
- `Contents/PlugIns/tls` 删除后，仍可完成真实导出
- `Contents/PlugIns/quick` 删除后，启动检查和内部触发失败，当前必须保留
- `Contents/PlugIns/sqldrivers` 删除后，任务停留在 `state=0`，当前必须保留
- 当前默认 `build_runtime_candidate.py` 已改为：
  - 保留 `sqldrivers`
  - 保留 `quick`
  - 移除 `DJIStudioQuickLookHost.app / iconengines / networkinformation / geometryloaders / sceneparsers / styles`
  - 移除 `renderplugins / renderers / imageformats / multimedia / tls`
  - 移除 `Contents/Resources/resource / resource/dashboard`
  - 移除 `Contents/Resources/tracking`
  - 移除 `Contents/Resources/filter`
  - 以及三项资源文件


## 最新结论（2026-04-16）

- `runtime_candidate` 现在已经可以在默认构建下完成真实高质量导出
- 当前默认裁剪策略仅移除：
  - `Contents/Resources/appcast.xml`
  - `Contents/Resources/UserGuideVideo.mp4`
  - `Contents/Resources/ThirdCopyright.txt`
- 以及：
  - `Contents/Resources/filter`
  - `Contents/Resources/resource`
  - `Contents/Resources/resource/dashboard`
  - `Contents/Resources/tracking`
  - `Contents/PlugIns/styles`
- 以及：
  - `Contents/PlugIns/DJIStudioQuickLookHost.app`
  - `Contents/PlugIns/iconengines`
- 以及：
  - `Contents/PlugIns/networkinformation`
  - `Contents/PlugIns/geometryloaders`
  - `Contents/PlugIns/sceneparsers`
- 以及：
  - `Contents/PlugIns/renderplugins`
  - `Contents/PlugIns/renderers`
  - `Contents/PlugIns/imageformats`
  - `Contents/PlugIns/multimedia`
  - `Contents/PlugIns/tls`
- 以下插件当前仍视为导出相关，暂不从默认构建里删除：
  - `Contents/PlugIns/quick`
  - `Contents/PlugIns/sqldrivers`
- 后续若继续缩减 runtime，必须逐项恢复/验证，并以真实导出通过为准
- 当前 `runtime_candidate` 体积约 `938,068,126` bytes
