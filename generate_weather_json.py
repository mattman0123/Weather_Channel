import http.server
import socketserver
import threading
import time
import random
import requests
import json
import feedparser
import yfinance as yf
import os
from bs4 import BeautifulSoup
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from html.parser import HTMLParser
from dotenv import load_dotenv


# === CONFIG ===from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
LOCATION = "Winnipeg"
REFRESH_INTERVAL = 15 * 60  # 15 minutes
PORT = 8000

# === Output Files ===
WEATHER_FILE = "weather.json"
NEWS_FILE = "news.json"
STOCK_FILE = "stocks.json"
ALERTS_FILE = "alerts.json"
AQHI_ALERTS_FILE = "aqhi_alerts.json"

# === Stock Symbols ===
STOCK_SYMBOLS = [
    # Tech Stocks
    "AAPL",   # Apple
    "MSFT",   # Microsoft
    "NVDA",   # Nvidia
    "GOOGL",  # Alphabet (Google)

    # Farming/Agriculture Stocks
    "DE",     # Deere & Co (tractors & ag tech)
    "ADM",    # Archer-Daniels-Midland (ag processing)
    "BG",     # Bunge Limited (global agribusiness)
    "CF"      # CF Industries (fertilizers)
]
# === URLs ===
NEWS_FEED_URLS = [
    "https://globalnews.ca/winnipeg/feed/",
    "https://www.manitobacooperator.ca/feed/",
    "https://www.producer.com/news/feed/"
]

ECCC_ALERTS_URL = "https://weather.gc.ca/warnings/index_e.html?prov=mb"

class HTMLStripper(HTMLParser):
    def __init__(self):
        super().__init__()
        self.result = []

    def handle_data(self, d):
        self.result.append(d)

    def get_data(self):
        return ''.join(self.result)

def strip_tags(html):
    s = HTMLStripper()
    s.feed(html)
    return s.get_data()

def fetch_weatherapi_data():
    print(f"[{datetime.now()}] Fetching weather data from WeatherAPI...")
    url = f"http://api.weatherapi.com/v1/forecast.json?key={API_KEY}&q={LOCATION}&days=5&aqi=yes&alerts=yes"
    res = requests.get(url)
    data = res.json()

    slides = []

    # Current weather
    current = data["current"]
    if current["precip_mm"] > 0.0:
        slides.append(f"CURRENT: {current['temp_c']}°C, {current['condition']['text'].upper()}\n"
                  f"HUMIDITY: {current['humidity']}%\nWIND: {current['wind_kph']} KM/H -- {current['wind_dir']}\n"
                  f"ESTIMATE RAIN: {current['precip_mm']}mm")
    else:
        slides.append(f"CURRENT: {current['temp_c']}°C, {current['condition']['text'].upper()}\n"
                  f"HUMIDITY: {current['humidity']}%\nWIND: {current['wind_kph']} KM/H -- {current['wind_dir']}\n")

    # AQI 
    slides.append(f"AIR QUAILITY INDEX\n"
                  f"CO: {current['air_quality']['co']} -- NO2: {current['air_quality']['no2']}\nO3: {current['air_quality']['o3']}\n"
                  f"PM2.5: {current['air_quality']['pm2_5']} -- PM10: {current['air_quality']['pm10']}\n")
    
    # Rain Chance
    Rain_slide = "5-DAY RAIN FORECAST:\n"
    for day in data["forecast"]["forecastday"]:
        if day['day']['daily_will_it_rain'] == 1:
            Rain_slide += f"{datetime.strptime(day['date'], '%Y-%m-%d').strftime('%a').upper()}: " \
                            f"{day['day']['totalprecip_mm']} MM - HUMIDITY {day['day']['avghumidity']}% - " \
                            f"CHANCE: {day['day']['daily_chance_of_rain']}% - {day['day']['condition']['text'].upper()}\n"
        elif day['day']['daily_will_it_snow'] == 1:
            Rain_slide += f"{datetime.strptime(day['date'], '%Y-%m-%d').strftime('%a').upper()}: " \
                            f"{day['day']['totalsnow_cm']} CM - HUMIDITY {day['day']['avghumidity']}% - " \
                            f"CHANCE: {day['day']['daily_chance_of_snow']}% - {day['day']['condition']['text'].upper()}\n"
        else:
            Rain_slide += f"{datetime.strptime(day['date'], '%Y-%m-%d').strftime('%a').upper()}: " \
                            f"{day['day']['condition']['text'].upper()}\n"
            
    slides.append(Rain_slide.strip())

    # Next 5 hours
    hours = data["forecast"]["forecastday"][0]["hour"]
    next_hours = [h for h in hours if int(h["time"].split(" ")[1].split(":")[0]) >= datetime.now().hour][:5]
    hour_slide = "NEXT HOURS:\n" + "\n".join(
        f"{h['time'].split(' ')[1][:5]} - {h['temp_c']}°C, {h['condition']['text'].upper()}, WIND: {h['wind_kph']}KM/H - {h['wind_dir']}" for h in next_hours)
    slides.append(hour_slide)

    # 5-day forecast
    forecast_slide = "5-DAY FORECAST:\n"
    for day in data["forecast"]["forecastday"]:
        forecast_slide += f"{datetime.strptime(day['date'], '%Y-%m-%d').strftime('%a').upper()}: " \
                          f"{day['day']['maxtemp_c']}° / {day['day']['mintemp_c']}°C - " \
                          f"{day['day']['condition']['text'].upper()}\n"
    slides.append(forecast_slide.strip())

    # WeatherAPI alerts
    alerts = data.get("alerts", {}).get("alert", [])
    alert_slides = []

    for alert in alerts:
        headline = alert.get('headline', 'No headline').replace('\n', ' ').replace('\r', ' ').strip()
        desc = alert.get('desc', 'No description').replace('\n', ' ').replace('\r', ' ').strip()
        instruction = alert.get('instruction', 'No instructions').replace('\n', ' ').replace('\r', ' ').strip()

        alert_slides.append(
            f"⚠️ WEATHER ALERT ⚠️ {headline} --- {desc} --- {instruction}..."
        )



    return slides, alert_slides


