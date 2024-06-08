import requests
from flask import Flask, render_template, request, abort, redirect, url_for, flash
from werkzeug.security import generate_password_hash, check_password_hash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from flask_wtf import FlaskForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'thisisasecretkey'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

class User(db.Model, UserMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)
        

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class RegisterForm(FlaskForm):
    email = StringField(validators=[
        InputRequired(), Length(min=4, max=50)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    
    def validate_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        if existing_user_email:
            raise ValidationError('That email already exists. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField(validators=[
        InputRequired(), Length(min=4, max=30)], render_kw={"placeholder": "Email"})
    password = PasswordField(validators=[
        InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')
    
@app.before_request
def before_first_request():
    db.create_all()
    pass


@app.route('/search')
@login_required
def search():
   return render_template('newsearch.html')

@app.route('/')
def home():
    return render_template('newhome.html')

@app.route('/results', methods=['POST'])
def get_forecast():
    location = request.form.get('location')
    if not location:
        abort(400, description="The 'location' field is required.")

    api_key = "3450acc3ccb969baf99ddbcb6796e04e"
    qapi_key = "f8f537204d2341b8292c06070ef4c6cd908686acbd6288bf1c4ea701ba90c2e5"
    units = request.form.get('units', 'imperial')
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

        air_quality = get_air_quality(location_name, qapi_key)
        if air_quality:
            aqi = air_quality.get("aqi", "N/A")
            pollutants = air_quality.get("pollutants", "N/A")
        else:
            aqi = "N/A"
            pollutants = "N/A"

        return render_template('results.html', location=location, temp=temp, feels_like=feels_like, weather=weather, units=units_symbol, aqi=aqi, pollutants=pollutants)
    else:
        abort(400, description="Invalid location or API response.")

def get_city_name_by_coordinates(lat, lon, api_key):
    reverse_geocode_url = f"http://api.openweathermap.org/geo/1.0/reverse?lat={lat}&lon={lon}&limit=1&appid={api_key}"
    response = requests.get(reverse_geocode_url)
    data = response.json()
    if response.status_code == 200 and len(data) > 0:
        city_name = data[0].get("name")
        state_name = data[0].get("state")
        if city_name == "Municipality of Al Shamal":
            city_name = "Riyadh"
        if city_name and state_name:
            return city_name, state_name
        elif state_name:
            return None, state_name
    return None, None

def get_weather_results_by_zip(zip_code, api_key, units):
    api_url = f"http://api.openweathermap.org/data/2.5/weather?zip={zip_code}&units={units}&appid={api_key}"
    r = requests.get(api_url)
    return r.json()

def get_weather_results_by_city(city_name, state_name, api_key, units):
    if city_name:
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&units={units}&appid={api_key}"
    else:
        api_url = f"http://api.openweathermap.org/data/2.5/weather?q={state_name}&units={units}&appid={api_key}"
    result = requests.get(api_url)
    return result.json()

def get_air_quality(city_name, qapi_key):
    api_url = f"https://api.openaq.org/v2/latest?city={city_name}"
    headers = {'X-API-Key': qapi_key}
    response = requests.get(api_url, headers=headers)
    data = response.json()
    if response.status_code == 200 and "results" in data and len(data["results"]) > 0:
        aqi = data["results"][0].get("measurements")[0].get("value")
        pollutants = ', '.join([m["parameter"] for m in data["results"][0].get("measurements")])
        return {"aqi": aqi, "pollutants": pollutants}
    return None

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('Login successful!', 'success')
            return redirect(url_for('search'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(email=form.email.data, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.')
    return redirect(url_for('home'))

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':

    app.run(debug=True, host='0.0.0.0', port=5000)

