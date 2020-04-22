from requests import get
from flask import Flask, render_template
import requests
import json, re, sys, argparse, os
from datetime import datetime
import dateutil.parser as parser

# API_KEY = "8GGqTVDqQc6P5lg3TtgT8artGzWtA9tV"
# API_KEY = "XIUiYTK02GACGyPukXAD8PGRddL8VMAM"
# API_KEY = "HvaEC8gFXcCL0VApPv7JeS5OwylGkuWc"
# API_KEY = "AIzaSyB1y6B6yEeGqFVGFj2An3u56_sqVVMu5sw"
# API_KEY = "zSrzFTRB2rQokEaHDLVRvk8Fn8p1UIdh"
API_KEY = "8eGiOWuWKXOJxpL8n2lAK8CzeWKRp6JF"

def get_ip():
    ip = get('https://api.ipify.org').text
    return ip

def normaliseCountry(country):
    string = country.replace("_", " ")
    return string

def getKey(city):
    response = requests.get("http://dataservice.accuweather.com/locations/v1/cities/search?apikey=" + API_KEY + "&q=" + city)
    json_data = json.loads(response.text)
    return json_data[0]["Key"]

def getLocationFromIP(ip):
    response = requests.get("http://dataservice.accuweather.com/locations/v1/cities/ipaddress?apikey=" + API_KEY + "&q=" + ip)
    json_data = json.loads(response.text)
    return json_data["Country"]["EnglishName"]

def getListOfCities(countryName):
    response = requests.get("http://dataservice.accuweather.com/locations/v1/topcities/150?apikey=" + API_KEY)
    json_data = json.loads(response.text)

    cityList = []
    for location in json_data:
        cityDict = {}
        cityDict.fromkeys(['name', 'locationKey', 'temp', 'tempUnit', 'feelsLike', 'minTemp', 'minTempTime', 'maxTemp', 'maxTempTime'], 0)
        if (location["Country"]["EnglishName"] == countryName):
            cityDict['name'] = location["EnglishName"]
            cityList.append(cityDict)
    return cityList

def getCityName(locationKey):
    response = requests.get("http://dataservice.accuweather.com/locations/v1/" + locationKey + "?apikey=" + API_KEY)
    json_data = json.loads(response.text)
    return json_data

def dashboardData(cityList):
    newList = []
    for i in cityList:
        locationKey = getKey(i['name'])
        json_data = getCurrentConditions(locationKey)
        newDict = dict().fromkeys(("Name", "Icon", "TempVal", "TempUnit", "TempFeel", "Description"), None)
        newDict["Name"] = i['name']
        newDict["Icon"] = getWeatherIcon(json_data[0]["WeatherIcon"])
        newDict["TempVal"] = str(json_data[0]["Temperature"]["Metric"]["Value"])
        newDict["TempUnit"] = str(json_data[0]["Temperature"]["Metric"]["Unit"])
        newDict["TempFeel"] = str(json_data[0]["RealFeelTemperature"]["Metric"]["Value"])
        newDict["Description"] = str(json_data[0]["WeatherText"])
        newList.append(newDict)
    return newList

def getCurrentConditions(locationKey):
    response = requests.get("http://dataservice.accuweather.com/currentconditions/v1/" + locationKey + "?apikey=" + API_KEY + "&details=true")
    json_data = json.loads(response.text)

    formattedTime = str(formatDateTime(json_data[0]["LocalObservationDateTime"], "T"))
    json_data[0]["LocalObservationDateTime"] = formattedTime[:-5] + "00"
    
    return json_data

def get12HourForecast(locationKey):
    response = requests.get("http://dataservice.accuweather.com/forecasts/v1/hourly/12hour/" + locationKey + "?apikey=" + API_KEY + "&details=true&metric=true")
    json_data = json.loads(response.text)

    for i in range(0, 12):
        formattedTime = str(formatDateTime(json_data[i]["DateTime"], "T"))
        json_data[i]["DateTime"] = formattedTime[:-3]

        icon = getWeatherIcon(json_data[i]["WeatherIcon"])
        json_data[i]["WeatherIcon"] = icon

    return json_data

