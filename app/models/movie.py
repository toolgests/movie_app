from fastapi import APIRouter
from app.services.tmdb import fetch_movies
from app.services.cache import get_cache, set_cache

router = APIRouter()


@router.get("/movies")
async def get_movies():

    cached = get_cache("movies")
    if cached:
        return cached

    popular = await fetch_movies("popular", 1)
    top = await fetch_movies("top_rated", 1)

    data = {
        "popular": popular["results"],
        "top_rated": top["results"]
    }

    set_cache("movies", data)

    return data
