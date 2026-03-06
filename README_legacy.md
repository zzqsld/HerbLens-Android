# 中草药本地识别 Android APP（离线）

GitHub 仓库：`https://github.com/zzqsld/HerbLens-Android`
模型来源（开源仓库）：`https://openi.pcl.ac.cn/cubeai-model-zoo/hf_cv_chinese_medicine_classification`

基于你提供的模型仓库 `hf_cv_chinese_medicine_classification`，此项目实现了一个可在安卓手机运行的本地识别 APP：
- 从相册或存储空间选择图片
- 本地 ONNX 推理（不依赖后端）
- 显示识别名称和识别度

支持类别（5类）：
- 百合
- 党参
- 枸杞
- 槐花
- 金银花

## 1. 项目结构

- `app/`：安卓应用代码（Kotlin + ONNX Runtime）
- `scripts/export_to_onnx.py`：把原始 HuggingFace ViT 模型导出成 ONNX
- `scripts/requirements-export.txt`：导出模型所需 Python 依赖

## 2. 模型获取方式（使用开源仓库链接）

本仓库不直接托管大模型文件，模型请从上面的开源仓库来源获取并本地导出。

参考链接：
- OpenI 模型仓库：`https://openi.pcl.ac.cn/cubeai-model-zoo/hf_cv_chinese_medicine_classification`
- HuggingFace 镜像模型：`https://hf-mirror.com/Bazaar/cv_chinese_medicine_classification`

在项目根目录执行导出：

```bash
pip install -r scripts/requirements-export.txt
python scripts/export_to_onnx.py
```

执行后会在本地生成：
- `artifacts/chinese_medicine_vit.onnx`
- `artifacts/labels.json`
- `artifacts/preprocess_config.json`

## 3. 拷贝到安卓 assets

把这三个文件复制到：

- `app/src/main/assets/model/chinese_medicine_vit.onnx`
- `app/src/main/assets/model/labels.json`
- `app/src/main/assets/model/preprocess_config.json`

说明：模型文件为本地生成文件，不建议直接提交到 Git 仓库。

## 4. 在 Android Studio 运行

1. 用 Android Studio 打开项目根目录。
2. 等待 Gradle 同步完成。
3. 连接安卓手机（或启动模拟器）。
4. 点击 Run。

## 5. 使用方式

1. 打开 APP，点击“选择图片”。
2. 从相册或文件管理器选择一张中草药图片。
3. 点击“开始识别”。
4. 页面显示“识别结果 + 识别度(%)”。

## 6. 关键实现说明

- 图片选择：`ActivityResultContracts.OpenDocument`
- 本地推理：`ai.onnxruntime:onnxruntime-android`
- 预处理：`224x224`、RGB、按 `preprocess_config.json` 的 mean/std 归一化
- 输出处理：对 logits 做 softmax，取 Top-1

## 7. 注意事项

- 若你重新训练了模型，请重新执行 `scripts/export_to_onnx.py` 并替换 assets 中三个文件。
- 首次加载模型会稍慢（会将 ONNX 从 assets 拷贝到应用内部目录）。
- 模型版权与使用限制请以原始开源仓库说明为准。
- APK 签名别名（keystore alias）：`herblens`

## 8. 图标裁剪预览工具

如果你觉得图标被拉伸，可使用可视化裁剪工具自己框选保留区域：

```bash
python scripts/icon_cropper.py
```

使用方式：
1. 打开后可直接加载项目根目录下的 `1772753925687.png`（或点击 `Open Image` 选图）。
2. 在左侧图上鼠标拖拽，框选要保留的正方形区域。
3. 右侧会实时预览方形和圆形效果。
4. 点击 `Save Icon`，会覆盖输出到：
	`app/src/main/res/drawable-nodpi/ic_launcher_source.png`
5. 然后重新打包安装：

```bash
./gradlew.bat :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```
