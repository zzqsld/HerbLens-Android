# HerbLens-Android v1.0.1

发布日期：2026-03-06

## 更新内容

- 新增识别结果三档提示逻辑：
  - 置信度 < 50%：提示未识别到中草药
  - 50% <= 置信度 < 98%：提示可能结果，并提示低于 98% 时通常不准确
  - 置信度 >= 98%：展示识别结果，并提示结果仅供参考
- 优化大屏/挖孔屏显示：页面整体下移，减少标题被前摄遮挡的情况
- 保留中文药名显示与识别度展示

## 版本信息

- 包名：`com.cnpurse.herb`
- 最低系统：Android 8.0 (API 26)
- 目标系统：Android 16 (API 36)

## 发布文件

- 文件名：`app-release.apk`
- 文件大小：397,975,154 bytes
- SHA256：`B9C8A59ED78A3C0ED6CFB39C22B34D5884344912C89B321C2CBE0D42B2331387`

## 签名校验

已校验为签名 APK（v2 方案）：
- Signer DN：`C=CN, ST=Jinan, L=Shandong, O=Personal, OU=Android, CN=zzqsld`
- 签名证书 SHA-256：`47fec370c72ebcccc0302ce0099c1e392e5ce920d70a865d6e4394b70beea1b3`

## 模型来源

- OpenI：`https://openi.pcl.ac.cn/cubeai-model-zoo/hf_cv_chinese_medicine_classification`
- HuggingFace 镜像：`https://hf-mirror.com/Bazaar/cv_chinese_medicine_classification`
