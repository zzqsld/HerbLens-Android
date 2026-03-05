import json
from pathlib import Path

import torch
from transformers import AutoImageProcessor, ViTForImageClassification

MODEL_ID = "Bazaar/cv_chinese_medicine_classification"
OUT_DIR = Path("artifacts")
ONNX_NAME = "chinese_medicine_vit.onnx"


def main() -> None:
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    processor = AutoImageProcessor.from_pretrained(MODEL_ID)
    model = ViTForImageClassification.from_pretrained(MODEL_ID)
    model.eval()

    size_cfg = processor.size
    image_size = size_cfg.get("height") or size_cfg.get("shortest_edge") or 224

    # ViT ONNX input format: [batch, channels, height, width]
    dummy = torch.randn(1, 3, image_size, image_size)
    onnx_path = OUT_DIR / ONNX_NAME
    torch.onnx.export(
        model,
        (dummy,),
        str(onnx_path),
        input_names=["pixel_values"],
        output_names=["logits"],
        dynamic_axes={"pixel_values": {0: "batch"}, "logits": {0: "batch"}},
        opset_version=17,
        do_constant_folding=True,
    )

    id2label = model.config.id2label
    labels = [id2label[str(i)] if isinstance(id2label, dict) and str(i) in id2label else id2label[i] for i in range(model.config.num_labels)]

    preprocess = {
        "size": int(image_size),
        "mean": [float(x) for x in processor.image_mean],
        "std": [float(x) for x in processor.image_std],
    }

    (OUT_DIR / "labels.json").write_text(json.dumps(labels, ensure_ascii=False, indent=2), encoding="utf-8")
    (OUT_DIR / "preprocess_config.json").write_text(json.dumps(preprocess, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"Export done: {onnx_path.resolve()}")
    print("Generated labels.json and preprocess_config.json in artifacts/")


if __name__ == "__main__":
    main()
