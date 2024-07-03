from fastapi import FastAPI, Request
import httpx
import os
from dotenv import load_dotenv


load_dotenv()

app = FastAPI()

IPINFO_TOKEN = os.getenv('IPINFO_TOKEN')
OPENWEATHERMAP_API_KEY = os.getenv('OPENWEATHERMAP_API_KEY')

@app.get("/api/hello")
async def welcome_guest(request: Request, visitor_name: str):
    client_ip = request.client.host

    city = "Unknown location"
    temperature = "unknown temperature"

    location_url = f"https://ipinfo.io/{client_ip}/json?token={IPINFO_TOKEN}"
    async with httpx.AsyncClient() as client:
        try:
            location_response = await client.get(location_url, headers={"Accept": "application/json"})
            location_response.raise_for_status()  
            location_data = location_response.json()

            city = location_data.get("city", "Unknown location")
            loc = location_data.get("loc", "0,0").split(',')
            lat, lon = loc[0], loc[1]
        except Exception as e:
            print(f"Error fetching location data: {e}")

    if lat and lon:
        weather_url = f"http://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={OPENWEATHERMAP_API_KEY}"
        async with httpx.AsyncClient() as client:
            try:
                weather_response = await client.get(weather_url)
                weather_response.raise_for_status()  
                weather_data = weather_response.json()

                temperature = weather_data.get("main", {}).get("temp", "unknown temperature")
            except Exception as e:
                print(f"Error fetching weather data: {e}")

    greeting = f"Hello, {visitor_name}!, the temperature is {temperature} degrees Celsius in {city}"

    return {
        "client_ip": client_ip,
        "location": city,
        "greeting": greeting
    }
