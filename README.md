# Harmony AI - Virtual Intelligence

Production-ready full-stack healthcare AI application with:

- FastAPI backend
- React + Tailwind frontend (Vite)
- Modular chatbot providers (Azure OpenAI / OpenAI / Gemini / Mock)
- Skin disease prediction using pretrained VGG19 `.h5` model

## Project Structure

```text
backend/
  main.py
  config.py
  routes/
  services/
  models/
  utils/
  model/
  .env
  .env.example
  requirements.txt

frontend/
  src/
  .env
  .env.example
```

## Environment Files

Environment files are created in:

- `backend/.env`
- `backend/.env.example`
- `frontend/.env`
- `frontend/.env.example`

Do not commit real secrets. Keep API keys only in local `.env`.

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Place your pretrained model at:

`backend/model/vgg19_skin_model.h5`

Then run backend:

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Backend APIs

- `GET /status`
- `POST /predict-skin` (multipart image upload)
- `POST /chat` (mental wellness topics only)

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

Frontend runs at:

`http://localhost:5173`

## Chat Provider Configuration

In `backend/.env`, set:

- `CHAT_PROVIDER=azure_openai` (default)
- or `openai`, `gemini`, `mock`

For Azure OpenAI, configure:

- `AZURE_OPENAI_ENDPOINT`
- `AZURE_OPENAI_API_VERSION`
- `AZURE_OPENAI_DEPLOYMENT`
- `AZURE_OPENAI_API_KEY`

## Important Notes

- Backend rejects unrelated chatbot topics and returns a polite refusal.
- Self-harm intent triggers emergency-support response.
- All configuration values are env-driven (no hardcoded runtime secrets/paths/ports).
- This project is not a substitute for medical diagnosis or clinical mental health treatment.


 python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload