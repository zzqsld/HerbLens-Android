# HerbLens-Android

大家好，我是这个项目的作者 `zzqsld`。

这个项目是一个可离线运行的中草药识别 Android APP。你在手机上选一张中草药图片，就能看到识别结果和识别度。

GitHub 项目地址：`https://github.com/zzqsld/HerbLens-Android`

## 项目能做什么

- 从相册或存储空间选择图片
- 本地离线识别（不依赖服务器）
- 显示中草药名称（中文）和识别度
- 支持点击作者链接跳转 GitHub

当前模型类别（5类）：
- 百合
- 党参
- 枸杞
- 槐花
- 金银花

## 一、先准备模型文件

本仓库不直接托管大模型文件，请从开源来源获取并在本地导出。

模型来源：
- OpenI：`https://openi.pcl.ac.cn/cubeai-model-zoo/hf_cv_chinese_medicine_classification`
- HuggingFace 镜像：`https://hf-mirror.com/Bazaar/cv_chinese_medicine_classification`

在项目根目录执行：

```bash
pip install -r scripts/requirements-export.txt
python scripts/export_to_onnx.py
```

导出后会生成：
- `artifacts/chinese_medicine_vit.onnx`
- `artifacts/labels.json`
- `artifacts/preprocess_config.json`

把它们复制到：
- `app/src/main/assets/model/chinese_medicine_vit.onnx`
- `app/src/main/assets/model/labels.json`
- `app/src/main/assets/model/preprocess_config.json`

## 二、在 Android Studio 运行

1. 打开项目目录：`D:\cn-purse`
2. 等待 Gradle 同步完成
3. 连接手机（或启动模拟器）
4. 点击 Run

如果只是想安装包：

```bash
./gradlew.bat :app:assembleDebug
```

APK 路径：
- `app/build/outputs/apk/debug/app-debug.apk`

## 三、APP 使用教程

1. 打开 APP
2. 点击 `选择图片`
3. 从相册或文件管理器选择中草药图片
4. 点击 `开始识别`
5. 查看结果：`识别结果 + 识别度`

## 四、图标调整（可选）

如果图标显示不理想，可以使用我写的可视化裁剪工具：

```bash
python scripts/icon_cropper.py
```

使用步骤：
1. 默认会加载根目录下 `1772753925687.png`
2. 鼠标拖拽选择保留区域
3. 右侧实时看方形/圆形预览
4. 点击 `Save Icon`

输出位置：
- `app/src/main/res/drawable-nodpi/ic_launcher_source.png`

保存后重新打包安装：

```bash
./gradlew.bat :app:assembleDebug
adb install -r app/build/outputs/apk/debug/app-debug.apk
```

## 五、发布签名说明

签名别名（keystore alias）：`herblens`

建议你保管好：
- keystore 文件
- keystore 密码
- alias 和 key 密码

后续更新同一个 APP 必须使用同一套签名信息。

## 六、常见问题

- 识别失败提示 `Config#HARDWARE bitmaps`：
已在代码中修复为软件位图解码，重新安装新版 APK 即可。

- 显示拼音标签（如 `dangshen`）：
已在代码中做了拼音到中文映射，当前会显示中文名（如 `党参`）。

- 安装失败：
先执行 `adb devices` 确认手机已连接并授权 USB 调试。

## 许可证与声明

- 代码许可证以仓库 `LICENSE` 为准。
- 模型版权与使用限制请以原始开源模型仓库说明为准。
