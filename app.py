import requests
from flask import Flask, render_template, request

app = Flask(__name__)


def fetch_weather(api_key, location, country_code="us"):
    """fetch the weather date from the OpenWeatherMap API
    
    Keyword arguments:
    api_key -- the API key
    Return: JSON object
    """
    
    
    
    api_key = "3450acc3ccb969baf99ddbcb6796e04e"

    # Check if the location is a zip code (assuming it only contains digits)
    if location.isdigit():

        api_url = "http://api.openweathermap.org/data/2.5/weather?zip={},{}&units=imperial&appid={}".format(location, country_code, api_key)
    else:
        api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}".format(location, api_key)

    r = requests.get(api_url)
    return r.json()

# Example usage:
api_key = '3450acc3ccb969baf99ddbcb6796e04e'
print(fetch_weather(api_key, 'San Francisco'))  # Fetch by city name
print(fetch_weather(api_key, '94103'))  # Fetch by zip code


if __name__ == '__main__':
    app.run(debug=True)
