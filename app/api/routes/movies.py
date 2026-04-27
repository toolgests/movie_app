
import datetime
import json
import random

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




# @router.get("/homepage")
# async def homepage():

#     cached = get_cache("movies_home")

#     if not cached:
#         return {"error": "No cached data found"}

#     if isinstance(cached, str):
#         data = json.loads(cached)
#     else:
#         data = cached

#     movies = data.get("results", [])

#     used_ids = set()

#     # 🔝 Top 10 Today
#     top_today = sorted(
#         [m for m in movies if m.get("id") not in used_ids],
#         key=lambda x: x.get("popularity", 0),
#         reverse=True
#     )[:10]

#     used_ids.update(m.get("id") for m in top_today)

#     # 🔥 Hot
#     hot_now = sorted(
#         [m for m in movies if m.get("id") not in used_ids],
#         key=lambda x: (x.get("vote_average", 0), x.get("vote_count", 0)),
#         reverse=True
#     )[:10]

#     used_ids.update(m.get("id") for m in hot_now)

#     # ✨ Fresh
#     from datetime import datetime

#     def parse_date(movie):
#         try:
#             return datetime.strptime(movie.get("release_date", "1900-01-01"), "%Y-%m-%d")
#         except:
#             return datetime(1900, 1, 1)

#     fresh = sorted(
#         [m for m in movies if m.get("id") not in used_ids],
#         key=parse_date,
#         reverse=True
#     )[:10]

#     used_ids.update(m.get("id") for m in fresh)

#     # ⭐ Pop/Original (remaining movies)
#     pop_original = sorted(
#         [m for m in movies if m.get("id") not in used_ids],
#         key=lambda x: (x.get("popularity", 0), x.get("vote_average", 0)),
#         reverse=True
#     )[:10]

#     return {
#         "source": "cache_only",
#         "data": {
#             "top_10_today": top_today,
#             "hot_right_now": hot_now,
#             "fresh_releases": fresh,
#             "pop_original": pop_original
#         }
#     }

@router.get("/homepage")
async def homepage():

    cached = get_cache("movies_home")

    if not cached:
        return {"error": "No cached data found"}

    if isinstance(cached, str):
        data = json.loads(cached)
    else:
        data = cached

    movies = data.get("results", [])

    if not movies:
        return {"error": "No movies available"}

    used_ids = set()

    # 🔝 Top Today
    top_today = sorted(
        [m for m in movies if m.get("id") not in used_ids],
        key=lambda x: x.get("popularity", 0),
        reverse=True
    )[:10]

    used_ids.update(m["id"] for m in top_today)

    # 🔥 Hot Now
    hot_now = sorted(
        [m for m in movies if m.get("id") not in used_ids],
        key=lambda x: (x.get("vote_average", 0), x.get("vote_count", 0)),
        reverse=True
    )[:10]

    used_ids.update(m["id"] for m in hot_now)

    # ✨ Fresh Releases
    def parse_date(movie):
        try:
            return datetime.strptime(movie.get("release_date", "1900-01-01"), "%Y-%m-%d")
        except:
            return datetime(1900, 1, 1)

    fresh = sorted(
        [m for m in movies if m.get("id") not in used_ids],
        key=parse_date,
        reverse=True
    )[:10]

    used_ids.update(m["id"] for m in fresh)

    # ⭐ Pop Original
    pop_original = sorted(
        [m for m in movies if m.get("id") not in used_ids],
        key=lambda x: (x.get("popularity", 0), x.get("vote_average", 0)),
        reverse=True
    )[:10]

    # 🎬 Trailer (24h cache)
    today_key = datetime.now().strftime("%Y-%m-%d")
    trailer_cache = get_cache("daily_trailer")

    if trailer_cache:
        if isinstance(trailer_cache, str):
            trailer_cache = json.loads(trailer_cache)

        if trailer_cache.get("date") == today_key:
            trailer_movie = trailer_cache.get("movie")
        else:
            trailer_movie = random.choice(movies)
            set_cache("daily_trailer", json.dumps({
                "date": today_key,
                "movie": trailer_movie
            }), 86400)
    else:
        trailer_movie = random.choice(movies)
        set_cache("daily_trailer", json.dumps({
            "date": today_key,
            "movie": trailer_movie
        }), 86400)

    # 🎯 IMAGE BASES (DIFFERENT FOR EACH SECTION)
    IMAGE_TOP = "https://image.tmdb.org/t/p/original"  # HD banner
    IMAGE_HOT = "https://image.tmdb.org/t/p/w780"      # medium
    IMAGE_FRESH = "https://image.tmdb.org/t/p/w500"    # smaller

    # 🎯 BANNER BUILDER
    def build_banner(source_list, image_base, limit=5):
        banner = []
        local_used = set()

        for m in source_list:
            if m.get("id") in local_used:
                continue

            # fallback if backdrop missing
            path = m.get("backdrop_path") or m.get("poster_path")
            if not path:
                continue

            banner.append({
                "image": image_base + path,
                "movie": m
            })

            local_used.add(m.get("id"))

            if len(banner) == limit:
                break

        return banner

    # 🎯 BUILD BANNERS
    banner1 = build_banner(top_today, IMAGE_TOP)
    banner2 = build_banner(hot_now, IMAGE_HOT)
    banner3 = build_banner(fresh, IMAGE_FRESH)

    # 🚀 FINAL RESPONSE
    return {
        "source": "cache_only",
        "data": {
            "trailer": trailer_movie,

            "banner_top_today": banner1,
            "banner_hot": banner2,
            "banner_fresh": banner3,

            "top_10_today": top_today,
            "hot_right_now": hot_now,
            "fresh_releases": fresh,
            "pop_original": pop_original
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



def get_daily_trailer(movies):
    today_key = datetime.now().strftime("%Y-%m-%d")

    cached = get_cache("daily_trailer")

    if cached:
        if isinstance(cached, str):
            cached = json.loads(cached)

        # if already today's trailer → return
        if cached.get("date") == today_key:
            return cached.get("movie")

    # 🔥 pick random movie
    movie = random.choice(movies)

    trailer_data = {
        "date": today_key,
        "movie": movie
    }

    # save for 24h
    set_cache("daily_trailer", json.dumps(trailer_data), 86400)

    return movie
