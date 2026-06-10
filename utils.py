
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots


#  Weather icon emoji map 

ICON_MAP = {
    "01d": "☀️", "01n": "🌙",
    "02d": "⛅", "02n": "⛅",
    "03d": "☁️", "03n": "☁️",
    "04d": "☁️", "04n": "☁️",
    "09d": "🌧️", "09n": "🌧️",
    "10d": "🌦️", "10n": "🌧️",
    "11d": "⛈️", "11n": "⛈️",
    "13d": "❄️", "13n": "❄️",
    "50d": "🌫️", "50n": "🌫️",
}

CONDITION_COLORS = {
    "Clear": "#FFB347",
    "Clouds": "#90AFC5",
    "Rain": "#336B87",
    "Drizzle": "#6AAFE6",
    "Thunderstorm": "#4A235A",
    "Snow": "#AED6F1",
    "Mist": "#BDC3C7",
    "Fog": "#BDC3C7",
    "Haze": "#D4B896",
    "Smoke": "#7F8C8D",
    "Dust": "#C4A35A",
    "Sand": "#E2B96F",
    "Ash": "#95A5A6",
    "Squall": "#2C3E50",
    "Tornado": "#922B21",
}


def get_emoji(icon_code: str) -> str:
    return ICON_MAP.get(icon_code, "🌡️")


def get_condition_color(condition: str) -> str:
    return CONDITION_COLORS.get(condition, "#7EC8E3")


def wind_direction(degrees: int) -> str:
    dirs = ["N", "NNE", "NE", "ENE", "E", "ESE", "SE", "SSE",
            "S", "SSW", "SW", "WSW", "W", "WNW", "NW", "NNW"]
    idx = round(degrees / 22.5) % 16
    return dirs[idx]


# AI Insights 

