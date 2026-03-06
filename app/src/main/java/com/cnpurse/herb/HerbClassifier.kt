package com.cnpurse.herb

import ai.onnxruntime.OnnxTensor
import ai.onnxruntime.OrtEnvironment
import ai.onnxruntime.OrtSession
import android.content.Context
import android.graphics.Bitmap
import org.json.JSONArray
import org.json.JSONObject
import java.io.File
import java.nio.FloatBuffer
import kotlin.math.exp

class HerbClassifier(private val context: Context) {
    private val env: OrtEnvironment = OrtEnvironment.getEnvironment()
    private val session: OrtSession
    private val labels: List<String>
    private val config: PreprocessConfig
    private val labelZhMap: Map<String, String> = mapOf(
        "baihe" to "百合",
        "dangshen" to "党参",
        "gouqi" to "枸杞",
        "huaihua" to "槐花",
        "jinyinhua" to "金银花"
    )

    data class Prediction(val label: String, val confidence: Float)

    data class PreprocessConfig(
        val imageSize: Int,
        val mean: FloatArray,
        val std: FloatArray
    )

    init {
        labels = loadLabels()
        config = loadPreprocessConfig()
        val modelPath = copyAssetToInternalStorage("model/chinese_medicine_vit.onnx")
        session = env.createSession(modelPath, OrtSession.SessionOptions())
    }

    fun predict(bitmap: Bitmap): Prediction {
        val input = preprocess(bitmap, config)
        val shape = longArrayOf(1, 3, config.imageSize.toLong(), config.imageSize.toLong())

        val inputName = session.inputNames.first()
        OnnxTensor.createTensor(env, FloatBuffer.wrap(input), shape).use { tensor ->
            session.run(mapOf(inputName to tensor)).use { output ->
                val logits = (output[0].value as Array<FloatArray>)[0]
                val probs = softmax(logits)
                val bestIndex = probs.indices.maxByOrNull { probs[it] } ?: 0
                val rawLabel = labels.getOrElse(bestIndex) { "未知" }
                val zhLabel = toChineseLabel(rawLabel)
                return Prediction(zhLabel, probs[bestIndex])
            }
        }
    }

    private fun toChineseLabel(rawLabel: String): String {
        val normalized = rawLabel.trim().lowercase()
            .replace(" ", "")
            .replace("_", "")
            .replace("-", "")
        return labelZhMap[normalized] ?: rawLabel
    }

    private fun preprocess(bitmap: Bitmap, cfg: PreprocessConfig): FloatArray {
        val scaled = Bitmap.createScaledBitmap(bitmap, cfg.imageSize, cfg.imageSize, true)
        val pixels = IntArray(cfg.imageSize * cfg.imageSize)
        scaled.getPixels(pixels, 0, cfg.imageSize, 0, 0, cfg.imageSize, cfg.imageSize)

        val output = FloatArray(3 * cfg.imageSize * cfg.imageSize)
        var offsetR = 0
        var offsetG = cfg.imageSize * cfg.imageSize
        var offsetB = 2 * cfg.imageSize * cfg.imageSize

        for (pixel in pixels) {
            val r = ((pixel shr 16) and 0xFF) / 255.0f
            val g = ((pixel shr 8) and 0xFF) / 255.0f
            val b = (pixel and 0xFF) / 255.0f

            output[offsetR++] = (r - cfg.mean[0]) / cfg.std[0]
            output[offsetG++] = (g - cfg.mean[1]) / cfg.std[1]
            output[offsetB++] = (b - cfg.mean[2]) / cfg.std[2]
        }
        return output
    }

    private fun softmax(logits: FloatArray): FloatArray {
        val maxLogit = logits.maxOrNull() ?: 0f
        val exps = FloatArray(logits.size)
        var sum = 0.0f
        for (i in logits.indices) {
            val v = exp((logits[i] - maxLogit).toDouble()).toFloat()
            exps[i] = v
            sum += v
        }
        return FloatArray(logits.size) { i -> exps[i] / sum }
    }

    private fun loadLabels(): List<String> {
        val text = context.assets.open("model/labels.json").bufferedReader().use { it.readText() }
        val array = JSONArray(text)
        return List(array.length()) { i -> array.getString(i) }
    }

    private fun loadPreprocessConfig(): PreprocessConfig {
        val text = context.assets.open("model/preprocess_config.json").bufferedReader().use { it.readText() }
        val json = JSONObject(text)
        val size = json.getInt("size")
        val meanJson = json.getJSONArray("mean")
        val stdJson = json.getJSONArray("std")
        return PreprocessConfig(
            imageSize = size,
            mean = FloatArray(meanJson.length()) { i -> meanJson.getDouble(i).toFloat() },
            std = FloatArray(stdJson.length()) { i -> stdJson.getDouble(i).toFloat() }
        )
    }

    private fun copyAssetToInternalStorage(assetPath: String): String {
        val fileName = assetPath.substringAfterLast('/')
        val outFile = File(context.filesDir, fileName)
        if (!outFile.exists()) {
            context.assets.open(assetPath).use { input ->
                outFile.outputStream().use { output ->
                    input.copyTo(output)
                }
            }
        }
        return outFile.absolutePath
    }
}
