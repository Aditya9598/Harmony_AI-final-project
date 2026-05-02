import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import tensorflow as tf
from PIL import Image


@dataclass(frozen=True)
class PredictionResult:
    label: str
    confidence: float
    top_predictions: list[tuple[str, float]]


def load_prediction_model(model_path: Path) -> tf.keras.Model:
    if not model_path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")
    return tf.keras.models.load_model(model_path)


def load_class_names(class_names_path: Path) -> list[str]:
    if not class_names_path.exists():
        raise FileNotFoundError(f"Class names file not found: {class_names_path}")
    return json.loads(class_names_path.read_text(encoding="utf-8"))


def preprocess_image(image: Image.Image, image_size: tuple[int, int] = (256, 256)) -> np.ndarray:
    image = image.convert("RGB").resize(image_size)
    array = np.asarray(image, dtype=np.float32)
    return np.expand_dims(array, axis=0)


def predict_pil_image(
    model: tf.keras.Model,
    image: Image.Image,
    class_names: list[str],
    image_size: tuple[int, int] = (256, 256),
    top_k: int = 5,
) -> PredictionResult:
    batch = preprocess_image(image, image_size=image_size)
    raw_prediction = model.predict(batch, verbose=0)
    prediction = np.asarray(raw_prediction, dtype=np.float32)
    prediction = np.squeeze(prediction)
    if prediction.ndim == 0:
        raise ValueError("Model returned a scalar prediction; expected class probabilities.")
    if prediction.ndim > 1:
        prediction = prediction.reshape(-1)
    if prediction.size == 0:
        raise ValueError("Model returned empty predictions.")

    # Guard against mismatched model outputs/class_names and keep class index <= 8.
    num_classes = int(prediction.shape[0])
    max_allowed_index = min(8, num_classes - 1)
    valid_indices = [idx for idx in range(num_classes) if idx <= max_allowed_index]
    if not valid_indices:
        raise ValueError("Model did not return any valid prediction indices.")

    ranked_indices = sorted(valid_indices, key=lambda idx: float(prediction[idx]), reverse=True)
    top_indices = ranked_indices[:top_k]

    top_predictions = []
    for index in top_indices:
        if index < len(class_names):
            label = class_names[index]
        else:
            label = f"class_{index}"
        top_predictions.append((label, float(prediction[index])))

    best_label, best_confidence = top_predictions[0]

    return PredictionResult(
        label=best_label,
        confidence=best_confidence,
        top_predictions=top_predictions,
    )