def generate_ai_insights(weather: dict, forecast_df: pd.DataFrame) -> list[dict]:
    """
    Generate rule-based AI weather insights and recommendations.
    Returns a list of {icon, title, message, level} dicts.
    """
    insights = []
    temp = weather["temp"]
    humidity = weather["humidity"]
    wind_speed = weather["wind_speed"]
    condition = weather["condition"]
    visibility = weather["visibility"]
    clouds = weather["clouds"]

    # Check forecast for rain in next 24h
    rain_soon = False
    if not forecast_df.empty:
        next_24h = forecast_df.head(8)
        rain_soon = any(
            c in ["Rain", "Drizzle", "Thunderstorm"]
            for c in next_24h["condition"].values
        )
        max_pop = next_24h["pop"].max()
    else:
        max_pop = 0

    # Temperature-based clothing advice
    if temp >= 35:
        insights.append({
            "icon": "🥵",
            "title": "Extreme Heat Alert",
            "message": "Temperature is dangerously high. Stay indoors between 11 AM–4 PM, drink water every 30 minutes, and wear light, breathable fabrics.",
            "level": "error",
        })
    elif temp >= 28:
        insights.append({
            "icon": "👕",
            "title": "Hot & Humid Weather",
            "message": "Wear light, loose clothing. Stay hydrated throughout the day. Apply sunscreen SPF 50+ if going outside.",
            "level": "warning",
        })
    elif temp >= 20:
        insights.append({
            "icon": "😊",
            "title": "Pleasant Conditions",
            "message": "Great day for outdoor activities! Light clothing recommended. A light layer for evenings would be wise.",
            "level": "success",
        })
    elif temp >= 10:
        insights.append({
            "icon": "🧥",
            "title": "Cool Weather",
            "message": "Wear a jacket or medium-weight layer. Consider gloves in the morning and evening.",
            "level": "info",
        })
    elif temp >= 0:
        insights.append({
            "icon": "🧣",
            "title": "Cold Conditions",
            "message": "Bundle up with a warm coat, scarf, and gloves. Layer your clothing for better insulation.",
            "level": "warning",
        })
    else:
        insights.append({
            "icon": "🥶",
            "title": "Freezing Temperatures",
            "message": "Dress in heavy winter layers. Limit outdoor exposure. Watch for ice on roads and walkways.",
            "level": "error",
        })

    # Rain & precipitation advice
    if condition in ["Thunderstorm"]:
        insights.append({
            "icon": "⚡",
            "title": "Thunderstorm Warning",
            "message": "Avoid outdoor activities. Stay away from tall trees and metal objects. Seek shelter immediately.",
            "level": "error",
        })
    elif condition in ["Rain", "Drizzle"]:
        insights.append({
            "icon": "☂️",
            "title": "Rain Today",
            "message": "Carry an umbrella or waterproof jacket. Allow extra travel time as roads may be slippery.",
            "level": "warning",
        })
    elif rain_soon and max_pop > 50:
        insights.append({
            "icon": "🌂",
            "title": "Rain Expected Soon",
            "message": f"There's a {max_pop}% chance of rain in the next 24 hours. Keep an umbrella handy.",
            "level": "info",
        })

    # Humidity advice
    if humidity >= 80:
        insights.append({
            "icon": "💧",
            "title": "High Humidity",
            "message": "Air feels muggy. Use dehumidifiers indoors, stay cool, and avoid strenuous outdoor exercise.",
            "level": "warning",
        })
    elif humidity <= 20:
        insights.append({
            "icon": "🏜️",
            "title": "Low Humidity",
            "message": "Very dry air — stay hydrated, use a moisturiser, and consider a humidifier indoors.",
            "level": "info",
        })

    # Wind advice
    if wind_speed >= 60:
        insights.append({
            "icon": "🌀",
            "title": "Dangerous Wind Speed",
            "message": "Extremely high winds. Secure loose outdoor objects. Avoid driving high-sided vehicles.",
            "level": "error",
        })
    elif wind_speed >= 30:
        insights.append({
            "icon": "💨",
            "title": "Strong Winds",
            "message": "Hold on to your hat! Secure any loose items outside. Cycling and walking may be difficult.",
            "level": "warning",
        })

    # Visibility advice
    if visibility < 1:
        insights.append({
            "icon": "🌫️",
            "title": "Very Low Visibility",
            "message": "Dense fog or heavy conditions. Use fog lights while driving and travel at reduced speed.",
            "level": "error",
        })
    elif visibility < 3:
        insights.append({
            "icon": "👁️",
            "title": "Reduced Visibility",
            "message": "Visibility is limited. Drive carefully and use headlights. Avoid unfamiliar roads.",
            "level": "warning",
        })

    # Outdoor activity suggestion
    if condition == "Clear" and 15 <= temp <= 28 and wind_speed < 20:
        insights.append({
            "icon": "🏃",
            "title": "Perfect for Outdoors",
            "message": "Ideal conditions for jogging, cycling, or a picnic. Sun protection is still recommended.",
            "level": "success",
        })

    # Snow alert
    if condition == "Snow":
        insights.append({
            "icon": "❄️",
            "title": "Snow Alert",
            "message": "Snowy conditions expected. Wear waterproof boots and warm layers. Drive slowly and allow extra stopping distance.",
            "level": "warning",
        })

    return insights


# Plotly Charts

CHART_COLORS = {
    "temp": "#FF6B6B",
    "feels_like": "#FFA07A",
    "humidity": "#4FC3F7",
    "wind": "#81C784",
    "pressure": "#CE93D8",
    "pop": "#64B5F6",
    "grid": "rgba(255,255,255,0.08)",
    "bg": "rgba(0,0,0,0)",
    "paper": "rgba(0,0,0,0)",
    "font": "#E0E0E0",
}

LAYOUT_BASE = dict(
    paper_bgcolor=CHART_COLORS["paper"],
    plot_bgcolor=CHART_COLORS["bg"],
    font=dict(color=CHART_COLORS["font"], family="Inter, sans-serif", size=12),
    margin=dict(l=10, r=10, t=40, b=10),
    xaxis=dict(gridcolor=CHART_COLORS["grid"], showgrid=True, zeroline=False),
    yaxis=dict(gridcolor=CHART_COLORS["grid"], showgrid=True, zeroline=False),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    hovermode="x unified",
)


