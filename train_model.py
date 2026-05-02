import argparse
import json
import os
import shutil
import zipfile
from pathlib import Path

import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow.keras.applications import VGG16
from tensorflow.keras.callbacks import EarlyStopping, LearningRateScheduler
from tensorflow.keras.layers import BatchNormalization, Dense, Dropout, Flatten, LeakyReLU
from tensorflow.keras.models import Sequential
from tensorflow.keras.optimizers import Adam


ROOT = Path(__file__).resolve().parent
DATASET_SLUG = "subirbiswas19/skin-disease-dataset"
DATA_DIR = ROOT / "data"
ZIP_PATH = DATA_DIR / "skin-disease-dataset.zip"
EXTRACT_DIR = DATA_DIR / "skin-disease-dataset"
MODEL_DIR = ROOT / "models"
MODEL_PATH = MODEL_DIR / "skin_disease_vgg16.keras"
CLASS_NAMES_PATH = MODEL_DIR / "class_names.json"
PLOTS_DIR = ROOT / "reports"
IMAGE_SIZE = (256, 256)
BATCH_SIZE = 32


def setup_kaggle_credentials() -> None:
    source = ROOT / "kaggle.json"
    target_dir = Path.home() / ".kaggle"
    target = target_dir / "kaggle.json"

    if target.exists():
        return
    if not source.exists():
        raise FileNotFoundError(
            "Kaggle credentials not found. Put kaggle.json in the project root "
            "or create ~/.kaggle/kaggle.json before running this script."
        )

    target_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    try:
        target.chmod(0o600)
    except OSError:
        pass


def download_dataset(force: bool = False) -> None:
    setup_kaggle_credentials()
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if ZIP_PATH.exists() and not force:
        print(f"Using existing dataset archive: {ZIP_PATH}")
        return

    try:
        from kaggle.api.kaggle_api_extended import KaggleApi
    except ImportError as exc:
        raise ImportError("Install kaggle first: pip install kaggle") from exc

    api = KaggleApi()
    api.authenticate()
    api.dataset_download_files(DATASET_SLUG, path=str(DATA_DIR), unzip=False, force=force)


def extract_dataset(force: bool = False) -> None:
    if EXTRACT_DIR.exists() and any(EXTRACT_DIR.iterdir()) and not force:
        print(f"Using existing extracted dataset: {EXTRACT_DIR}")
        return

    if not ZIP_PATH.exists():
        raise FileNotFoundError(f"Dataset archive not found: {ZIP_PATH}")

    EXTRACT_DIR.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(ZIP_PATH, "r") as zip_ref:
        zip_ref.extractall(EXTRACT_DIR)


def find_dataset_split(root: Path, split_names: tuple[str, ...]) -> Path:
    candidates = []
    for path in root.rglob("*"):
        if path.is_dir() and path.name.lower() in split_names:
            class_dirs = [child for child in path.iterdir() if child.is_dir()]
            if class_dirs:
                candidates.append(path)

    if not candidates:
        names = ", ".join(split_names)
        raise FileNotFoundError(f"Could not find a dataset split named one of: {names}")

    return sorted(candidates, key=lambda item: len(item.parts))[0]


def load_datasets(train_dir: Path, validation_dir: Path):
    train_ds = tf.keras.utils.image_dataset_from_directory(
        train_dir,
        labels="inferred",
        label_mode="int",
        batch_size=BATCH_SIZE,
        image_size=IMAGE_SIZE,
        shuffle=True,
    )

    validation_ds = tf.keras.utils.image_dataset_from_directory(
        validation_dir,
        labels="inferred",
        label_mode="int",
        batch_size=BATCH_SIZE,
        image_size=IMAGE_SIZE,
        shuffle=False,
    )

    class_names = train_ds.class_names
    autotune = tf.data.AUTOTUNE
    train_ds = train_ds.prefetch(buffer_size=autotune)
    validation_ds = validation_ds.prefetch(buffer_size=autotune)
    return train_ds, validation_ds, class_names


