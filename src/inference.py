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
    prediction = model.predict(batch, verbose=0)[0]

    top_indices = np.argsort(prediction)[::-1][:top_k]
    top_predictions = [(class_names[index], float(prediction[index])) for index in top_indices]
    best_label, best_confidence = top_predictions[0]

    return PredictionResult(
        label=best_label,
        confidence=best_confidence,
        top_predictions=top_predictions,
    )
