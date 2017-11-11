from flask import Flask, Response, jsonify
from datetime import datetime
from dateutil import relativedelta
import requests
import config

app = Flask(__name__)

@app.route('/')
def startpage():
    """The start page for the server."""
    return Response('Skyhook\'s custom API Server.', mimetype='text/plain')

@app.route('/weather')
def get_weather():
    """Pulls Weather Data from Weather Underground: Currently only works for one location."""
    try:
        result = requests.get('http://api.wunderground.com/api/' + config.wukey + '/geolookup/conditions/q/pws:IBRITISH434.json')
        try:
            weather = result.json()
        except Exception as err:
            return Response('Weather API did not return any JSON data!', mimetype='text/plain')
    except requests.exceptions.RequestException as err:
        return Response('Failed to connect to weather API!', mimetype='text/plain')

    try:
        weather_desc = weather['current_observation']['weather']
        temp_c = weather['current_observation']['temp_c']
        temp_f = weather['current_observation']['temp_f']
        wind_kmh = weather['current_observation']['wind_kph']
        wind_kmh_gust = weather['current_observation']['wind_gust_kph']
    except Exception as err:
        return Response('Failed to pull weather data! Usually caused by an incorrect API key.', mimetype='text/plain')

    weather_full = '%s with a temperature of %s°C (%s°F)' % (str(weather_desc), str(temp_c), str(temp_f))

    if float(wind_kmh_gust) > 0:
        weather_full = '%s. Wind is currently blowing at %skm/h with gusts of %skm/h.' % (str(weather_full), str(wind_kmh), str(wind_kmh_gust))
    elif float(wind_kmh) > 0:
        weather_full = '%s. Wind is currently blowing at %skm/h.' % (str(weather_full), str(wind_kmh))
    else:
        weather_full = '%s. There is curently no wind.' % str(weather_full)

    return Response(weather_full, mimetype='text/plain')

@app.route('/convert/<unit_one>/<unit_two>/<value>')
def convert(unit_one,unit_two,value):
    """Will be a conversion function to convert units of distance, etc. Currently not being used."""
    return Response('Unit One: ' + unit_one + ' Unit Two: ' + unit_two + ' Value: ' + value, mimetype='text/plain')

@app.route('/glitch/getid/<username>')
def get_twitch_id(username):
    """Will return the userid of a username on Twitch."""
    return Response('Username: ' + username, mimetype='text/plain')

@app.route('/glitch/getuser/<userid>')
def get_twitch_user(userid):
    """Will return user information from the userid given."""
    return Response('User ID: ' + userid, mimetype='text/plain')

@app.route('/glitch/followage/<channelname>/<username>')
def get_followage(channelname,username):
    """Get how long someone has been following a certain channel."""
    channelid = twitch_getid(channelname)
    userid = twitch_getid(username)
    test = twitch_followage(channelid,userid)

#   return Response('Channel Name: ' + channelname + ' User Name: ' + username + ' Channel ID: ' + channelid + ' User ID: ' + userid, mimetype='text/plain')
    return Response('Test: ' + test, mimetype='text/plain')

@app.route('/glitch/subage/<oauth>/<channelname>/<username>')
def get_subage(oauth,channelname,username):
    """Get how long someone has been subbed a certain channel."""
    return Response('OAuth Key: ' + oauth + ' Channel Name: ' + channelname + ' User Name: ' + username, mimetype='text/plain')

@app.route('/glitch/test')
def glitch_test():
    """Testing for date and time differences"""

    #Aug 7 1989 8:10 pm
    date_1 = datetime(1989, 8, 7, 20, 10)

    #Dec 5 1990 5:20 am
    date_2 = datetime(1990, 12, 5, 5, 20)

    difference = relativedelta.relativedelta(date_2, date_1)

    years = difference.years
    months = difference.months
    days = difference.days
    hours = difference.hours
    minutes = difference.minutes

    return Response("Difference is " + str(years) + " years " + str(months) + " months " + str(days) + " days " + str(hours) + " hours " + str(minutes) + " minutes.", mimetype='text/plain')

@app.errorhandler(404)
def page_not_found(error):
    """404 Error Handling function. Just returns a plaintext error."""
    return Response('404 Error: Bad API call.', mimetype='text/plain')

def twitch_getid(username):
    """Gets Twitch ID by their username."""
    try:
        url = 'https://api.twitch.tv/helix/users?login=%s' % username
        headers = {'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)

        try:
            request = request.json()
        except Exception as err:
            return('Failed to format JSON data from Twitch!')

    except requests.exceptions.RequestException as err:
        return('Failed to connect to Twitch API server.')
    
    try:
        result = request['data'][0]['id']
    except Exception as err:
        result = 'No user with that name found!'

    return (result)

def twitch_followage(channelid,userid):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid,channelid)
        headers = {'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return('Failed to format JSON data from Twitch!')
    except requests.exceptions.RequestException as err:
        return('Failed to connect to Twitch API server.')

    try:
        result = request['data'][0]['followed_at']
        formatted_date = datetime.strptime( result, "%Y-%m-%dT%H:%M:%SZ" )
        try:
            currentdate = datetime.utcnow()
            difference = relativedelta.relativedelta(currentdate,formatted_date)

            years = difference.years
            months = difference.months
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes

            return "%s years %s months %s days %s hours %s minutes" % (years,months,days,hours,minutes)
        except Exception as err:
            return 'An error occured in the date comparison.'
    except Exception as err:
        return 'User is not following this channel.'

    return ('An error occured in the lookup.')