def make_temperature_chart(df: pd.DataFrame) -> go.Figure:
    """Temperature & feels-like line chart over the 5-day forecast."""
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["temp"],
        mode="lines+markers",
        name="Temperature (°C)",
        line=dict(color=CHART_COLORS["temp"], width=2.5),
        marker=dict(size=5),
        fill="tozeroy",
        fillcolor="rgba(255,107,107,0.10)",
    ))
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["feels_like"],
        mode="lines",
        name="Feels Like (°C)",
        line=dict(color=CHART_COLORS["feels_like"], width=1.8, dash="dot"),
    ))
    fig.update_layout(
        title="🌡️ Temperature Trend",
        yaxis_title="°C",
        **LAYOUT_BASE
    )
    return fig


def make_humidity_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["datetime"], y=df["humidity"],
        name="Humidity (%)",
        marker=dict(
            color=df["humidity"],
            colorscale="Blues",
            showscale=False,
        ),
    ))
    fig.update_layout(
        title="💧 Humidity Trend",
        yaxis_title="%",
        yaxis_range=[0, 100],
        **LAYOUT_BASE
    )
    return fig


def make_wind_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["wind_speed"],
        mode="lines+markers",
        name="Wind Speed (km/h)",
        line=dict(color=CHART_COLORS["wind"], width=2.5),
        marker=dict(size=5),
        fill="tonexty" if len(df) > 1 else "tozeroy",
        fillcolor="rgba(129,199,132,0.12)",
    ))
    fig.update_layout(
        title="💨 Wind Speed Trend",
        yaxis_title="km/h",
        **LAYOUT_BASE
    )
    return fig


def make_pressure_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["datetime"], y=df["pressure"],
        mode="lines+markers",
        name="Pressure (hPa)",
        line=dict(color=CHART_COLORS["pressure"], width=2.5),
        marker=dict(size=5),
    ))
    # Reference line at standard pressure
    fig.add_hline(
        y=1013.25,
        line_dash="dash",
        line_color="rgba(255,255,255,0.3)",
        annotation_text="Standard (1013 hPa)",
        annotation_font_color="rgba(255,255,255,0.5)",
    )
    fig.update_layout(
        title="🔵 Atmospheric Pressure",
        yaxis_title="hPa",
        **LAYOUT_BASE
    )
    return fig


def make_precip_chart(df: pd.DataFrame) -> go.Figure:
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=df["datetime"], y=df["pop"],
        name="Precipitation Probability (%)",
        marker=dict(
            color=df["pop"],
            colorscale=[[0, "#AED6F1"], [0.5, "#2980B9"], [1, "#1B2EFF"]],
            showscale=False,
        ),
    ))
    fig.update_layout(
        title="🌧️ Precipitation Probability",
        yaxis_title="%",
        yaxis_range=[0, 100],
        **LAYOUT_BASE
    )
    return fig


def get_daily_summary(forecast_df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate 3-hour slots into daily summaries for forecast cards."""
    df = forecast_df.copy()
    df["day"] = df["datetime"].dt.date
    daily = df.groupby("day").agg(
        temp_min=("temp_min", "min"),
        temp_max=("temp_max", "max"),
        condition=("condition", lambda x: x.mode()[0]),
        icon=("icon", lambda x: x.mode()[0]),
        description=("description", lambda x: x.mode()[0]),
        humidity=("humidity", "mean"),
        wind_speed=("wind_speed", "mean"),
        pop=("pop", "max"),
    ).reset_index()
    daily["temp_min"] = daily["temp_min"].round(1)
    daily["temp_max"] = daily["temp_max"].round(1)
    daily["humidity"] = daily["humidity"].round(0).astype(int)
    daily["wind_speed"] = daily["wind_speed"].round(1)
    daily["day_label"] = pd.to_datetime(daily["day"]).dt.strftime("%A, %d %b")
    return daily