def fetch_environment_canada_aqhi_alerts():
    try:
        print(f"[{datetime.now()}] Fetching ECCC AQHI forecasts...")

        alerts = []
        hourly_aqhi = defaultdict(list)

        # Fetch AQHI forecasts for Winnipeg
        aqhi_url = "https://api.weather.gc.ca/collections/aqhi-forecasts-realtime/items?location_name_en=Winnipeg&lang=eng&f=json"
        response = requests.get(aqhi_url, timeout=10)
        response.raise_for_status()
        aqhi_data = response.json()

        now = datetime.now(timezone.utc)
        end = now + timedelta(hours=12)

        for feature in aqhi_data.get("features", []):
            props = feature.get("properties", {})
            aqhi_value = props.get("aqhi")
            forecast_time_str = props.get("forecast_datetime")

            if aqhi_value is None or forecast_time_str is None:
                continue

            forecast_time = datetime.fromisoformat(forecast_time_str.replace("Z", "+00:00"))

            if now <= forecast_time <= end:
                # Group by hour
                forecast_hour = forecast_time.replace(minute=0, second=0, microsecond=0)
                hourly_aqhi[forecast_hour].append(aqhi_value)

        for hour, values in sorted(hourly_aqhi.items()):
            avg = round(sum(values) / len(values))
            if avg <= 3:
                continue  # Skip low-risk hours

            if 4 <= avg <= 6:
                risk = "Moderate"
            elif 7 <= avg <= 10:
                risk = "High"
            else:
                risk = "Very High"

            local_time_str = hour.astimezone().strftime("%I:%M %p").lstrip("0")  # local time
            alert = f"Winnipeg - {local_time_str}: AIR QUALITY {avg} ({risk})"
            alerts.append(alert)

        if alerts:
            print(f"[{datetime.now()}] ✅ Averaged to {len(alerts)} hourly AQHI alerts.")
        else:
            print(f"[{datetime.now()}] ✅ No AQHI alerts in the next 12 hours.")

        return alerts

    except Exception as e:
        print(f"[{datetime.now()}] ❌ Failed to fetch ECCC AQHI alerts: {e}")
        return []


def fetch_local_news():
    try:
        print(f"[{datetime.now()}] Fetching local news from {len(NEWS_FEED_URLS)} sources...")
        headlines = []

        for url in NEWS_FEED_URLS:
            feed = feedparser.parse(url)

            if feed.entries:
                # Pick 2 random articles from the top 10
                top_entries = feed.entries[:10]
                selected = random.sample(top_entries, k=min(2, len(top_entries)))

                for entry in selected:
                    title = strip_tags(entry.title)
                    summary = strip_tags(entry.summary) if hasattr(entry, "summary") else "No summary available."
                    link = strip_tags(entry.link)


                    headlines.append({
                        "title": title,
                        "headline": title,
                        "summary": summary,
                        "link": link
                    })

        with open(NEWS_FILE, "w") as f:
            json.dump(headlines, f, indent=2)

        print(f"[{datetime.now()}] ✅ News updated: {len(headlines)} stories fetched.")
    except Exception as e:
        print(f"[{datetime.now()}] ❌ News fetch failed: {e}")


def fetch_stock_data():
    try:
        print(f"[{datetime.now()}] Fetching stock data...")
        stock_data = {}

        for symbol in STOCK_SYMBOLS:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d")
            if not data.empty:
                latest_price = round(data["Close"].iloc[-1], 2)
                previous_close = ticker.info.get("previousClose", latest_price)
                change = round(latest_price - previous_close, 2)
                percent = round((change / previous_close) * 100, 2) if previous_close else 0.0
                name = ticker.info.get("shortName", "Unknown Company")

                stock_data[symbol] = {
                    "name": name,
                    "price": latest_price,
                    "change": change,
                    "percent": percent
                }

        with open(STOCK_FILE, "w") as f:
            json.dump(stock_data, f, indent=2)

        print(f"[{datetime.now()}] ✅ Stocks updated.")
    except Exception as e:
        print(f"❌ Stock fetch failed: {e}")


def update_all():
    while True:
        print(f"[{datetime.now()}] 🔄 Starting data update cycle...")

        # Weather & alerts
        weather_slides, weatherapi_alerts = fetch_weatherapi_data()
        env_canada_aqhi_alerts = fetch_environment_canada_aqhi_alerts()

        # Save weather
        with open(WEATHER_FILE, "w") as f:
            json.dump(weather_slides, f, indent=2)

        # Save alerts
        all_alerts = weatherapi_alerts
        with open(ALERTS_FILE, "w") as f:
            json.dump(all_alerts, f, indent=2)
        
        with open(AQHI_ALERTS_FILE, "w") as f:
            json.dump(env_canada_aqhi_alerts, f, indent=2)

        print(f"[{datetime.now()}] ✅ Weather and alerts saved.")

        # News & Stocks
        fetch_local_news()
        fetch_stock_data()

        print(f"[{datetime.now()}] ✅ Update cycle complete. Sleeping {REFRESH_INTERVAL} seconds.\n")
        time.sleep(REFRESH_INTERVAL)


def start_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        print(f"🌐 Serving at http://localhost:{PORT}")
        httpd.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=update_all, daemon=True).start()
    start_server()
