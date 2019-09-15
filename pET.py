import os
import pyeto
from pyeto import fao
import requests
import json
import ast
import boto3
from boto3.dynamodb.conditions import Key
import datetime, time
import framework
import cropET
import traceback

try:
    from . import conversion
except:
    import conversion # "__main__" case

def pet(event,context):

    latitude = event['latitude']
    print("Latitude: " + str(latitude))

    longitude = event['longitude']
    print("Longitude: " + str(longitude))

    if latitude is None or longitude is None:
        print("Unknown lat/lng")
        return {}
    if latitude == 0 and longitude == 0:
        print("Zeroed lat/lng")
        return {}

    lat = pyeto.deg2rad(latitude)
    # convert lat to radians
    #pass google maps api info
    mapKey = os.environ['GOOGLE_MAPS_API_KEY']
    #pass lat/long and API key variables
    GOOGLE_MAPS_API = 'https://maps.googleapis.com/maps/api/elevation/json?locations='+str(latitude)+','+str(longitude)+'&key='+str(mapKey)
    # Test: curl 'https://maps.googleapis.com/maps/api/elevation/json?locations=29.405708,-82.140176&key='
    req = requests.get(GOOGLE_MAPS_API)
    res = req.json()

    if res['status']=='REQUEST_DENIED':
        print(f"Error: Google Maps API request denied. {res['error_message']}")
        return {}

    results = res["results"]

    if len(results)==0:
        print(f"Error: Google Maps API request returned no results. Status: {res['status']}, Error: {res['error_message']}")
        return {}

    #print(results)
    #ELEVATION / ALTITUDE DATA
    alt = results[0]['elevation']

    deviceName = event['deviceName']
    print("deviceName: " + str(deviceName))

    #set table parameters for sensor data
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table(os.environ['READINGS_TABLE_NAME'])
    # time parameters
    current_time = datetime.datetime.now(datetime.timezone.utc)
    unix_timestamp = current_time.timestamp()
    # remove decimal when passing in unix timestamp
    currentTime = int(unix_timestamp)
    #1440 minutes in a day * 60 seconds
    #format timestamp to remove float...
    dayPast = int(unix_timestamp - (1440*60))

    # let's sample air temperature now
    tempSample = table.query(
        ReturnConsumedCapacity='TOTAL',
        ProjectionExpression="weatherData.temperature",
        KeyConditionExpression=Key('deviceName').eq(deviceName) & Key('epoch').between(dayPast, currentTime)
    )
    tempList = [conversion.obj_to_json(i) for i in tempSample[u'Items']]
    #print(tempList)
    day1Temp = [ast.literal_eval(tempList[i]) for i in range(len(tempList))]
    #print(day1Temp)
    day1TempFormat = []
    for dic in day1Temp:
        for val in dic.values():
            #print(val['temperature'])
            day1TempFormat.append(val['temperature'])
    print(day1TempFormat)
    #  calculate temperature avg, min, max for last 24 hrs
    # convert to Celcius because default from DarkSky is F
    tempListLength = len(day1TempFormat)
    print("Temp List Length: " + str(tempListLength))
    day1TempAvg = 0
    day1TempMin = 0
    day1TempMax = 0
    if tempListLength != 0:
        day1TempAvg = round(sum(day1TempFormat)/tempListLength,2)
        day1TempAvg = round((day1TempAvg - 32) * (5/9), 2)
        day1TempMin = min(day1TempFormat)
        day1TempMin = round((day1TempMin - 32) * (5/9), 2)
        day1TempMax = max(day1TempFormat)
        day1TempMax = round((day1TempMax - 32) * (5/9), 2)

    print("Temp Avg (C): " + str(day1TempAvg))
    print("Temp Min (C): " + str(day1TempMin))
    print("Temp Max (C): " + str(day1TempMax))

    # calculate dew point average
    dewSample = table.query(
    ReturnConsumedCapacity='TOTAL',
    ProjectionExpression="weatherData.dewPoint",
    KeyConditionExpression=Key('deviceName').eq(deviceName) & Key('epoch').between(dayPast,currentTime)
    )

    dewList = [conversion.obj_to_json(i) for i in dewSample[u'Items']]
    day1Dew = [ast.literal_eval(dewList[i]) for i in range(len(dewList))]
    day1DewFormat = []
    for dic in day1Dew:
        for val in dic.values():
            day1DewFormat.append(val['dewPoint'])
    #print(day1DewFormat)
    dewListLength = len(day1DewFormat)
    print("Dew List Length: " + str(dewListLength))
    day1DewAvg = 0
    if dewListLength != 0:
        day1DewAvg = round(sum(day1DewFormat)/dewListLength, 2)
    # convert F to C (F-32) x 5/9
    #AVERAGE ACTUAL DAILY VAPOUR PRESSURE
    day1DewAvg = round((day1DewAvg - 32) * (5/9), 2)
    print("Dew Point Avg (C): " + str(day1DewAvg))
    # dew point is temp at which concentration of water vapour in air at concentration, convert to C down below because DarkSky is F
    # now calculate wind speed
    windSample = table.query(
    ReturnConsumedCapacity='TOTAL',
    ProjectionExpression="weatherData.windSpeed",
    KeyConditionExpression=Key('deviceName').eq(deviceName) & Key('epoch').between(dayPast,currentTime)
    )

    windList = [conversion.obj_to_json(i) for i in windSample[u'Items']]
    day1Wind = [ast.literal_eval(windList[i]) for i in range(len(windList))]
    day1WindFormat = []
    for dic in day1Wind:
        for val in dic.values():
            day1WindFormat.append(val['windSpeed'])

    windListLength = len(day1WindFormat)
    #print(windListLength)
    if windListLength <= 0:
        windListLength = 1
    day1windSpeed = round(sum(day1WindFormat)/windListLength,2)
    print("Wind Speed (knots): " + str(day1windSpeed))

    #HUMIDITY
    # pull in dewpoint temperature data from DarkSky
    vaporPressure = fao.avp_from_tdew(day1DewAvg)
    #SATURATION VAPOUR --> estimated from air temperature
    satVapor = fao.svp_from_t(day1TempAvg)
    #SLOPE OF SATURATION VAPOR CURVE
    satVaporSlope = fao.delta_svp(day1TempAvg)

    #ATMOSPHERIC PRESSURE
    atmosphericPressure = fao.atm_pressure(alt)
    #PSYCHOMETRIC CONSTANT - Eq 8 Allen, 1998
    psychroConstant = fao.psy_const(atmosphericPressure)

    #RADIATION
    #day of year
    day_of_year = time.localtime().tm_yday
    #DAILY NET RADIATION
    #SOLAR DECLINATION  - FAO equation 24
    sol_declination = fao.sol_dec(day_of_year)
    # SUNSET HOUR ANGLE
    sunsetHourAngle = fao.sunset_hour_angle(lat, sol_declination)
    #calculate daylight hours
    daylightHours = fao.daylight_hours(sunsetHourAngle)
    #inverse rel distance - sun-earth
    earthSunDist = fao.inv_rel_dist_earth_sun(day_of_year)

    # ESTIMATED DAILY EXTRATERRESTRIAL RADIATION (top of atmosphere)
    # Eq 21 (Allen et al 1998)
    #def et_rad(latitude, sol_dec, sha, ird):
    extraTerRad = fao.et_rad(lat, sol_declination, sunsetHourAngle, earthSunDist)

    #ESTIMATED CLEAR SKY RADIATION
    # Eq 37 Allen et al 1998)
    clearSkyRad = fao.cs_rad(alt,extraTerRad)
    #daily min and max temperatures expressed as degrees C
    grossRadiation = fao.sol_rad_from_t(extraTerRad, clearSkyRad, day1TempMin, day1TempMax, coastal=False)

    #NET INCOMING SOLAR  (shortwave rad) --> FAO equation 38
    #albedo is of crop as proporiton of gross incoming solar radiation reflected by surgace --> 0.23 default set by FAO for grass crop
    #incomingRadiation = net_in_sol_rad(sol_rad, albedo=0.23)
    netIncomingRad = fao.net_in_sol_rad(grossRadiation, albedo=0.23)

    #NET OUTGOING LONGWAVE ENERGY leaving earth's surface (Eq 39 in Allen et al 1998)
    # def net_out_lw_rad(tmin, tmax, sol_rad, cs_rad, avp)
    netOutgoingRad = fao.net_out_lw_rad(day1TempMin, day1TempMax, grossRadiation, clearSkyRad, vaporPressure)

    #DAILY NET RADIATION AT CROP SURCACE (assuming grass ref crop)
    #Eq 40 in Allen et al (1998)
    dailyNetRadiation = fao.net_rad(netIncomingRad,netOutgoingRad)

    #convert air temp from C to degrees Kelvin
    day1TempAvg = day1TempAvg + 273.15

    #FAO-56 ENMAN-MONTIETCH EQUATION to estimate reference evapotranspiration (ETo) from short grass reference surface
    # Eq 6 in Allen et al 1998
    #def fao56_penman_monteith(net_rad, t, ws, svp, avp, delta_svp, psy, shf=0.0):

    penmanMontOutput = round(fao.fao56_penman_monteith(dailyNetRadiation, day1TempAvg, day1windSpeed, satVapor, vaporPressure, satVaporSlope, psychroConstant, shf=0.0),2)

    print("Reference ETo [mm/day]: " + str(penmanMontOutput))
    # convert from mm/day to in/day
    pET = round((penmanMontOutput * 0.0393701),4)
    if pET <= 0:
        pET = 0
    # now multiply by crop coefficients to find ETc (crop evapotranspiration)
    ret = {
        "ETo": pET
    }

    try:
        ETc = None # Default value if missing or error
        cc = cropET.calculateCropCoef(deviceName)
        if cc is not None:
            Kc = cc["KcMAIN"]
            cropName = cc["cropName"]
            if Kc is not None:
                ETc =  round((pET*Kc),4)

            ret.update({
                "ETc": ETc,
                "crop": cropName
            })
    except:
        traceback.print_exc()

    return ret

def main(event, context):
    return framework.execute_function(pet, event, context)

if __name__ == "__main__":
    pet({}, {})