def get1DayForecast(locationKey):
    response = requests.get("http://dataservice.accuweather.com/forecasts/v1/daily/1day/" + locationKey + "?apikey=" + API_KEY + "&details=true&metric=true")
    json_data = json.loads(response.text)

    # Change times to correct format
    moonRise = str(formatDateTime(json_data["DailyForecasts"][0]["Moon"]["Rise"], "T"))
    json_data["DailyForecasts"][0]["Moon"]["Rise"] = moonRise[:-3]
    moonSet = str(formatDateTime(json_data["DailyForecasts"][0]["Moon"]["Set"], "T"))
    json_data["DailyForecasts"][0]["Moon"]["Set"] = moonSet[:-3]

    sunRise = str(formatDateTime(json_data["DailyForecasts"][0]["Sun"]["Rise"], "T"))
    json_data["DailyForecasts"][0]["Sun"]["Rise"] = sunRise[:-3]
    sunSet = str(formatDateTime(json_data["DailyForecasts"][0]["Sun"]["Set"], "T"))
    json_data["DailyForecasts"][0]["Sun"]["Set"] = sunSet[:-3]

    moonPhase = str(json_data["DailyForecasts"][0]["Moon"]["Phase"])
    newPhase = ""
    for k in range(1, len(moonPhase)):
        if (moonPhase[k].isupper()):
            newPhase = moonPhase[:k] + " " + moonPhase[k:]
    json_data["DailyForecasts"][0]["Moon"]["Phase"] = str(newPhase)
    

    newDate = str(formatDateTime(json_data["DailyForecasts"][0]["Date"], "D"))
    json_data["DailyForecasts"][0]["Weekday"] = str(getWeekday(json_data["DailyForecasts"][0]["Date"]))
    json_data["DailyForecasts"][0]["Date"] = newDate
    
    icon = getWeatherIcon(json_data["DailyForecasts"][0]["Day"]["Icon"])
    json_data["DailyForecasts"][0]["Day"]["Icon"] = icon

    return json_data

def get5DayForecast(locationKey):
    response = requests.get("http://dataservice.accuweather.com/forecasts/v1/daily/5day/" + locationKey + "?apikey=" + API_KEY + "&details=true&metric=true")
    json_data = json.loads(response.text)

    # Change times to correct format
    for i in range(0, 5):
        first = json_data["DailyForecasts"][i]["Temperature"]["Minimum"]["Value"]
        second = json_data["DailyForecasts"][i]["Temperature"]["Maximum"]["Value"]
        json_data["DailyForecasts"][i]["Temperature"]["Average"] = str((first + second) / 2)

        moonRise = str(formatDateTime(json_data["DailyForecasts"][i]["Moon"]["Rise"], "T"))
        json_data["DailyForecasts"][i]["Moon"]["Rise"] = moonRise[:-3]
        moonSet = str(formatDateTime(json_data["DailyForecasts"][i]["Moon"]["Set"], "T"))
        json_data["DailyForecasts"][i]["Moon"]["Set"] = moonSet[:-3]

        sunRise = str(formatDateTime(json_data["DailyForecasts"][i]["Sun"]["Rise"], "T"))
        json_data["DailyForecasts"][i]["Sun"]["Rise"] = sunRise[:-3]
        sunSet = str(formatDateTime(json_data["DailyForecasts"][i]["Sun"]["Set"], "T"))
        json_data["DailyForecasts"][i]["Sun"]["Set"] = sunSet[:-3]

        moonPhase = str(json_data["DailyForecasts"][i]["Moon"]["Phase"])
        newPhase = ""
        for k in range(1, len(moonPhase)):
            if (moonPhase[k].isupper()):
                newPhase = moonPhase[:k] + " " + moonPhase[k:]
        json_data["DailyForecasts"][i]["Moon"]["Phase"] = str(newPhase)
        

        newDate = str(formatDateTime(json_data["DailyForecasts"][i]["Date"], "D"))
        json_data["DailyForecasts"][i]["Weekday"] = str(getWeekday(json_data["DailyForecasts"][i]["Date"]))
        json_data["DailyForecasts"][i]["Date"] = newDate
        
        icon = getWeatherIcon(json_data["DailyForecasts"][i]["Day"]["Icon"])
        json_data["DailyForecasts"][i]["Day"]["Icon"] = icon

    return json_data

