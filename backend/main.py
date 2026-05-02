from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from routes import chat_router, skin_router, status_router


settings = get_settings()
app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(status_router)
app.include_router(skin_router)
app.include_router(chat_router)


@app.get("/")
async def root() -> dict:
    return {"message": f"{settings.app_name} backend is running"}
