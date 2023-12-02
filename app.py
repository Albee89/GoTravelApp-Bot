#!/usr/bin/env python3.7

#importing a lot of libraries:
from flask import Flask, render_template, request, redirect, jsonify, url_for, g
import requests
from dotenv import load_dotenv
from flask_wtf import FlaskForm
from wtforms import SelectField, SubmitField
from wtforms.validators import InputRequired
import os
from chatterbot import ChatBot
from chatterbot.trainers import ChatterBotCorpusTrainer
import sqlite3
import pandas as pd
from io import StringIO

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



# Database setup
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect('alex_b.db')
    return db




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


# Importing the CSV files/reading CSV into DataFrame
locations_list = pd.read_csv('blog_locations.csv')

# Viewing the DF:
print(locations_list.shape)
print(locations_list.head())


# Initialize Flask app
app = Flask(__name__)

# Set the secret key in your Flask app config
load_dotenv("venv/weather1.env")
load_dotenv("venv/google.env")
load_dotenv("venv/weather_3.env")
load_dotenv("venv/we2.env")
load_dotenv("venv/secret.env")
load_dotenv("../.env")

# Retrieve API keys from the environment, access variable, with a default value if not found on SECRET_KEY:
API_key = os.getenv("weather_api")
google_API = os.getenv("google_API")
weather_key = os.getenv("weather_3")
API_KEY2 = os.getenv("API_KEY2")
SECRET_KEY = os.environ.get('SECRET_KEY', 'abc123ced456')
chatbot_weather = os.getenv("chatbot_weather")


app.config['SECRET_KEY'] = SECRET_KEY


# Creating a chatbot instance:
my_bot= ChatBot(
    name="Allie",
    read_only=True,
    storage_adapter='chatterbot.storage.SQLStorageAdapter', database_uri='sqlite:///database.sqlite3',
    logic_adapters=["chatterbot.logic.MathematicalEvaluation", "chatterbot.logic.BestMatch"])


# Create a new trainer
trainer = ChatterBotCorpusTrainer(my_bot)

# Train the chatbot (you can customize this based on your needs)
trainer.train("chatterbot.corpus.english")
trainer.train("chatterbot.corpus.english.conversations")



# Insert sample data into the responses table
#cursor.execute("INSERT INTO weather_appy_data (keyword, response) VALUES (?, ?)", ('hello', 'Hi there!'))
#cursor.execute("INSERT INTO responses (keyword, response) VALUES (?, ?)", ('goodbye', 'Goodbye!'))
# Create the responses table if it doesn't exist

##########Connect to the database ###################

# Read data from CSV file using pandas
locations_df = pd.read_csv('blog_locations.csv')

conn = sqlite3.connect('ab_db.db')
cursor = conn.cursor()

# Creating the table if it doesn't exist
cursor.execute('''
    CREATE TABLE IF NOT EXISTS appy_bot_chat (
        name TEXT,
        temp FLOAT,
        datetime TEXT
    )
''')

# Iterate through rows and insert data into the database
for index, row in locations_df.iterrows():
    name = row['name']
    temperature = row['temp']
    datetime = row['datetime']
    conn.cursor()

    # Executing INSERT query:
    cursor.execute("INSERT INTO appy_bot_chat (name, temp, datetime) VALUES (?, ?, ?)", (name, temperature, datetime))

# Committing changes:
conn.commit()


@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        if not user_input:
            return jsonify({'error': 'User input parameter is required'}), 400

        # Executing chatbot logic:
        bot_response = str(my_bot.get_response(user_input))

        # Closing connection:
        conn.close()

        return render_template('index.html', chatbot_response=bot_response)

    # Handle GET requests if needed
    return render_template('index.html')


@app.route("/")
def home():
    return render_template("base.html")



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

#closing down the app after use:
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# closing out the flask app:
with app.app_context():
    if __name__ == "__main__":
        app.run(debug=True)



