# from fastapi import APIRouter, HTTPException
# import httpx
# from app.core.config import TMDB_TOKEN

# router = APIRouter()
# TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNGE2NTNkZDdjOTE2MjgwMTg0NTNiZWRjMDBhOWI2ZCIsIm5iZiI6MTc3NDQ0NzAyNC4wNzgsInN1YiI6IjY5YzNlOWIwZTAzYzY2OTliOTZhYzQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LpUiFi1j_JrtP8AuuuXxGigR3YMSzNlTDZmNH14_ZB8"  # यहाँ अपना token डालो

# BASE_URL = "https://api.themoviedb.org/3"

# headers = {
#     "Authorization": f"Bearer {TMDB_TOKEN}",
#     "accept": "application/json"
# }


# @router.get("/movie/{movie_id}")
# async def movie_details(movie_id: int):

#     url = f"{BASE_URL}/movie/{movie_id}"  # 👈 simple API

#     try:
#         async with httpx.AsyncClient(timeout=10.0) as client:
#             res = await client.get(url, headers=headers)

#         # अगर TMDB error दे
#         if res.status_code != 200:
#             raise HTTPException(
#                 status_code=res.status_code,
#                 detail=res.json()
#             )

#         return res.json()

#     except httpx.RequestError:
#         raise HTTPException(
#             status_code=500,
#             detail="TMDB API request failed"
#         )
# from fastapi import APIRouter, HTTPException
# import httpx
# from app.core.config import TMDB_TOKEN
# from app.services.cache import get_cache, set_cache

# router = APIRouter()
# TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNGE2NTNkZDdjOTE2MjgwMTg0NTNiZWRjMDBhOWI2ZCIsIm5iZiI6MTc3NDQ0NzAyNC4wNzgsInN1YiI6IjY5YzNlOWIwZTAzYzY2OTliOTZhYzQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LpUiFi1j_JrtP8AuuuXxGigR3YMSzNlTDZmNH14_ZB8"  # यहाँ अपना token डालो

# BASE_URL = "https://api.themoviedb.org/3"

# headers = {
#     "Authorization": f"Bearer {TMDB_TOKEN}",
#     "accept": "application/json"
# }


# @router.get("/movie/{movie_id}/full")
# async def movie_full(movie_id: int):

#     cache_key = f"movie:{movie_id}"

#     # ✅ 1. Cache check
#     cached = get_cache(cache_key)
#     if cached:
#         return {
#             "source": "cache",
#             "data": cached
#         }

#     try:
#         async with httpx.AsyncClient() as client:

#             # 🔥 parallel calls
#             movie_req = client.get(
#                 f"{BASE_URL}/movie/{movie_id}", headers=headers
#             )
#             video_req = client.get(
#                 f"{BASE_URL}/movie/{movie_id}/videos", headers=headers
#             )

#             movie_res, video_res = await movie_req, await video_req

#         if movie_res.status_code != 200:
#             raise HTTPException(status_code=404, detail="Movie not found")

#         movie_data = movie_res.json()
#         video_data = video_res.json()

#         # ✅ combine data
#         final_data = {
#             **movie_data,
#             "videos": video_data.get("results", [])
#         }

#         # ✅ store in Redis
#         set_cache(cache_key, final_data)

#         return {
#             "source": "api",
#             "data": final_data
#         }

#     except Exception:
#         raise HTTPException(status_code=500, detail="Error fetching data")
from fastapi import APIRouter, HTTPException
import httpx
import asyncio
import json

from app.services.cache import get_cache, set_cache

router = APIRouter()

TMDB_TOKEN = "eyJhbGciOiJIUzI1NiJ9.eyJhdWQiOiJhNGE2NTNkZDdjOTE2MjgwMTg0NTNiZWRjMDBhOWI2ZCIsIm5iZiI6MTc3NDQ0NzAyNC4wNzgsInN1YiI6IjY5YzNlOWIwZTAzYzY2OTliOTZhYzQxNyIsInNjb3BlcyI6WyJhcGlfcmVhZCJdLCJ2ZXJzaW9uIjoxfQ.LpUiFi1j_JrtP8AuuuXxGigR3YMSzNlTDZmNH14_ZB8"  # यहाँ अपना token डालो
BASE_URL = "https://api.themoviedb.org/3"

headers = {
    "Authorization": f"Bearer {TMDB_TOKEN}",
    "accept": "application/json"
}


@router.get("/movie/{movie_id}/full")
async def movie_full(movie_id: int):

    cache_key = f"movie:{movie_id}"

    # ✅ 1. CHECK CACHE
    cached = get_cache(cache_key)

    if cached:
        try:
            data = json.loads(cached)   # if string
        except:
            data = cached              # if already dict

        return {
            "source": "cache",
            "data": data
        }

    # ✅ 2. FETCH FROM API
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:

            movie_res, video_res = await asyncio.gather(
                client.get(f"{BASE_URL}/movie/{movie_id}", headers=headers),
                client.get(f"{BASE_URL}/movie/{movie_id}/videos", headers=headers)
            )

        if movie_res.status_code != 200:
            raise HTTPException(status_code=404, detail="Movie not found")

        movie_data = movie_res.json()
        video_data = video_res.json()

        final_data = {
            **movie_data,
            "videos": video_data.get("results", [])
        }

        # ✅ 3. SAVE CACHE (ALWAYS STRING)
        set_cache(cache_key, json.dumps(final_data))

        return {
            "source": "api",
            "data": final_data
        }

    except Exception as e:
        print("ERROR:", str(e))
        raise HTTPException(status_code=500, detail=str(e))
