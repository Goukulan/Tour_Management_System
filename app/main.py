from fastapi import FastAPI
from app.constants import messages

from app.api.v1.api_v1 import router as api_v1_router



app = FastAPI(title="Tour Management System")

app.include_router(api_v1_router)

@app.get("/")
def root():
    return {"message": messages.API_RUNNING}