def build_model(num_classes: int) -> tf.keras.Model:
    vgg16_base = VGG16(weights="imagenet", include_top=False, input_shape=(256, 256, 3))
    vgg16_base.trainable = False

    model = Sequential(
        [
            tf.keras.layers.Rescaling(1.0 / 255, input_shape=(256, 256, 3)),
            vgg16_base,
            Flatten(),
            Dense(512),
            BatchNormalization(),
            LeakyReLU(),
            Dropout(0.5),
            Dense(256),
            BatchNormalization(),
            LeakyReLU(),
            Dropout(0.5),
            Dense(num_classes, activation="softmax"),
        ]
    )

    model.compile(
        optimizer=Adam(learning_rate=0.001),
        loss="sparse_categorical_crossentropy",
        metrics=["accuracy"],
    )
    return model


def scheduler(epoch: int, lr: float) -> float:
    if epoch < 10:
        return lr
    return float(lr * tf.math.exp(-0.1).numpy())


def save_training_plots(history) -> None:
    PLOTS_DIR.mkdir(parents=True, exist_ok=True)

    plt.figure()
    plt.plot(history.history["accuracy"])
    plt.plot(history.history["val_accuracy"])
    plt.title("Model Accuracy")
    plt.xlabel("Epoch")
    plt.ylabel("Accuracy")
    plt.legend(["Train", "Validation"], loc="upper left")
    plt.savefig(PLOTS_DIR / "accuracy.png", bbox_inches="tight")
    plt.close()

    plt.figure()
    plt.plot(history.history["loss"])
    plt.plot(history.history["val_loss"])
    plt.title("Model Loss")
    plt.xlabel("Epoch")
    plt.ylabel("Loss")
    plt.legend(["Train", "Validation"], loc="upper left")
    plt.savefig(PLOTS_DIR / "loss.png", bbox_inches="tight")
    plt.close()


def train(args: argparse.Namespace) -> None:
    if not args.skip_download:
        download_dataset(force=args.force)
    extract_dataset(force=args.force)

    train_dir = Path(args.train_dir) if args.train_dir else find_dataset_split(EXTRACT_DIR, ("train", "train_set"))
    validation_dir = (
        Path(args.validation_dir)
        if args.validation_dir
        else find_dataset_split(EXTRACT_DIR, ("test", "test_set", "validation", "valid", "val"))
    )

    print(f"Training data: {train_dir}")
    print(f"Validation data: {validation_dir}")

    train_ds, validation_ds, class_names = load_datasets(train_dir, validation_dir)
    model = build_model(num_classes=len(class_names))

    callbacks = [
        EarlyStopping(monitor="val_loss", patience=5, restore_best_weights=True),
        LearningRateScheduler(scheduler),
    ]

    history = model.fit(
        train_ds,
        epochs=args.epochs,
        validation_data=validation_ds,
        callbacks=callbacks,
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    model.save(MODEL_PATH)
    CLASS_NAMES_PATH.write_text(json.dumps(class_names, indent=2), encoding="utf-8")
    save_training_plots(history)

    print(f"Saved model: {MODEL_PATH}")
    print(f"Saved classes: {CLASS_NAMES_PATH}")
    print(f"Saved plots: {PLOTS_DIR}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the Harmony AI skin disease classifier.")
    parser.add_argument("--epochs", type=int, default=int(os.getenv("EPOCHS", "1")))
    parser.add_argument("--skip-download", action="store_true", help="Use an existing dataset zip/extract.")
    parser.add_argument("--force", action="store_true", help="Redownload and re-extract the dataset.")
    parser.add_argument("--train-dir", type=str, default=None, help="Optional explicit train folder.")
    parser.add_argument("--validation-dir", type=str, default=None, help="Optional explicit validation/test folder.")
    return parser.parse_args()


if __name__ == "__main__":
    train(parse_args())
