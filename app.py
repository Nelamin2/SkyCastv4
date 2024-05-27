import requests
from flask import Flask, render_template, request, abort

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/results', methods=['POST'])
def get_forecast():
    location = request.form.get('location')
    if 'location' not in request.form:
        abort(400, description="The 'location' field is required.")
    print(f"Location received: {location}")  # Debugging print statement

    api_key = "3450acc3ccb969baf99ddbcb6796e04e"
    
    print(f"API Key: {api_key}")  # Debugging print statement

    units = request.form.get('units', 'imperial')  # Default to Fahrenheit if no unit is specified
    units_symbol = '°F' if units == 'imperial' else '°C' if units == 'metric' else 'K'
    print(f"Units: {units}, Units symbol: {units_symbol}")  # Debugging print statement

    if ',' in location:
        lat, lon = location.split(',')
        print(f"Coordinates received - Latitude: {lat}, Longitude: {lon}")  # Debugging print statement
        city_name, state_name = get_city_name_by_coordinates(lat, lon, api_key)
        print(f"City name from coordinates: {city_name}, State name: {state_name}")  # Debugging print statement
        data = get_weather_results_by_city(city_name, state_name, api_key, units)
    elif location.isdigit():
        data = get_weather_results_by_zip(location, api_key, units)
    else:
        data = get_weather_results_by_city(location, None, api_key, units)
    print(f"Data received: {data}")  # Debugging print statement

    if 'main' in data and 'weather' in data:
        temp = "{0:.2f}".format(data["main"]["temp"])
        feels_like = "{0:.2f}".format(data["main"]["feels_like"])
        weather = data["weather"][0]["main"]
        location = data["name"]
        print(f"Rendering view with: location={location}, temp={temp}, feels_like={feels_like}, weather={weather}")  # Debugging print statement

        return render_template('view_forecast.html',
                            location=location, temp=temp,
                            feels_like=feels_like, weather=weather, units=units_symbol)
    else:
        abort(400, description="Invalid location or API response.")

def get_city_name_by_coordinates(lat, lon, api_key):
    reverse_geocode_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
    response = requests.get(reverse_geocode_url)
    print(f"Reverse geocoding API response: {response.text}")  # Debugging print statement
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
    abort(400, description="Invalid coordinates or API response.")
    
def get_weather_results_by_zip(zip_code, api_key, units):
    api_url = "http://api.openweathermap.org/data/2.5/weather?zip={}&units={}&appid={}".format(zip_code, units, api_key)
    r = requests.get(api_url)
    return r.json()

def get_weather_results_by_city(city_name, state_name, api_key, units):
    if city_name:
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units={units}&appid={api_key}"
    else:
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={state_name}&units={units}&appid={api_key}"
    result = requests.get(api_url)
    return result.json()


if __name__ == '__main__':
    app.run(debug=True)