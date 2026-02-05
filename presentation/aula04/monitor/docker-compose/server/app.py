from fastapi import FastAPI
import logging
import os
from logging.handlers import RotatingFileHandler
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import uvicorn

app = FastAPI()

log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)
log_file_path = os.path.join(log_directory, "app.log")

logger = logging.getLogger("uvicorn.access")

handler = RotatingFileHandler(log_file_path, maxBytes=5*1024*1024, backupCount=2)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.setLevel(logging.INFO)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=JSONResponse)
async def read_root():
    logger.info("Rota raiz '/' acessada")
    return {"message": "Hello, FastAPI!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)