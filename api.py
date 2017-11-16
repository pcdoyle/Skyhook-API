"""
Skyhook-API
Copyright 2017: Patrick Doyle. (KaoAtlantis on Twitch)
Repositoy: https://github.com/pcdoyle/Skyhook-API
License: MIT
____________________________________________________________________
Required Modules:
- datetime        - For date manipulation and common date functions.
- flask           - Flask project: http://flask.pocoo.org/
- python-dateutil - dateutil for Python 3
- pint            - For unit conversions.
"""
from datetime import datetime
from flask import Flask, Response
from dateutil import relativedelta
from pint import UnitRegistry
import requests
import config

"""
Required Global Variables:
"""
ureg = UnitRegistry()
Q_ = ureg.Quantity

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

@app.route('/beta_convert/<unit_one>/<unit_two>/<value>')
def convert(unit_one,unit_two,value):
    """Will be a conversion function to convert units of measurement.
    This is entirely test based on a pint example, don't use this
    code for anything ever. Also need to make this user friendly.
    It currently doesn't say the units in a easily readable way."""
    try:
        user_input = '%s * %s to %s' % (value, unit_one, unit_two)
        src, dst = user_input.split(' to ')
        converted = Q_(src).to(dst)
    except Exception as err:
        return Response('Unable to convert ' + unit_one + ' to ' + unit_two + ' [This API is in Beta]', mimetype='text/plain')

    return Response(value + unit_one + ' to ' + unit_two + ' is ' + str(round(converted, 2)) + ' [This API is in Beta]', mimetype='text/plain')

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
    follow_result = twitch_followage(channelid, userid)

    return Response(follow_result, mimetype='text/plain')

@app.route('/glitch/subage/<channelname>/<username>')
def get_subage(channelname,username):
    """Get how long someone has been subbed a certain channel."""
    channelid = twitch_getid(channelname)
    userid = twitch_getid(username)
    oauth = config.twoauth_test
    sub_result = twitch_subage(channelid, userid, oauth)

    return Response(sub_result, mimetype='text/plain')

@app.route('/glitch/test')
def glitch_test():
    """Test Function to Testing Twitch API stuff."""
    return Response("Test function", mimetype='text/plain')

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
            return 'Failed to format JSON data from Twitch!'

    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'
    
    try:
        result = request['data'][0]['id']
    except Exception as err:
        result = 'No user with that name found!'

    return result

def twitch_followage(channelid,userid):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/helix/users/follows?from_id=%s&to_id=%s' % (userid, channelid)
        headers = {'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        result = request['data'][0]['followed_at']
        formatted_date = datetime.strptime( result, "%Y-%m-%dT%H:%M:%SZ" )
        try:
            currentdate = datetime.utcnow()
            difference = relativedelta.relativedelta(currentdate, formatted_date)

            years = difference.years
            months = difference.months
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes

            return "%s years %s months %s days %s hours %s minutes." % (years, months, days, hours, minutes)
        except Exception as err:
            return 'An error occured in the date comparison.'
    except Exception as err:
        return 'User is not following this channel.'

    return 'An error occured in the lookup.'

def twitch_subage(channelid,userid,oauth):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s/subscriptions/%s' % (channelid,userid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid, 'Authorization': 'OAuth ' + oauth}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
            print(request)
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        sub_date = request['created_at']
        sub_type = request['sub_plan']


        formatted_date = datetime.strptime( sub_date, "%Y-%m-%dT%H:%M:%SZ" )
        try:
            currentdate = datetime.utcnow()
            difference = relativedelta.relativedelta(currentdate,formatted_date)

            years = difference.years
            months = difference.months
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes

            sub_length = "%s years %s months %s days %s hours %s minutes." % (years, months, days, hours, minutes)

            if sub_type == 'Prime':
                return 'Prime sub for ' + sub_length
            elif sub_type == '1000':
                return '$4.99 sub for ' + sub_length
            elif sub_type == '2000':
                return '$9.99 sub for ' + sub_length
            elif sub_type == '3000':
                return '$24.99 sub for ' + sub_length
            else:
                return 'Sub for: ' + sub_length + ' (Error: Couldn\'t get subscription type.)'
        except Exception as err:
            return 'An error occured in the date comparison.'
    except Exception as err:
        return 'User is not subscribed to this channel.'

    return 'An error occured in the lookup.'

if __name__ == "__main__":
    app.run(debug=True)
