

import streamlit as st
import pandas as pd
import time
from datetime import datetime

from weather_api import (
    get_current_weather,
    get_forecast,
    parse_current_weather,
    parse_forecast,
)
from utils import (
    get_emoji,
    get_condition_color,
    wind_direction,
    generate_ai_insights,
    get_daily_summary,
    make_temperature_chart,
    make_humidity_chart,
    make_wind_chart,
    make_pressure_chart,
    make_precip_chart,
)

#Page config 

st.set_page_config(
    page_title="WeatherSense – AI Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# CSS Styling 

def load_css(dark_mode: bool):
    if dark_mode:
        bg_gradient = "linear-gradient(135deg, #0d1117 0%, #161b27 50%, #0d1117 100%)"
        card_bg = "rgba(255, 255, 255, 0.05)"
        card_border = "rgba(255, 255, 255, 0.10)"
        card_shadow = "0 8px 32px rgba(0,0,0,0.4)"
        text_primary = "#E8EDF5"
        text_secondary = "#8B9AB0"
        metric_bg = "rgba(255, 255, 255, 0.04)"
        sidebar_bg = "rgba(13, 17, 23, 0.98)"
        input_bg = "rgba(255,255,255,0.07)"
    else:
        bg_gradient = "linear-gradient(135deg, #E8F4FD 0%, #D6EAF8 50%, #EBF5FB 100%)"
        card_bg = "rgba(255, 255, 255, 0.75)"
        card_border = "rgba(255, 255, 255, 0.90)"
        card_shadow = "0 8px 32px rgba(100,149,237,0.15)"
        text_primary = "#1A2940"
        text_secondary = "#4A6080"
        metric_bg = "rgba(100, 149, 237, 0.07)"
        sidebar_bg = "rgba(236, 246, 255, 0.98)"
        input_bg = "rgba(100,149,237,0.08)"

    st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Outfit:wght@300;400;500;600;700&display=swap');

    /* ── Global ── */
    html, body, [class*="css"] {{
        font-family: 'Inter', sans-serif;
    }}
    .stApp {{
        background: {bg_gradient};
        min-height: 100vh;
    }}
    .block-container {{
        padding: 1.5rem 2rem;
        max-width: 1400px;
    }}

    /* ── Sidebar ── */
    section[data-testid="stSidebar"] {{
        background: {sidebar_bg} !important;
        backdrop-filter: blur(20px);
        border-right: 1px solid {card_border};
    }}
    section[data-testid="stSidebar"] .block-container {{
        padding: 1.5rem 1rem;
    }}

    /* ── Glass cards ── */
    .glass-card {{
        background: {card_bg};
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        border: 1px solid {card_border};
        border-radius: 20px;
        padding: 1.5rem;
        box-shadow: {card_shadow};
        color: {text_primary};
        margin-bottom: 1rem;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }}
    .glass-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.25);
    }}

    /* ── Hero weather card ── */
    .hero-card {{
        background: {card_bg};
        backdrop-filter: blur(20px);
        border: 1px solid {card_border};
        border-radius: 24px;
        padding: 2.5rem 2rem;
        box-shadow: {card_shadow};
        text-align: center;
        margin-bottom: 1.2rem;
        position: relative;
        overflow: hidden;
    }}
    .hero-emoji {{
        font-size: 5rem;
        line-height: 1.1;
        margin-bottom: 0.3rem;
        display: block;
    }}
    .hero-temp {{
        font-family: 'Outfit', sans-serif;
        font-size: 5rem;
        font-weight: 700;
        color: {text_primary};
        line-height: 1;
        letter-spacing: -3px;
    }}
    .hero-city {{
        font-size: 1.5rem;
        font-weight: 600;
        color: {text_primary};
        margin: 0.3rem 0 0.1rem 0;
    }}
    .hero-condition {{
        font-size: 1rem;
        color: {text_secondary};
        margin-bottom: 0.5rem;
    }}
    .hero-time {{
        font-size: 0.78rem;
        color: {text_secondary};
        margin-top: 0.3rem;
    }}

    /* ── Metric pills ── */
    .metric-row {{
        display: flex;
        flex-wrap: wrap;
        gap: 0.75rem;
        margin-top: 1rem;
    }}
    .metric-pill {{
        flex: 1;
        min-width: 100px;
        background: {metric_bg};
        border: 1px solid {card_border};
        border-radius: 14px;
        padding: 0.7rem 1rem;
        text-align: center;
        transition: background 0.2s;
    }}
    .metric-pill:hover {{
        background: rgba(100,149,237,0.12);
    }}
    .metric-pill .mp-icon {{
        font-size: 1.4rem;
        display: block;
        margin-bottom: 0.15rem;
    }}
    .metric-pill .mp-value {{
        font-size: 1.1rem;
        font-weight: 600;
        color: {text_primary};
        display: block;
    }}
    .metric-pill .mp-label {{
        font-size: 0.7rem;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}

    /* ── Section heading ── */
    .section-heading {{
        font-family: 'Outfit', sans-serif;
        font-size: 1.15rem;
        font-weight: 700;
        color: {text_primary};
        margin: 1.5rem 0 0.75rem 0;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        letter-spacing: -0.3px;
    }}

    /* ── Forecast cards ── */
    .forecast-card {{
        background: {card_bg};
        backdrop-filter: blur(12px);
        border: 1px solid {card_border};
        border-radius: 16px;
        padding: 1.2rem 0.8rem;
        text-align: center;
        box-shadow: {card_shadow};
        transition: transform 0.2s;
    }}
    .forecast-card:hover {{
        transform: translateY(-3px);
    }}
    .fc-day {{
        font-size: 0.75rem;
        font-weight: 600;
        color: {text_secondary};
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }}
    .fc-icon {{
        font-size: 2.2rem;
        margin: 0.4rem 0;
        display: block;
    }}
    .fc-temp-max {{
        font-size: 1.3rem;
        font-weight: 700;
        color: {text_primary};
    }}
    .fc-temp-min {{
        font-size: 0.9rem;
        color: {text_secondary};
        margin-left: 0.2rem;
    }}
    .fc-desc {{
        font-size: 0.72rem;
        color: {text_secondary};
        margin-top: 0.3rem;
    }}
    .fc-pop {{
        font-size: 0.72rem;
        color: #64B5F6;
        margin-top: 0.15rem;
    }}

    /* ── Insight cards ── */
    .insight-success {{ border-left: 4px solid #66BB6A !important; }}
    .insight-warning {{ border-left: 4px solid #FFA726 !important; }}
    .insight-error   {{ border-left: 4px solid #EF5350 !important; }}
    .insight-info    {{ border-left: 4px solid #42A5F5 !important; }}
    .insight-title {{
        font-weight: 700;
        font-size: 0.95rem;
        color: {text_primary};
        margin-bottom: 0.2rem;
    }}
    .insight-msg {{
        font-size: 0.85rem;
        color: {text_secondary};
        line-height: 1.5;
    }}

    /* ── Sidebar items ── */
    .fav-city-btn {{
        width: 100%;
        padding: 0.55rem 1rem;
        margin: 0.2rem 0;
        background: {metric_bg};
        border: 1px solid {card_border};
        border-radius: 10px;
        color: {text_primary};
        font-family: 'Inter', sans-serif;
        font-size: 0.88rem;
        cursor: pointer;
        text-align: left;
        transition: background 0.2s;
    }}
    .fav-city-btn:hover {{
        background: rgba(100,149,237,0.15);
    }}

    /* ── History table ── */
    .history-row {{
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.6rem 0.8rem;
        border-radius: 10px;
        background: {metric_bg};
        margin-bottom: 0.4rem;
        font-size: 0.85rem;
        color: {text_primary};
    }}

    /* ── Streamlit widget tweaks ── */
    div[data-testid="stTextInput"] input {{
        background: {input_bg} !important;
        border: 1px solid {card_border} !important;
        border-radius: 12px !important;
        color: {text_primary} !important;
        padding: 0.6rem 1rem !important;
    }}
    div.stButton > button {{
        background: linear-gradient(135deg, #4F8EF7 0%, #6C5CE7 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.55rem 1.5rem !important;
        font-weight: 600 !important;
        transition: opacity 0.2s !important;
        width: 100% !important;
    }}
    div.stButton > button:hover {{
        opacity: 0.88 !important;
    }}
    div[data-testid="stSelectbox"] > div {{
        background: {input_bg} !important;
        border-radius: 12px !important;
    }}

    /* ── Tab styling ── */
    button[data-baseweb="tab"] {{
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        font-size: 0.88rem !important;
    }}

    /* ── Hide Streamlit branding ── */
    #MainMenu, footer, header {{ visibility: hidden; }}
    </style>
    """, unsafe_allow_html=True)


# Session state init 

def init_state():
    defaults = {
        "dark_mode": True,
        "city": "",
        "weather": None,
        "forecast_df": None,
        "history": [],        # list of {city, temp, condition, time}
        "favorites": ["London", "New York", "Tokyo", "Mumbai", "Sydney"],
        "last_refresh": None,
        "auto_refresh": False,
        "refresh_interval": 300,  # seconds
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v

init_state()


# Fetch & cache weather 

def fetch_weather(city: str, api_key: str):
    """Fetch current + forecast, update session state."""
    with st.spinner(f"Fetching weather for **{city}**…"):
        raw_current = get_current_weather(city, api_key)
        raw_forecast = get_forecast(city, api_key)
    weather = parse_current_weather(raw_current)
    forecast_list = parse_forecast(raw_forecast)
    forecast_df = pd.DataFrame(forecast_list)

    st.session_state.weather = weather
    st.session_state.forecast_df = forecast_df
    st.session_state.city = city
    st.session_state.last_refresh = datetime.now()

    # Add to history (dedup by city)
    entry = {
        "city": f"{weather['city']}, {weather['country']}",
        "temp": weather["temp"],
        "condition": weather["condition"],
        "time": datetime.now().strftime("%H:%M"),
    }
    # Remove existing entry for same city, prepend new
    st.session_state.history = [
        h for h in st.session_state.history
        if h["city"] != entry["city"]
    ][:9]  # keep max 9 history entries
    st.session_state.history.insert(0, entry)


# Sidebar 

def render_sidebar(api_key: str):
    with st.sidebar:
        # Logo & title
        st.markdown("""
        <div style="text-align:center; padding: 0.5rem 0 1.2rem 0;">
            <span style="font-size:2.8rem;">🌤️</span>
            <div style="font-family:'Outfit',sans-serif; font-size:1.4rem; font-weight:700; margin-top:0.2rem;">WeatherSense</div>
            <div style="font-size:0.72rem; opacity:0.5; letter-spacing:1px; text-transform:uppercase;">AI Weather Dashboard</div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("#### 🔍 Search City")
        city_input = st.text_input(
            "City name",
            value=st.session_state.city,
            placeholder="e.g. Paris, Tokyo, Mumbai",
            label_visibility="collapsed",
        )
        search_clicked = st.button("Get Weather", use_container_width=True)

        if search_clicked and city_input.strip():
            try:
                fetch_weather(city_input.strip(), api_key)
                st.success("Weather updated!")
            except (ValueError, ConnectionError, TimeoutError) as e:
                st.error(str(e))
        elif search_clicked:
            st.warning("Please enter a city name.")

        # Dark / Light mode
        st.markdown("---")
        st.markdown("#### ⚙️ Settings")
        dark = st.toggle("Dark Mode", value=st.session_state.dark_mode)
        st.session_state.dark_mode = dark

        auto = st.toggle("Auto-Refresh", value=st.session_state.auto_refresh)
        st.session_state.auto_refresh = auto
        if auto:
            interval = st.select_slider(
                "Refresh every",
                options=[60, 120, 300, 600, 1800],
                value=st.session_state.refresh_interval,
                format_func=lambda x: f"{x//60} min" if x >= 60 else f"{x}s",
            )
            st.session_state.refresh_interval = interval

        # Favourite cities
        st.markdown("---")
        st.markdown("#### ⭐ Favourite Cities")
        for fav in st.session_state.favorites:
            if st.button(f"🏙️  {fav}", key=f"fav_{fav}", use_container_width=True):
                try:
                    fetch_weather(fav, api_key)
                except (ValueError, ConnectionError, TimeoutError) as e:
                    st.error(str(e))

        # Add to favourites
        if st.session_state.city:
            city_label = st.session_state.weather["city"] if st.session_state.weather else st.session_state.city
            if city_label not in st.session_state.favorites:
                if st.button("⭐ Save current city", use_container_width=True):
                    st.session_state.favorites.append(city_label)
                    st.success(f"Added {city_label} to favourites!")

        # Search history
        if st.session_state.history:
            st.markdown("---")
            st.markdown("#### 🕓 Recent Searches")
            for h in st.session_state.history[:5]:
                emoji = get_emoji(
                    "01d" if h["condition"] == "Clear" else
                    "09d" if h["condition"] in ["Rain", "Drizzle"] else
                    "03d"
                )
                st.markdown(
                    f"<div class='history-row'>"
                    f"{emoji} <b>{h['city']}</b> &nbsp; {h['temp']}°C &nbsp;"
                    f"<span style='opacity:0.5;font-size:0.75rem;'>{h['time']}</span>"
                    f"</div>",
                    unsafe_allow_html=True,
                )

        # Last refresh info
        if st.session_state.last_refresh:
            st.markdown(
                f"<div style='opacity:0.35; font-size:0.72rem; text-align:center; margin-top:1rem;'>"
                f"Updated {st.session_state.last_refresh.strftime('%H:%M:%S')}</div>",
                unsafe_allow_html=True,
            )


#  Hero current-weather card 

def render_hero(weather: dict):
    emoji = get_emoji(weather["icon"])
    cond_color = get_condition_color(weather["condition"])

    st.markdown(f"""
    <div class="hero-card" style="border-top: 4px solid {cond_color};">
        <span class="hero-emoji">{emoji}</span>
        <div class="hero-temp">{weather['temp']}°C</div>
        <div class="hero-city">📍 {weather['city']}, {weather['country']}</div>
        <div class="hero-condition">{weather['description']}</div>
        <div style="display:flex; justify-content:center; gap:1.5rem; margin-top:0.6rem; font-size:0.85rem; opacity:0.7;">
            <span>↑ {weather['temp_max']}°</span>
            <span>↓ {weather['temp_min']}°</span>
            <span>Feels {weather['feels_like']}°</span>
        </div>
        <div class="hero-time">🕐 {weather['timestamp']}</div>
    </div>
    """, unsafe_allow_html=True)


def render_metrics(weather: dict):
    wind_dir = wind_direction(weather["wind_deg"])
    metrics = [
        ("💧", f"{weather['humidity']}%", "Humidity"),
        ("🔵", f"{weather['pressure']} hPa", "Pressure"),
        ("💨", f"{weather['wind_speed']} km/h {wind_dir}", "Wind"),
        ("👁️", f"{weather['visibility']} km", "Visibility"),
        ("☁️", f"{weather['clouds']}%", "Cloud Cover"),
        ("🌅", weather["sunrise"], "Sunrise UTC"),
        ("🌇", weather["sunset"], "Sunset UTC"),
    ]

    pills_html = "<div class='metric-row'>"
    for icon, value, label in metrics:
        pills_html += f"""
        <div class="metric-pill">
            <span class="mp-icon">{icon}</span>
            <span class="mp-value">{value}</span>
            <span class="mp-label">{label}</span>
        </div>"""
    pills_html += "</div>"
    st.markdown(pills_html, unsafe_allow_html=True)


#  5-Day Forecast Cards 

def render_forecast_cards(daily: pd.DataFrame):
    st.markdown("<div class='section-heading'>📅 5-Day Forecast</div>", unsafe_allow_html=True)
    cols = st.columns(len(daily))
    for idx, (_, row) in enumerate(daily.iterrows()):
        with cols[idx]:
            emoji = get_emoji(row["icon"])
            pop_str = f"🌧 {row['pop']}%" if row["pop"] > 0 else ""
            st.markdown(f"""
            <div class="forecast-card">
                <div class="fc-day">{row['day_label']}</div>
                <span class="fc-icon">{emoji}</span>
                <div>
                    <span class="fc-temp-max">{row['temp_max']}°</span>
                    <span class="fc-temp-min">{row['temp_min']}°</span>
                </div>
                <div class="fc-desc">{row['description']}</div>
                <div class="fc-pop">{pop_str}</div>
            </div>
            """, unsafe_allow_html=True)


#  Charts section 

def render_charts(df: pd.DataFrame):
    st.markdown("<div class='section-heading'>📊 Interactive Trends</div>", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🌡️ Temperature", "💧 Humidity", "💨 Wind", "🔵 Pressure", "🌧️ Precipitation"
    ])
    cfg = {"displayModeBar": False, "responsive": True}

    with tab1:
        st.plotly_chart(make_temperature_chart(df), use_container_width=True, config=cfg)
    with tab2:
        st.plotly_chart(make_humidity_chart(df), use_container_width=True, config=cfg)
    with tab3:
        st.plotly_chart(make_wind_chart(df), use_container_width=True, config=cfg)
    with tab4:
        st.plotly_chart(make_pressure_chart(df), use_container_width=True, config=cfg)
    with tab5:
        st.plotly_chart(make_precip_chart(df), use_container_width=True, config=cfg)


# Insights section 

def render_insights(weather: dict, forecast_df: pd.DataFrame):
    st.markdown("<div class='section-heading'>🤖 AI Weather Insights</div>", unsafe_allow_html=True)
    insights = generate_ai_insights(weather, forecast_df)

    cols = st.columns(2)
    for i, insight in enumerate(insights):
        with cols[i % 2]:
            st.markdown(f"""
            <div class="glass-card insight-{insight['level']}">
                <div style="font-size:1.8rem; margin-bottom:0.4rem;">{insight['icon']}</div>
                <div class="insight-title">{insight['title']}</div>
                <div class="insight-msg">{insight['message']}</div>
            </div>
            """, unsafe_allow_html=True)


#  History section 

def render_history():
    if not st.session_state.history:
        st.info("No search history yet. Search for a city to get started.")
        return

    st.markdown("<div class='section-heading'>🕓 Search History</div>", unsafe_allow_html=True)
    history_df = pd.DataFrame(st.session_state.history)
    history_df.columns = ["City", "Temp (°C)", "Condition", "Time"]
    st.dataframe(
        history_df,
        use_container_width=True,
        hide_index=True,
    )


#  Welcome screen 

def render_welcome():
    st.markdown("""
    <div style="text-align:center; padding: 4rem 1rem;">
        <div style="font-size:5rem; margin-bottom:1rem;">🌤️</div>
        <h1 style="font-family:'Outfit',sans-serif; font-size:2.5rem; font-weight:800; margin-bottom:0.5rem;">
            Welcome to WeatherSense
        </h1>
        <p style="font-size:1.1rem; opacity:0.6; max-width:480px; margin:0 auto 2rem auto;">
            Enter a city name in the sidebar to get a real-time AI-powered weather forecast with interactive charts.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)
    features = [
        ("🌡️", "Live Weather", "Real-time data for any city worldwide"),
        ("📅", "5-Day Forecast", "Daily predictions with hourly breakdown"),
        ("📊", "Visual Trends", "Interactive Plotly charts for all metrics"),
        ("🤖", "AI Insights", "Smart recommendations tailored to conditions"),
    ]
    for col, (icon, title, desc) in zip([col1, col2, col3, col4], features):
        with col:
            st.markdown(f"""
            <div class="glass-card" style="text-align:center;">
                <div style="font-size:2rem; margin-bottom:0.5rem;">{icon}</div>
                <div style="font-weight:700; margin-bottom:0.3rem;">{title}</div>
                <div style="font-size:0.82rem; opacity:0.6;">{desc}</div>
            </div>
            """, unsafe_allow_html=True)


#  Main 

def main():
    # Load CSS for current theme
    load_css(st.session_state.dark_mode)

    # Retrieve API key from Streamlit secrets or session
    api_key = ""
    try:
        api_key = st.secrets["OPENWEATHERMAP_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass  # Will prompt user below

    # Sidebar navigation & search
    render_sidebar(api_key if api_key else "MISSING_KEY")

    # If no API key, show setup banner
    if not api_key:
        st.warning(
            "⚠️ **API Key Missing** — Add your OpenWeatherMap API key to `.streamlit/secrets.toml`:\n\n"
            "```toml\nOPENWEATHERMAP_API_KEY = \"your_key_here\"\n```\n\n"
            "Get a free key at [openweathermap.org](https://openweathermap.org/api)",
            icon="🔑"
        )
        api_key = st.text_input(
            "Or enter your API key here to try it out:",
            type="password",
            placeholder="Paste your OpenWeatherMap API key…",
        )
        if api_key:
            # Retry with inline key
            if st.session_state.city:
                try:
                    fetch_weather(st.session_state.city, api_key)
                except Exception:
                    pass

    # Auto-refresh logic
    if (
        st.session_state.auto_refresh
        and st.session_state.city
        and st.session_state.last_refresh
        and api_key
    ):
        elapsed = (datetime.now() - st.session_state.last_refresh).seconds
        if elapsed >= st.session_state.refresh_interval:
            try:
                fetch_weather(st.session_state.city, api_key)
            except Exception:
                pass
        st.markdown(
            f"<div style='text-align:right; opacity:0.4; font-size:0.75rem; margin-bottom:0.5rem;'>"
            f"Auto-refresh in {max(0, st.session_state.refresh_interval - elapsed)}s</div>",
            unsafe_allow_html=True,
        )

    # Render content
    if st.session_state.weather is None:
        render_welcome()
    else:
        weather = st.session_state.weather
        forecast_df = st.session_state.forecast_df
        daily = get_daily_summary(forecast_df)

        # Current conditions
        col_hero, col_right = st.columns([1.1, 1.9])
        with col_hero:
            render_hero(weather)
        with col_right:
            st.markdown("<div class='section-heading'>📋 Current Conditions</div>", unsafe_allow_html=True)
            render_metrics(weather)

        st.markdown("---")

        # 5-day forecast
        render_forecast_cards(daily)

        st.markdown("---")

        # Tabs: Charts | AI Insights | History
        main_tab1, main_tab2, main_tab3 = st.tabs([
            "📊 Charts & Trends", "🤖 AI Insights", "🕓 History"
        ])

        with main_tab1:
            render_charts(forecast_df)

        with main_tab2:
            render_insights(weather, forecast_df)

        with main_tab3:
            render_history()

    # Footer
    st.markdown("""
    <div style="text-align:center; opacity:0.3; font-size:0.75rem; padding: 2rem 0 0.5rem 0;">
        WeatherSense · Powered by OpenWeatherMap · Built with Streamlit
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
