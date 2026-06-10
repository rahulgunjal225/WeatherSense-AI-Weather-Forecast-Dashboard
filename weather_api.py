

import requests
from datetime import datetime, timezone

BASE_URL = "https://api.openweathermap.org/data/2.5"
GEO_URL = "http://api.openweathermap.org/geo/1.0"


def get_current_weather(city: str, api_key: str) -> dict | None:
    """Fetch current weather data for a given city."""
    try:
        url = f"{BASE_URL}/weather"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key. Please check your OpenWeatherMap API key.")
        elif e.response.status_code == 404:
            raise ValueError(f"City '{city}' not found. Please check the city name.")
        else:
            raise ValueError(f"API error: {e.response.status_code}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Network error. Please check your internet connection.")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out. Please try again.")


def get_forecast(city: str, api_key: str) -> dict | None:
    """Fetch 5-day / 3-hour forecast for a given city."""
    try:
        url = f"{BASE_URL}/forecast"
        params = {
            "q": city,
            "appid": api_key,
            "units": "metric",
        }
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        if e.response.status_code == 401:
            raise ValueError("Invalid API key. Please check your OpenWeatherMap API key.")
        elif e.response.status_code == 404:
            raise ValueError(f"City '{city}' not found.")
        else:
            raise ValueError(f"API error: {e.response.status_code}")
    except requests.exceptions.ConnectionError:
        raise ConnectionError("Network error. Please check your internet connection.")
    except requests.exceptions.Timeout:
        raise TimeoutError("Request timed out. Please try again.")


def parse_current_weather(data: dict) -> dict:
    """Parse raw API response into a clean dict."""
    sunrise_ts = data["sys"]["sunrise"]
    sunset_ts = data["sys"]["sunset"]
    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temp": round(data["main"]["temp"], 1),
        "feels_like": round(data["main"]["feels_like"], 1),
        "temp_min": round(data["main"]["temp_min"], 1),
        "temp_max": round(data["main"]["temp_max"], 1),
        "condition": data["weather"][0]["main"],
        "description": data["weather"][0]["description"].title(),
        "icon": data["weather"][0]["icon"],
        "humidity": data["main"]["humidity"],
        "pressure": data["main"]["pressure"],
        "wind_speed": round(data["wind"]["speed"] * 3.6, 1),  # m/s → km/h
        "wind_deg": data["wind"].get("deg", 0),
        "visibility": round(data.get("visibility", 0) / 1000, 1),  # m → km
        "clouds": data["clouds"]["all"],
        "sunrise": datetime.fromtimestamp(sunrise_ts, tz=timezone.utc).strftime("%H:%M"),
        "sunset": datetime.fromtimestamp(sunset_ts, tz=timezone.utc).strftime("%H:%M"),
        "timezone_offset": data["timezone"],
        "timestamp": datetime.fromtimestamp(data["dt"]).strftime("%d %b %Y, %H:%M"),
    }


def parse_forecast(data: dict) -> list[dict]:
    """Parse forecast list into clean records."""
    records = []
    for item in data["list"]:
        records.append({
            "datetime": datetime.fromtimestamp(item["dt"]),
            "date": datetime.fromtimestamp(item["dt"]).strftime("%d %b"),
            "time": datetime.fromtimestamp(item["dt"]).strftime("%H:%M"),
            "temp": round(item["main"]["temp"], 1),
            "feels_like": round(item["main"]["feels_like"], 1),
            "temp_min": round(item["main"]["temp_min"], 1),
            "temp_max": round(item["main"]["temp_max"], 1),
            "condition": item["weather"][0]["main"],
            "description": item["weather"][0]["description"].title(),
            "icon": item["weather"][0]["icon"],
            "humidity": item["main"]["humidity"],
            "pressure": item["main"]["pressure"],
            "wind_speed": round(item["wind"]["speed"] * 3.6, 1),
            "clouds": item["clouds"]["all"],
            "pop": round(item.get("pop", 0) * 100),  # probability of precipitation %
        })
    return records
