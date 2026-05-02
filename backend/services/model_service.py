from functools import lru_cache
from io import BytesIO
import json

import numpy as np
import tensorflow as tf
import h5py
from PIL import Image

from config import get_settings
from utils.constants import SKIN_LABEL_CONTEXT


def _sanitize_model_config(raw_config: dict) -> dict:
    """Normalize InputLayer keys for cross-version Keras compatibility."""
    config = json.loads(json.dumps(raw_config))
    for layer in config.get("config", {}).get("layers", []):
        if layer.get("class_name") != "InputLayer":
            continue
        layer_cfg = layer.get("config", {})
        if "batch_shape" in layer_cfg and "batch_input_shape" not in layer_cfg:
            layer_cfg["batch_input_shape"] = layer_cfg.pop("batch_shape")
        layer_cfg.pop("optional", None)
    return config


def _load_h5_with_compat_fallback(model_path: str) -> tf.keras.Model:
    with h5py.File(model_path, "r") as h5_file:
        model_config_attr = h5_file.attrs.get("model_config")
        if model_config_attr is None:
            raise ValueError("Missing model_config in H5 file.")
        if isinstance(model_config_attr, bytes):
            model_config_text = model_config_attr.decode("utf-8")
        else:
            model_config_text = model_config_attr
        model_config = json.loads(model_config_text)

    sanitized = _sanitize_model_config(model_config)
    model = tf.keras.models.model_from_config(sanitized)
    model.load_weights(model_path)
    return model


@lru_cache(maxsize=1)
def load_skin_model() -> tf.keras.Model:
    settings = get_settings()
    model_path = settings.resolved_model_path
    if not model_path.exists():
        raise FileNotFoundError(f"Model not found at: {model_path}")
    if model_path.suffix.lower() in {".h5", ".hdf5"}:
        return _load_h5_with_compat_fallback(str(model_path))
    try:
        return tf.keras.models.load_model(model_path, compile=False)
    except Exception as exc:
        message = str(exc)
        if "Unrecognized keyword arguments" not in message and "InputLayer" not in message:
            raise
        return _load_h5_with_compat_fallback(str(model_path))


def predict_skin_disease(image_bytes: bytes) -> dict:
    settings = get_settings()
    labels = settings.parsed_skin_labels
    if not labels:
        raise ValueError("SKIN_LABELS cannot be empty.")

    model = load_skin_model()
    image = Image.open(BytesIO(image_bytes))
    rgb = image.convert("RGB").resize((settings.model_image_size, settings.model_image_size))
    arr = np.asarray(rgb, dtype=np.float32) / 255.0
    batch = np.expand_dims(arr, axis=0)
    predictions = model.predict(batch, verbose=0)[0]

    top_index = int(np.argmax(predictions))
    label = labels[top_index] if top_index < len(labels) else f"class_{top_index}"
    confidence = float(predictions[top_index])

    meta = SKIN_LABEL_CONTEXT.get(
        label.lower(),
        {
            "description": "The model predicted a possible skin condition from the uploaded image.",
            "recommended_action": "Please consult a qualified dermatologist for confirmation.",
        },
    )

    return {
        "prediction": label,
        "confidence": confidence,
        "description": meta["description"],
        "recommended_action": meta["recommended_action"],
    }
