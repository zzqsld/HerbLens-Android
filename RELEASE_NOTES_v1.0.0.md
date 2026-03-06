# HerbLens-Android v1.0.0

发布日期：2026-03-06

## 版本亮点

- 支持从相册/存储空间选择图片进行中草药识别
- 本地离线推理（ONNX Runtime），不依赖云端服务
- 识别结果展示为中文药名 + 识别度
- 支持跳转 GitHub 作者链接
- 自定义应用图标，并提供可视化图标裁剪工具

## 支持范围

- 最低 Android 版本：Android 8.0 (API 26)
- 目标版本：Android 16 (API 36)

## 已知说明

- 模型文件不托管在仓库中，需要按 README 本地导出并放入 assets
- 针对 Google Play（Android 15+）的 16KB page size 兼容性，后续版本会继续优化原生库组合

## 下载文件

- `app-release.apk`
- 文件大小：397,975,106 bytes
- SHA256：`5338AE0B23E3CCDF42C4FAD50FF7D3BE26D6E561407CF6495ED78EF15D0CECBA`

## 安装方法

```bash
adb install -r app-release.apk
```

## 模型来源

- OpenI：`https://openi.pcl.ac.cn/cubeai-model-zoo/hf_cv_chinese_medicine_classification`
- HuggingFace 镜像：`https://hf-mirror.com/Bazaar/cv_chinese_medicine_classification`

## 作者

- `zzqsld`
- 项目地址：`https://github.com/zzqsld/HerbLens-Android`
