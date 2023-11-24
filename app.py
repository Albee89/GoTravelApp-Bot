#!/usr/bin/env python3.7
from flask import Flask, redirect, url_for, request, render_template, request, template_rendered
import requests
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import InputRequired
import os



# Defining a decorator that has been added in:
def hello_decorator(func):
    # inner1 is a Wrapper function in
    # which the argument is called

    # inner function can access the outer local
    # functions like in this case "func"
    def inner1():
        print("Hello, and welcome to my app before function execution...")

        # calling the actual function now
        # inside the wrapper function.
        func()

        print("After function execution! :)")

    return inner1


# defining a function, to be called inside wrapper
def function_to_be_used():
    print("Inside the function! Wow!")


# passing 'function_to_be_used' inside the
# decorator to control its behavior
function_to_be_used = hello_decorator(function_to_be_used)

# calling the function
function_to_be_used()

# Adding in bloggers itinerary as locations for locations selector:
locations = {
    "Lake District National Park": {"lat": 54.4609, "lng": -3.0886},
    "Corfe Castle": {"lat": 50.6419, "lng": -2.0554},
    "The Cotswolds": {"lat": 51.9294, "lng": -1.7203},
    "Cambridge": {"lat": 52.2053, "lng": 0.1218},
    "Bristol": {"lat": 51.4545, "lng": -2.5879},
    "Oxford": {"lat": 51.752, "lng": -1.2577},
    "Norwich": {"lat": 52.6309, "lng": 1.2974},
    "Stonehenge": {"lat": 51.1789, "lng": -1.8262},
    "Watergate Bay": {"lat": 50.4429, "lng": -5.0553},
    "Birmingham": {"lat": 52.4862, "lng": -1.8904}
}


# Generating choices from the above locations dictionary using class method:
class LocationForm(FlaskForm):  # class attributes:
    location = SelectField('Select a location', choices=[(location, location) for location in locations.keys()],
                           validators=[InputRequired()])
    submit = SubmitField('Submit')


app = Flask(__name__)


# Set the secret key in your Flask app config
load_dotenv("../weather1.env")
load_dotenv("../google.env")
load_dotenv("../weather_3.env")
load_dotenv("../we2.env")
load_dotenv("../secret.env")

# Retrieve API keys from the environment, access variable, with a default value if not found on SECRET_KEY:
API_key = os.getenv("weather_api")
google_API = os.getenv("google_API")
weather_key = os.getenv("weather_3")
API_KEY2 = os.getenv("API_KEY2")
SECRET_KEY = os.environ.get('SECRET_KEY', 'abc123ced456')

app.config['SECRET_KEY'] = SECRET_KEY



# app configs, added in sqlite to call later at weather_data:
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'  # using sqlite
#db = SQLAlchemy(app)


# importing model/database to be called by get_weather function:
#class weatherModel(db.Model):
    #id = db.Column(db.Integer, primary_key=True)
    #city = db.Column(db.String(50), nullable=False)
    #description = db.Column(db.String(100))
    #temperature = db.Column(db.Float)
    #humidity = db.Column(db.Float)
#def __repr__(self):
    #return f"User('{self.username}', '{self.email}')"


@app.route("/")
def home():
    return render_template("index.html")


@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        city_name = request.form['city']
        # pulling API data from openweathermap API:
        if city_name:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={API_key}"
            # if status_code is 200, weather data is generated as a json response, converted from kelvin to celcius temperature
            # with round() method, rendered via a template and displayed via result.html:
            response = requests.get(url)
            if response.status_code == 200:
                weather_data = response.json()
                temperature_celsius = round(weather_data['main']['temp'] - 273.15, 2)
                return render_template('result.html', weather=weather_data, temperature=temperature_celsius)
            else:
                return "Location not found. Please try again."

        return "Please enter a city name."

    return render_template('search.html')


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/login", methods=["POST", "GET"])
def login():
    if request.method == "POST":
        user = request.form["nm"]
        return redirect(url_for("user", usr=user))
    else:
        return render_template("login.html")


@app.route("/<usr>")
def user(usr):
    return f"<h1>{usr}</h1>"


# adding a weather route to pair link to base html's "Locations" button for a drop-down list of blogger locations:
@app.route('/weather', methods=['GET', 'POST'])
def weather():
    form = LocationForm()
    # had to ensure form was validated for method to be allowed:
    if form.validate_on_submit():
        selected_location = form.location.data
        selected_lat = locations[selected_location]['lat']
        selected_lng = locations[selected_location]['lng']

        # Using the OpenWeather API to fetch weather data with a new API key:
        api_endpoint = "http://api.openweathermap.org/data/2.5/weather"
        params = {
            'lat': selected_lat,
            'lon': selected_lng,
            'appid': weather_key,
            'units': 'metric'  # making sure the temp is in celcius: this took a while!
        }
        response = requests.get(api_endpoint, params=params)

        if response.status_code == 200:
            weather_data = response.json()
            temperature = weather_data['main']['temp']
            forecast = weather_data['weather'][0]['description']
            return render_template('weather.html', form=form, selected_location=selected_location,
                                   selected_lat=selected_lat, selected_lng=selected_lng, temperature=temperature,
                                   forecast=forecast)  # access attributes
        else:
            error_message = "Failed to fetch weather information"
            return render_template('weather.html', form=form, error_message=error_message)

    return render_template('weather.html', form=form)


# Endpoint for the chatbot:
@app.route('/chatbox_data', methods=['POST'])
def chatbot_data():
    data = request.get_json()

    # Extract city from the request
    city = data.get('city')

    # If city is provided, pull the weather information from API and jsonify:
    if city:
        weather_data = get_chat_data(city)
        return jsonify({'response': weather_data})
    else:
        return jsonify({'response': 'Please provide a city in the request.'})


def get_chat_data(city):  # Checking if weather data for the city is already in the database:
    weather_record = Weather_Model.query.filter_by(city=city).first()
    if weather_record:
        return f'The weather in {city} is {weather_record.description}. Temperature: {weather_record.temperature}°C, Humidity: {weather_record.humidity}%.'
    # If not in the database, fetch from the API:
    url = f'http://api.openweathermap.org/data/2.5/weather?q={city}&appid={API_KEY2}'

    try:
        response = requests.get(url)
        data = response.json()

        if response.status_code == 200:
            # Extract relevant weather information
            description = data['weather'][0]['description']
            temperature = data['main']['temp']
            humidity = data['main']['humidity']

            # Save the data to the database
            new_weather = Weather_Model(city=city, description=description, temperature=temperature, humidity=humidity)
            db.session.add(new_weather)
            db.session.commit()

            return f'The weather in {city} is {description}. Temperature: {temperature}°C, Humidity: {humidity}%.'
        else:
            return "Whoops- that\'s an error! Please try again"
    except Exception as e:
        return f'An error occurred: {str(e)}'


# Registering Swagger documentation blueprint
##SWAGGER_URL = '/api/docs'  # URL for exposing Swagger UI (without trailing '/')
#API_URL = '/static/swagger.json'  # URL for accessing the API documentation
#swagger_blueprint = swagger_ui_blueprint(
    #SWAGGER_URL,
    #API_URL,
    #config={
       # 'app_name': "Your API Documentation"
    #}
#)
#app.register_blueprint(swagger_blueprint, url_prefix=SWAGGER_URL)

with app.app_context():
    if __name__ == "__main__":
        #db.create_all()
        app.run(debug=True)
