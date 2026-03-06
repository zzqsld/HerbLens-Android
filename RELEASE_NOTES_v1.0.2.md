# HerbLens-Android v1.0.2

发布日期：2026-03-06

## 更新内容

- 修复 Android 15+ 16KB page size 兼容风险：发布包改为 ABI 分包，不再打入 `x86_64` 原生库
- 继续保留离线中草药识别流程（本地 ONNX 推理）

## 发布文件（位于 `app/release`）

- `app-arm64-v8a-release.apk`
  - SHA256: `1955E4ED5895E57D0FF4D48D4F06F8037689761B5DE0048EC7939853FF8A49C0`
- `app-armeabi-v7a-release.apk`
  - SHA256: `024C29CD1ABA01C432D1697E7DD1EA3DAF9E1754D63407F7B30036D182415729`

## 说明

- 推荐优先使用 `arm64-v8a` 包。
- 模型来源与使用限制请遵循上游仓库说明。
