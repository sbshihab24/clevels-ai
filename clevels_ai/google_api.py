# clevels_ai/google_api.py
from .config import settings
from .logger import logger
import requests
from urllib.parse import urlencode

def fetch_place_search(query: str, limit: int = 5, language: str = "en"):
    if not settings.GOOGLE_MAPS_API_KEY:
        raise RuntimeError("No Google Maps API key configured")
    url = "https://maps.googleapis.com/maps/api/place/textsearch/json"
    params = {"query": query, "key": settings.GOOGLE_MAPS_API_KEY, "language": language}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    data = r.json()
    results = data.get("results", [])[:limit]
    out = []
    for r0 in results:
        out.append({
            "name": r0.get("name"),
            "formatted_address": r0.get("formatted_address") or r0.get("vicinity"),
            "rating": r0.get("rating"),
            "place_id": r0.get("place_id"),
            "raw": r0
        })
    return out

def static_map_url(lat, lng, zoom=15, size="400x200"):
    if not settings.GOOGLE_MAPS_API_KEY:
        return None
    params = {
        "center": f"{lat},{lng}",
        "zoom": zoom,
        "size": size,
        "key": settings.GOOGLE_MAPS_API_KEY
    }
    return f"https://maps.googleapis.com/maps/api/staticmap?{urlencode(params)}"