def getWeatherIcon(icon):
    description = str(icon)
    description = description.strip()
    if ((description == "1") or (description == "2") or (description == "3") or (description == "4")):
        return "fa-sun"
    elif ((description == "5") or (description == "6")):
        return "fa-cloud-sun"
    elif ((description == "7") or (description == "8") or (description == "11")):
        return "fa-cloud"
    elif ((description == "12") or (description == "13") or (description == "14") or (description == "18") or (description == "26") or (description == "29") or (description == "39") or (description == "40")):
        return "fa-cloud-showers-heavy"
    elif ((description == "15") or (description == "16") or (description == "17") or (description == "41") or (description == "42")):
        return "fa-bolt"
    elif ((description == "19") or (description == "20") or (description == "21") or (description == "22") or (description == "23") or (description == "24") or (description == "25") or (description == "43") or (description == "44")):
        return "fa-snowflake"
    elif (description == "30"):
        return "fa-thermometer-full"
    elif (description == "31"):
        return "fa-temperature-low"
    elif (description == "32"):
        return "fa-wind"
    elif ((description == "33") or (description == "34") or (description == "35") or (description == "36") or (description == "37") or (description == "38")):
        return "fa-moon"
    else:
        return "fa-cloud"
    
def formatDateTime(oldTime, choice):
    # T for time, or D for date
    if (choice == "T"):
        newTime = parser.parse(oldTime)
        return newTime.time()
    elif (choice == "D"):
        newDate = parser.parse(oldTime)
        return newDate.date().strftime("%x")

def getWeekday(oldTime):
    newDate = parser.parse(oldTime)
    day = newDate.date().weekday()
    if (day is 0):
        return "MON"
    elif (day is 1):
        return "TUE"
    elif (day is 2):
        return "WED"
    elif (day is 3):
        return "THU"
    elif (day is 4):
        return "FRI"
    elif (day is 5):
        return "SAT"
    elif (day is 6):
        return "SUN"

def getIndices(locationKey):
    response = requests.get("http://dataservice.accuweather.com/indices/v1/daily/1day/" + locationKey + "?apikey=" + API_KEY + "&details=true")
    json_data = json.loads(response.text)
    json_data = sorted(json_data, key = lambda i: i['Value'])
    newList = []

    for i in range(0, len(json_data)):
        json_data[i]['Name'] = json_data[i]['Name'].replace(" Forecast", "")
        json_data[i]['Name'] = json_data[i]['Name'].replace(" Weather", "")
        if ((json_data[i]['ID'] is 10) or (json_data[i]['ID'] is 4) or (json_data[i]['ID'] is 13) or (json_data[i] is 5) or (json_data[i] is 16) or (json_data[i]['ID'] is 3) or (json_data[i]['ID'] is 20) or (json_data[i]['ID'] is -2) or (json_data[i]['ID'] is 24) or (json_data[i]['ID'] is 28) or (json_data[i]['ID'] is 29) or (json_data[i]['ID'] is 24) or (json_data[i]['ID'] is 8) or (json_data[i]['ID'] is 1) or (json_data[i]['ID'] is 6) or (json_data[i]['ID'] is 11) or (json_data[i]['ID'] is 39) or (json_data[i]['ID'] is 7) or (json_data[i]['ID'] is 15) or (json_data[i]['ID'] is 12)):
            newList.append(json_data[i]['Name'])
    return newList


# if __name__ == "__main__":
#     # print(get1DayForecast("227342"))
#     print(getIndices("274663"))
#     print(formatDateTime("2020-04-17T05:10:00+03:00", "D"))
#     print(getWeekday("2020-04-17T05:10:00+03:00"))
    # print(get5DayForecast("227342"))
    # cityList = getListOfCities("Australia")
    # print(getListOfCities("Australia"))
    # print(dashboardData(cityList))