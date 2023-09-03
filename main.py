from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.npa import npa

app = FastAPI()
app.include_router(npa)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
)
