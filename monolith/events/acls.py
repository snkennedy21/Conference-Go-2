from codecs import latin_1_decode
from .keys import PEXELS_API_KEY, OPEN_WEATHER_API_KEY
import json
import requests


def get_picture(city, state):
  url = "https://api.pexels.com/v1/search"
  headers = {"Authorization": PEXELS_API_KEY}
  params = {"query": f"{city} {state}", "page": 1, "per_page": 1}
  response = requests.get(url, headers=headers, params=params)
  data = json.loads(response.content)
  picture_url = data['photos'][0]['src']['original']
  return {"picture_url": picture_url}

  
def get_lat_lon(city, state):
  url = "http://api.openweathermap.org/geo/1.0/direct"
  params = {"q": f"{city},{state},USA", "appid": OPEN_WEATHER_API_KEY}
  response = requests.get(url, params=params)
  json_data = response.json()
  lat = json_data[0]["lat"]
  lon = json_data[0]["lon"]
  return lat, lon

def get_weather(city, state):
  lat, lon = get_lat_lon(city, state)
  url = "https://api.openweathermap.org/data/2.5/weather"
  params = {"lat": lat, "lon": lon, "appid": OPEN_WEATHER_API_KEY, "units": "imperial",}
  response = requests.get(url, params=params)
  json_data = response.json()
  if json_data == {'cod': '400', 'message': 'wrong latitude'}:
    return None
  else:
    return {
      "description": json_data['weather'][0]["description"],
      "temperature": json_data['main']['temp']
    }
