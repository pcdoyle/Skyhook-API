from flask import Flask, Response, jsonify
import requests
import config

app = Flask(__name__)

@app.route('/')
def startpage():
    """The start page for the server."""
    return Response('Skyhook\'s custom API Server.', mimetype='text/plain')

@app.route('/weather')
def weather():
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

@app.route('/convert')
def convert():
    """Will be a conversion function to convert units of distance, etc. Currently not being used."""
    return Response('Hello.', mimetype='text/plain')

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
    return Response('Channel Name: ' + channelname + ' User Name: ' + username, mimetype='text/plain')

@app.route('/glitch/subage/<oauth>/<channelname>/<username>')
def get_subage(oauth,channelname,username):
    """Get how long someone has been subbed a certain channel."""
    return Response('OAuth Key: ' + oauth + ' Channel Name: ' + channelname + ' User Name: ' + username, mimetype='text/plain')

@app.errorhandler(404)
def page_not_found(error):
    """404 Error Handling function. Just returns a plaintext error."""
    return Response('404 Error: Bad API call.', mimetype='text/plain')