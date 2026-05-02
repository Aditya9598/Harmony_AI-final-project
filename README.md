# Harmony AI Final Project

Streamlit frontend and VGG16 training pipeline for skin disease image classification.

## Setup

Use Python 3.10, 3.11, or 3.12 for TensorFlow compatibility.

```bash
pip install -r requirements.txt
```

Download your Kaggle API token from Kaggle and place `kaggle.json` in this project root. The training script copies it to `~/.kaggle/kaggle.json` and applies restricted permissions where supported.

## Train the Model

```bash
python train_model.py
```

The script downloads `subirbiswas19/skin-disease-dataset`, extracts it into `data/`, trains a VGG16-based classifier, and saves:

- `models/skin_disease_vgg16.keras`
- `models/class_names.json`
- `reports/accuracy.png`
- `reports/loss.png`

If the dataset is already downloaded, use:

```bash
python train_model.py --skip-download
```

## Run the Streamlit App

```bash
streamlit run app.py
```

Upload an image, click **Submit Prediction**, and the app will show the predicted disease with confidence scores.

This is an academic project demo and should not be used as a medical diagnosis tool.
