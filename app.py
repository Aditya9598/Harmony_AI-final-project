from pathlib import Path

import streamlit as st
from PIL import Image


ROOT = Path(__file__).resolve().parent
MODEL_PATH = ROOT / "models" / "skin_disease_vgg16.keras"
CLASS_NAMES_PATH = ROOT / "models" / "class_names.json"
IMAGE_SIZE = (256, 256)


st.set_page_config(
    page_title="Harmony AI | Skin Disease Prediction",
    page_icon="H",
    layout="wide",
)


def render_header() -> None:
    st.markdown(
        """
        <style>
            .main-header {
                padding: 2rem 2.25rem;
                border-radius: 8px;
                background: linear-gradient(120deg, rgba(16, 94, 91, 0.95), rgba(19, 122, 100, 0.9));
                color: white;
                margin-bottom: 1.5rem;
            }
            .main-header h1 {
                font-size: 2.2rem;
                margin: 0 0 0.5rem 0;
                letter-spacing: 0;
            }
            .main-header p {
                font-size: 1.05rem;
                margin: 0;
                max-width: 780px;
                color: rgba(255, 255, 255, 0.9);
            }
            .result-panel {
                padding: 1rem 1.25rem;
                border: 1px solid #d6e7e4;
                border-radius: 8px;
                background: #f7fbfa;
            }
            .disclaimer {
                font-size: 0.9rem;
                color: #4b5563;
            }
        </style>
        <div class="main-header">
            <h1>Harmony AI Skin Disease Prediction</h1>
            <p>Upload a skin image, submit it, and the trained VGG16 classifier will return the most likely disease class with confidence scores.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


@st.cache_resource(show_spinner="Loading trained model...")
def cached_model(model_path: str):
    from src.inference import load_prediction_model

    return load_prediction_model(Path(model_path))


@st.cache_data(show_spinner=False)
def cached_class_names(class_names_path: str):
    from src.inference import load_class_names

    return load_class_names(Path(class_names_path))


def show_training_help() -> None:
    st.warning(
        "Trained model not found. Train it first with `python train_model.py`, "
        "or place `skin_disease_vgg16.keras` and `class_names.json` inside the `models` folder."
    )
    with st.expander("Training setup"):
        st.code(
            """
pip install -r requirements.txt

# Put kaggle.json in this project root, then run:
python train_model.py

# Start the frontend:
streamlit run app.py
            """.strip(),
            language="bash",
        )


def main() -> None:
    render_header()

    st.sidebar.header("Model Status")
    st.sidebar.write(f"Image size: `{IMAGE_SIZE[0]} x {IMAGE_SIZE[1]}`")
    st.sidebar.write(f"Model file: `{MODEL_PATH.name}`")

    model_available = MODEL_PATH.exists() and CLASS_NAMES_PATH.exists()
    if not model_available:
        show_training_help()
        return

    try:
        from src.inference import predict_pil_image

        model = cached_model(str(MODEL_PATH))
        class_names = cached_class_names(str(CLASS_NAMES_PATH))
    except Exception as exc:
        st.error(f"Unable to load model files: {exc}")
        show_training_help()
        return

    left, right = st.columns([0.92, 1.08], gap="large")

    with left:
        st.subheader("Upload Image")
        uploaded_file = st.file_uploader(
            "Choose a skin image",
            type=["jpg", "jpeg", "png", "bmp", "webp"],
            label_visibility="collapsed",
        )

        image = None
        if uploaded_file is not None:
            image = Image.open(uploaded_file).convert("RGB")
            st.image(image, caption="Selected image", use_container_width=True)

        submitted = st.button("Submit Prediction", type="primary", disabled=image is None)

    with right:
        st.subheader("Prediction Result")
        if not submitted:
            st.info("Upload an image and click Submit Prediction to see the result.")
        elif image is None:
            st.error("Please upload an image before submitting.")
        else:
            with st.spinner("Analyzing image..."):
                result = predict_pil_image(model, image, class_names, image_size=IMAGE_SIZE)

            st.markdown('<div class="result-panel">', unsafe_allow_html=True)
            st.metric("Predicted Disease", result.label, f"{result.confidence:.2%} confidence")
            st.progress(float(result.confidence))
            st.markdown("</div>", unsafe_allow_html=True)

            st.write("Top confidence scores")
            for label, score in result.top_predictions:
                st.write(f"{label}: {score:.2%}")
                st.progress(float(score))

    st.divider()
    st.markdown(
        '<p class="disclaimer">This app is for academic project demonstration only and is not a medical diagnosis tool. Please consult a qualified clinician for medical concerns.</p>',
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    main()
