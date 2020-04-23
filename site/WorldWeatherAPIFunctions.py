from requests import get
from flask import Flask, render_template
import requests
import json, re, sys, argparse, os
from datetime import datetime

BASE_URL =  "https://api.worldweatheronline.com/premium/v1/past-weather.ashx"
API_KEY = "16368c2965dc4d5796d51643202104"

def getHistoricData(cityName, date):
    cityName = cityName.replace(" ", "+")
    historicalData = requests.get(BASE_URL + '?q=' + cityName + '&date=' + date + '&format=json' + '&key=' + API_KEY).json()
    historicalData['data']['weather'][0]['hourly'][4]['weatherCode'] = getWeatherIcon(historicalData['data']['weather'][0]['hourly'][4]['weatherCode'])
    return historicalData

def getWeatherIcon(code):
    code = str(code)
    if ((code == "386") or (code == "392") or (code == "200")):
        return "fa-bolt"
    elif ((code == "389") or (code == "377") or (code == "368")):
        return "fa-cloud-showers-heavy"
    elif ((code == "362") or (code == "359") or (code == "356")):
        return "fa-cloud-showers-heavy"
    elif ((code == "353") or (code == "314") or (code == "311")):
        return "fa-cloud-showers-heavy"
    elif ((code == "308") or (code == "305") or (code == "302")):
        return "fa-cloud-showers-heavy"
    elif ((code == "299") or (code == "296") or (code == "293")):
        return "fa-cloud-showers-heavy"
    elif ((code == "284") or (code == "281") or (code == "266") or (code == "263")):
        return "fa-cloud-showers-heavy"
    elif ((code == "395") or (code == "374") or (code == "371")):
        return "fa-snowflake"
    elif ((code == "365") or (code == "350") or (code == "338")):
        return "fa-snowflake"
    elif ((code == "335") or (code == "332") or (code == "329")):
        return "fa-snowflake"
    elif ((code == "326") or (code == "323") or (code == "320")):
        return "fa-snowflake"
    elif ((code == "317") or (code == "230") or (code == "227")):
        return "fa-snowflake"
    elif ((code == "260") or (code == "248") or (code == "119") or (code == "116")):
        return "fa-cloud-sun"
    elif ((code == "185") or (code == "182") or (code == "179")):
        return "fa-cloud-sun"
    elif ((code == "176") or (code == "143") or (code == "122")):
        return "fa-cloud"
    elif ((code == "113")):
        return "fa-sun"

if __name__ == "__main__":
    print(getFutureData("Sydney"))