from flask import Flask, render_template, request, jsonify
from AccuWeatherAPIFunctions import *
from WorldWeatherAPIFunctions import *

app = Flask(__name__)

@app.route("/", methods=['GET', 'POST'])
def home():
    cityList = getListOfCities(getLocationFromIP(get_ip()))
    city_info = dashboardData(cityList)
    return render_template("index.html", city_info=city_info)

@app.route("/country/<country>", methods=['GET', 'POST'])
def country(country):
    newCountry = normaliseCountry(country)
    cityList = getListOfCities(newCountry)
    city_info = dashboardData(cityList)
    return render_template("index.html", city_info=city_info)

@app.route("/location/<cityName>", methods=['GET', 'POST'])
def location(cityName):
    locationKey = getKey(cityName)
    name = getCityName(locationKey)
    current_conditions = getCurrentConditions(locationKey)
    hourly = get12HourForecast(locationKey)
    currDay = get1DayForecast(locationKey)
    daily = get5DayForecast(locationKey)
    indices = getIndices(locationKey)
    return render_template("locationPage.html", current_conditions=current_conditions[0], city_name=name, hourly=hourly, daily=daily, currDay=currDay, indices=indices)

@app.route("/location", methods=['GET', 'POST'])
def searchLocation():
    default_name = '0'
    cityName = request.form.get('myCity', default_name)
    locationKey = getKey(cityName)
    name = getCityName(locationKey)
    current_conditions = getCurrentConditions(locationKey)
    hourly = get12HourForecast(locationKey)
    currDay = get1DayForecast(locationKey)
    daily = get5DayForecast(locationKey)
    indices = getIndices(locationKey)
    return render_template("locationPage.html", current_conditions=current_conditions[0], city_name=name, hourly=hourly, daily=daily, currDay=currDay, indices=indices)

@app.route("/historical/<cityName>", methods=['GET', 'POST'])
def historicalData(cityName):
    default_date = '0'
    date = request.form.get('myDate', default_date)
    historicalData = getHistoricData(cityName, date)
    return render_template("historicalLocation.html", historicalData=historicalData)

@app.errorhandler(404)
def page_not_found(e):
    # note that we set the 404 status explicitly
    return render_template('error.html', e=e), 404

@app.errorhandler(403)
def page_not_found(e):
    # note that we set the 403 status explicitly
    return render_template('error.html', e=e), 403

@app.errorhandler(410)
def page_not_found(e):
    # note that we set the 410 status explicitly
    return render_template('error.html', e=e), 410

@app.errorhandler(500)
def page_not_found(e):
    # note that we set the 500 status explicitly
    return render_template('error.html', e=e), 500


if __name__ == "__main__":
    app.run(debug=True)