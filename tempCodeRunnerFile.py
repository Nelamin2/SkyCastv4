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

    if ',' in location:
        lat, lon = location.split(',')
        data = get_weather_results_by_coordinates(lat, lon, api_key)
    elif location.isdigit():
        data = get_weather_results_by_zip(location, api_key)
    else:
        data = get_weather_results_by_city(location, api_key)
    print(f"Data received: {data}")  # Debugging print statement

    if 'main' in data and 'weather' in data:
        temp = "{0:.2f}".format(data["main"]["temp"])
        feels_like = "{0:.2f}".format(data["main"]["feels_like"])
        weather = data["weather"][0]["main"]
        location = data["name"]

        return render_template('view_forecast.html',
                            location=location, temp=temp,
                             feels_like=feels_like, weather=weather)
    else:
        abort(400, description="Invalid location or API response.")



def get_weather_results_by_zip(zip_code, api_key):
    api_url = "http://api.openweathermap.org/data/2.5/weather?zip={}&units=imperial&appid={}".format(zip_code, api_key)
    r = requests.get(api_url)
    return r.json()

def get_weather_results_by_city(city_name, api_key):
    api_url = "http://api.openweathermap.org/data/2.5/weather?q={}&units=imperial&appid={}".format(city_name, api_key)
    result = requests.get(api_url)
    return result.json()

def get_weather_results_by_coordinates(lat, lon, api_key):
    api_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}"
    result = requests.get(api_url)
    return result.json()

if __name__ == '__main__':
    app.run(debug=True)
    