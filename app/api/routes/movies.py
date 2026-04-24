# from fastapi import APIRouter
# import httpx

# router = APIRouter()

# TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNGE2NTNkZDdjOTE2MjgwMTg0NTNiZWRjMDBhOWI2ZCIsIm5iZiI6MTc3NDQ0NzAyNC4wNzgsInN1YiI6IjY5YzNlOWIwZTAzYzY2OTliOTZhYzQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LpUiFi1j_JrtP8AuuuXxGigR3YMSzNlTDZmNH14_ZB8"  # यहाँ अपना token डालो

# headers = {
#     "Authorization": f"Bearer {TMDB_TOKEN}"
# }

# @router.get("/movies")
# async def get_movies():

#     all_movies = []

#     async with httpx.AsyncClient() as client:

#         for page in range(1, 11):  # 👈 page 1 to 10
#             url = f"https://api.themoviedb.org/3/movie/popular?page={page}"

#             res = await client.get(url, headers=headers)
#             data = res.json()

#             all_movies.extend(data.get("results", []))

#     return {
#         "total_movies": len(all_movies),
#         "results": all_movies
#     }

import json

from app.services.cache import get_cache, set_cache
from fastapi import APIRouter
import httpx
import asyncio

router = APIRouter()

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNGE2NTNkZDdjOTE2MjgwMTg0NTNiZWRjMDBhOWI2ZCIsIm5iZiI6MTc3NDQ0NzAyNC4wNzgsInN1YiI6IjY5YzNlOWIwZTAzYzY2OTliOTZhYzQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LpUiFi1j_JrtP8AuuuXxGigR3YMSzNlTDZmNH14_ZB8"  # यहाँ अपना token डालो

headers = {
    "Authorization": f"Bearer {TMDB_TOKEN}"
}

BASE_URL = "https://api.themoviedb.org/3/movie/popular"


# 🔥 single page fetch with timeout + error handling
async def fetch_page(client, page):
    url = f"{BASE_URL}?page={page}"

    try:
        res = await client.get(url)

        if res.status_code == 200:
            return res.json().get("results", [])
        else:
            return []

    except httpx.ConnectTimeout:
        print(f"Timeout on page {page}")
        return []

    except Exception as e:
        print(f"Error on page {page}: {e}")
        return []

@router.get("/movies")
async def get_movies():

    async with httpx.AsyncClient(headers=headers, timeout=20.0) as client:
        tasks = [fetch_page(client, page) for page in range(1, 11)]
        results = await asyncio.gather(*tasks)

    all_movies = []
    for r in results:
        all_movies.extend(r)

    final_data = {
        "total_movies": len(all_movies),
        "results": all_movies
    }

    # 🔥 SAVE TO CACHE (THIS IS MUST)
    set_cache("movies_home", json.dumps(final_data), expire=3600)

    return {
        "source": "api",
        "data": final_data
    }


# @router.get("/movies")
# async def get_movies():

#     async with httpx.AsyncClient(headers=headers, timeout=20.0) as client:

#         # ⚡ parallel calls (IMPORTANT FIX)
#         tasks = [fetch_page(client, page) for page in range(1, 11)]
#         results = await asyncio.gather(*tasks)

#     # merge data
#     all_movies = []
#     for r in results:
#         all_movies.extend(r)

#     return {
#         "total_movies": len(all_movies),
#         "results": all_movies
#     }
@router.get("/homepage")
async def homepage():

    cached = get_cache("movies_home")

    if not cached:
        return {"error": "No cached data found"}

    # 🔥 FIX HERE
    if isinstance(cached, str):
        data = json.loads(cached)
    else:
        data = cached

    movies = data.get("results", [])

    # 🔝 Top 10 Today
    top_today = sorted(movies, key=lambda x: x.get("popularity", 0), reverse=True)[:10]

    # 🔥 Hot
    hot_now = sorted(
        movies,
        key=lambda x: (x.get("vote_average", 0), x.get("vote_count", 0)),
        reverse=True
    )[:10]

    # ✨ Fresh
    from datetime import datetime

    def parse_date(movie):
        try:
            return datetime.strptime(movie.get("release_date", "1900-01-01"), "%Y-%m-%d")
        except:
            return datetime(1900, 1, 1)

    fresh = sorted(movies, key=parse_date, reverse=True)[:10]

    return {
        "source": "cache_only",
        "data": {
            "top_10_today": top_today,
            "hot_right_now": hot_now,
            "fresh_releases": fresh
        }
    }


@router.get("/movies/all")
async def get_all_movies_from_cache():

    cached = get_cache("movies_home")

    if not cached:
        return {"error": "No cached data found. Call /movies first."}

    # handle both string & dict
    if isinstance(cached, str):
        data = json.loads(cached)
    else:
        data = cached

    return {
        "source": "cache_only",
        "total_movies": data.get("total_movies", 0),
        "results": data.get("results", [])
    }