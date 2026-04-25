from app.services.tmdb import start_scheduler
from fastapi import FastAPI
from app.api.routes import movies, details
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],      # allow all origins (for now)
    allow_credentials=True,
    allow_methods=["*"],      # GET, POST, PUT, DELETE etc.
    allow_headers=["*"],
)

app.include_router(movies.router)
app.include_router(details.router)

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def home():
    return {"status": "running"}