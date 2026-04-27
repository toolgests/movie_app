# # from app.api.routes.hompage import homepage
# from app.services.tmdb import start_scheduler
# from fastapi import FastAPI
# from app.api.routes import movies, details, homepage
# from fastapi.middleware.cors import CORSMiddleware

# app = FastAPI()

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],      # allow all origins (for now)
#     allow_credentials=True,
#     allow_methods=["*"],      # GET, POST, PUT, DELETE etc.
#     allow_headers=["*"],
# )

# app.include_router(movies.router)
# app.include_router(details.router)
# app.include_router(homepage.router)

# @app.on_event("startup")
# async def startup_event():
#     start_scheduler()

# @app.get("/")
# def home():
#     return {"status": "running"}

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.services.tmdb import start_scheduler

from app.api.routes.movies import router as movies_router
from app.api.routes.details import router as details_router
from app.api.routes.hompage import router as homepage_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(movies_router)
app.include_router(details_router)
app.include_router(homepage_router)

@app.on_event("startup")
async def startup_event():
    start_scheduler()

@app.get("/")
def home():
    return {"status": "running"}
