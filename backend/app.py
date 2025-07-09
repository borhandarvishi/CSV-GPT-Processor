from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(
    title="GPT CSV Processor",
    description="Process CSV rows dynamically using OpenAI models",
    version="1.0.0"
)

app.include_router(router)
