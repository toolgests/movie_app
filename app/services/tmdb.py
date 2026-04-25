# import httpx
# from app.core.config import TMDB_TOKEN

# headers = {
#     "Authorization": f"Bearer {TMDB_TOKEN}"
# }

# BASE_URL = "https://api.themoviedb.org/3"


# async def fetch_movies(endpoint, page=1):
#     url = f"{BASE_URL}/movie/{endpoint}?page={page}"

#     async with httpx.AsyncClient() as client:
#         res = await client.get(url, headers=headers)

#     return res.json()
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
import httpx
import json

from app.services.cache import set_cache

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNGE2NTNkZDdjOTE2MjgwMTg0NTNiZWRjMDBhOWI2ZCIsIm5iZiI6MTc3NDQ0NzAyNC4wNzgsInN1YiI6IjY5YzNlOWIwZTAzYzY2OTliOTZhYzQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LpUiFi1j_JrtP8AuuuXxGigR3YMSzNlTDZmNH14_ZB8"  # यहाँ अपना token डालो

headers = {
    "Authorization": f"Bearer {TMDB_TOKEN}"
}

BASE_URL = "https://api.themoviedb.org/3/movie/popular"


async def fetch_page(client, page):
    url = f"{BASE_URL}?page={page}"
    res = await client.get(url)
    return res.json().get("results", [])


# 🔥 THIS FUNCTION WILL RUN EVERY 42 HOURS
async def refresh_movies_cache():
    print("⏳ Refreshing movie cache...")

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

    # save cache
    set_cache("movies_home", json.dumps(final_data), 3600 * 42)

    print("✅ Cache updated!")


# def start_scheduler():
#     scheduler = AsyncIOScheduler()

#     # ⏰ every 42 hours
#     scheduler.add_job(refresh_movies_cache, "interval", hours=42)

#     scheduler.start()
def start_scheduler():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(refresh_movies_cache, "interval", hours=42)

    scheduler.start()

    # ✅ RUN IMMEDIATELY
    asyncio.create_task(refresh_movies_cache())
