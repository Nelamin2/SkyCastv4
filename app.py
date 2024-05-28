import requests
from flask import Flask, render_template, request, abort

app = Flask(__name__)

@app.route('/search')
def search():
    """ a function that returns the search page
    Returns:
        render_template: the search page
    """
    return render_template('search.html')

@app.route('/')
def home():
    """ 
    a function that returns the home page
    Returns:  render_template: the home page
    """
    return render_template('home.html')

@app.route('/results', methods=['POST'])
def get_forecast():
    """ 
    a function that returns the results page
    Returns: render_template: the results page
    """
    location = request.form.get('location')
    if not location:
        abort(400, description="The 'location' field is required.")

    api_key = "3450acc3ccb969baf99ddbcb6796e04e"
    qapi_key = "f8f537204d2341b8292c06070ef4c6cd908686acbd6288bf1c4ea701ba90c2e5"

    units = request.form.get('units', 'imperial')  # Default to Fahrenheit if no unit is specified
    units_symbol = '°F' if units == 'imperial' else '°C' if units == 'metric' else 'K'

    if ',' in location:
        lat, lon = location.split(',')
        city_name, state_name = get_city_name_by_coordinates(lat, lon, api_key)
        if city_name is None and state_name is None:
            abort(400, description="Invalid coordinates.")
        data = get_weather_results_by_city(city_name, state_name, api_key, units)
    elif location.isdigit():
        data = get_weather_results_by_zip(location, api_key, units)
    else:
        data = get_weather_results_by_city(location, None, api_key, units)

    if 'main' in data and 'weather' in data:
        temp = "{0:.2f}".format(data["main"]["temp"])
        feels_like = "{0:.2f}".format(data["main"]["feels_like"])
        weather = data["weather"][0]["main"]
        location_name = data["name"]

    # Fetch air quality data
        air_quality = get_air_quality(location_name, qapi_key)
        print("Air Quality Data:", air_quality)  # Debug print
        if air_quality:
            aqi = air_quality.get("aqi", "N/A")
            pollutants = air_quality.get("pollutants", "N/A")
        else:
            aqi = "N/A"
            pollutants = "N/A"
        return render_template('results.html',
                               location=location, temp=temp,
                               feels_like=feels_like, weather=weather, units=units_symbol,  aqi=aqi, pollutants=pollutants)
    else:
        abort(400, description="Invalid location or API response.")

def get_city_name_by_coordinates(lat, lon, api_key):
    """ a function that returns the city name and state name if available, otherwise returns the state name only.

    Args:
        lat 
        lon 
        api_key 

    Returns:
        Returns the city name and state name if available, otherwise returns the state name only.
    """
    reverse_geocode_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
    response = requests.get(reverse_geocode_url)
    data = response.json()
    if response.status_code == 200 and len(data) > 0:
        city_name = data[0].get("name")
        state_name = data[0].get("state")
        if city_name == "Municipality of Al Shamal":
            city_name = "Riyadh"  # Map Municipality of Al Shamal to Riyadh
        if city_name and state_name:
            return city_name, state_name
        elif state_name:
            return None, state_name
    return None, None
def get_weather_results_by_zip(zip_code, api_key, units):
    """ 
    a function that returns the weather data for the given zip code.
    Args:
        zip_code 
        api_key 
        units 

    Returns:
        Returns the weather data for the given zip code.
    """
    api_url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code}&units={units}&appid={api_key}"
    r = requests.get(api_url)
    return r.json()

def get_weather_results_by_city(city_name, state_name, api_key, units):
    """
    a function that returns the weather data for the given city name.
    Args:
        city_name 
        state_name 
        api_key 
        units 

    Returns:
        Returns the weather data for the given city name.
    """
    if city_name:
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units={units}&appid={api_key}"
    else:
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={state_name}&units={units}&appid={api_key}"
    result = requests.get(api_url)
    return result.json()

def get_air_quality(city_name, qapi_key):
    api_url = f"https://api.openaq.org/v2/latest?city={city_name}"
    headers = {
        'X-API-Key': qapi_key
    }
    response = requests.get(api_url, headers=headers)
    data = response.json()
    if response.status_code == 200 and "results" in data and len(data["results"]) > 0:
        aqi = data["results"][0].get("measurements")[0].get("value")
        pollutants = ', '.join([m["parameter"] for m in data["results"][0].get("measurements")])
        return {"aqi": aqi, "pollutants": pollutants}
    return None

if __name__ == '__main__':
    app.run(debug=True)