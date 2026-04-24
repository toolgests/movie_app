from app.services.tmdb import start_scheduler
from fastapi import FastAPI
from app.api.routes import movies, details

app = FastAPI()

app.include_router(movies.router)
app.include_router(details.router)

@app.on_event("startup")
async def startup_event():
    start_scheduler()