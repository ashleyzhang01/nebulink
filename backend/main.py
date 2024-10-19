from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import auth, github, linkedin, network
from app.db.database import create_tables
from app.core.config import settings

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(github.router, prefix=settings.API_V1_STR)
app.include_router(linkedin.router, prefix=settings.API_V1_STR)
app.include_router(network.router, prefix=settings.API_V1_STR)


@app.on_event("startup")
async def startup_event():
    create_tables()


@app.get("/")
def read_root():
    return {"Hello": "World"}
