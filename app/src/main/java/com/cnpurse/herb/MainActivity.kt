package com.cnpurse.herb

import android.graphics.Bitmap
import android.graphics.ImageDecoder
import android.content.Intent
import android.net.Uri
import android.os.Build
import android.os.Bundle
import android.provider.MediaStore
import android.text.SpannableString
import android.text.Spanned
import android.text.method.LinkMovementMethod
import android.text.style.ClickableSpan
import android.text.style.ForegroundColorSpan
import android.text.TextPaint
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.cnpurse.herb.databinding.ActivityMainBinding
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private val githubUrl = "https://github.com/zzqsld/HerbLens-Android"
    private lateinit var binding: ActivityMainBinding
    private var selectedBitmap: Bitmap? = null
    private var classifier: HerbClassifier? = null

    private val pickImageLauncher = registerForActivityResult(ActivityResultContracts.OpenDocument()) { uri: Uri? ->
        if (uri == null) return@registerForActivityResult

        contentResolver.takePersistableUriPermission(
            uri,
            android.content.Intent.FLAG_GRANT_READ_URI_PERMISSION
        )

        val bitmap = decodeBitmap(uri)
        if (bitmap == null) {
            showToast("读取图片失败，请重试")
            return@registerForActivityResult
        }

        selectedBitmap = bitmap
        binding.previewImage.setImageBitmap(bitmap)
        binding.resultText.text = "已选择图片，点击“开始识别”"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.selectImageButton.setOnClickListener {
            pickImageLauncher.launch(arrayOf("image/*"))
        }

        binding.predictButton.setOnClickListener {
            runPrediction()
        }

        setupAuthorLink()

        lifecycleScope.launch(Dispatchers.IO) {
            try {
                classifier = HerbClassifier(applicationContext)
                withContext(Dispatchers.Main) {
                    binding.resultText.text = "模型已就绪，请选择图片开始识别"
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    binding.resultText.text = "模型加载失败：${e.message}\n请先按照 README 导出并放入 ONNX 模型文件"
                }
            }
        }
    }

    private fun runPrediction() {
        val bitmap = selectedBitmap
        val model = classifier
        if (bitmap == null) {
            showToast("请先选择一张图片")
            return
        }
        if (model == null) {
            showToast("模型还未准备好")
            return
        }

        binding.progressBar.visibility = android.view.View.VISIBLE
        binding.predictButton.isEnabled = false

        lifecycleScope.launch(Dispatchers.Default) {
            try {
                val prediction = model.predict(bitmap)
                withContext(Dispatchers.Main) {
                    binding.resultText.text = buildResultMessage(prediction.label, prediction.confidence)
                }
            } catch (e: Exception) {
                withContext(Dispatchers.Main) {
                    binding.resultText.text = "识别失败：${e.message}"
                }
            } finally {
                withContext(Dispatchers.Main) {
                    binding.progressBar.visibility = android.view.View.GONE
                    binding.predictButton.isEnabled = true
                }
            }
        }
    }

    private fun decodeBitmap(uri: Uri): Bitmap? {
        return try {
            if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.P) {
                val source = ImageDecoder.createSource(contentResolver, uri)
                ImageDecoder.decodeBitmap(source) { decoder, _, _ ->
                    // Force software bitmap so getPixels() works during preprocessing.
                    decoder.allocator = ImageDecoder.ALLOCATOR_SOFTWARE
                }
            } else {
                @Suppress("DEPRECATION")
                MediaStore.Images.Media.getBitmap(contentResolver, uri)
            }
        } catch (_: Exception) {
            null
        }
    }

    private fun showToast(msg: String) {
        Toast.makeText(this, msg, Toast.LENGTH_SHORT).show()
    }

    private fun buildResultMessage(label: String, confidence: Float): String {
        val confidencePercent = "%.2f".format(confidence * 100)
        return when {
            confidence < 0.50f -> {
                "未识别到中草药\n最高置信度：${confidencePercent}%"
            }

            confidence < 0.98f -> {
                "这可能是：${label}\n识别度：${confidencePercent}%\n通常置信度低于98%结果不准确。"
            }

            else -> {
                "识别结果：${label}\n识别度：${confidencePercent}%\n结果仅供参考。"
            }
        }
    }

    private fun setupAuthorLink() {
        val full = "作者：zzqsld"
        val clickableName = "zzqsld"
        val start = full.indexOf(clickableName)
        val end = start + clickableName.length
        val spannable = SpannableString(full)

        val linkSpan = object : ClickableSpan() {
            override fun onClick(widget: android.view.View) {
                openGithubRepo()
            }

            override fun updateDrawState(ds: TextPaint) {
                ds.color = android.graphics.Color.parseColor("#1E6BFF")
                ds.isUnderlineText = true
            }
        }

        spannable.setSpan(linkSpan, start, end, Spanned.SPAN_EXCLUSIVE_EXCLUSIVE)
        spannable.setSpan(
            ForegroundColorSpan(android.graphics.Color.parseColor("#1E6BFF")),
            start,
            end,
            Spanned.SPAN_EXCLUSIVE_EXCLUSIVE
        )

        binding.authorLinkText.text = spannable
        binding.authorLinkText.movementMethod = LinkMovementMethod.getInstance()
        binding.authorLinkText.highlightColor = android.graphics.Color.TRANSPARENT
    }

    private fun openGithubRepo() {
        val intent = Intent(Intent.ACTION_VIEW, Uri.parse(githubUrl))
        startActivity(intent)
    }
}
