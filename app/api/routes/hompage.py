from fastapi import APIRouter
from app.services.cache import get_cache, set_cache
import json
import random
from datetime import datetime   # ✅ IMPORTANT

router = APIRouter()


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
        key=lambda x: x.get("popularity", 0) or 0,
        reverse=True
    )[:10]

    used_ids.update(m.get("id") for m in top_today)

    # 🔥 Hot Now
    hot_now = sorted(
        [m for m in movies if m.get("id") not in used_ids],
        key=lambda x: (
            x.get("vote_average", 0) or 0,
            x.get("vote_count", 0) or 0
        ),
        reverse=True
    )[:10]

    used_ids.update(m.get("id") for m in hot_now)

    # ✨ Fresh Releases (SAFE VERSION)
    def parse_date(movie):
        date_str = movie.get("release_date")

        if not date_str:
            return datetime(1900, 1, 1)

        try:
            return datetime.strptime(date_str, "%Y-%m-%d")
        except Exception:
            return datetime(1900, 1, 1)

    fresh_candidates = [
        m for m in movies
        if m.get("id") not in used_ids
    ]

    fresh = sorted(
        fresh_candidates,
        key=parse_date,
        reverse=True
    )[:10]

    used_ids.update(m.get("id") for m in fresh)

    # ⭐ Pop Original
    pop_original = sorted(
        [m for m in movies if m.get("id") not in used_ids],
        key=lambda x: (
            x.get("popularity", 0) or 0,
            x.get("vote_average", 0) or 0
        ),
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

    # 🎯 IMAGE BASES
    IMAGE_TOP = "https://image.tmdb.org/t/p/original"
    IMAGE_HOT = "https://image.tmdb.org/t/p/w780"
    IMAGE_FRESH = "https://image.tmdb.org/t/p/w500"

    # 🎯 Banner Builder
    def build_banner(source_list, image_base, limit=5):
        movies_list = []
        banner_image = None

        for m in source_list:
            path = m.get("backdrop_path") or m.get("poster_path")
            if not path:
                continue

            # set banner image only once (first valid movie)
            if not banner_image:
                banner_image = image_base + path

            movies_list.append(m)

            if len(movies_list) == limit:
                break

        # return in your required format
        return {
            "image": banner_image,
            "movies": movies_list
        }


    banner1 = build_banner(top_today, IMAGE_TOP)
    banner2 = build_banner(hot_now, IMAGE_HOT)
    banner3 = build_banner(fresh, IMAGE_FRESH)

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
