# -*- coding: utf-8 -*-
"""
Skyhook-API Beta
Copyright 2018: Patrick Doyle. (KaoAtlantis on Twitch)
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
import dateutil.parser
from pint import UnitRegistry
import requests
import random
# Local Imports:
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
        result = requests.get('https://api.darksky.net/forecast/' + config.darksky_secret + '/49.1329,-122.3261?units=ca')
        try:
            weather = result.json()
        except Exception as err:
            return Response('Weather API did not return any JSON data!', mimetype='text/plain')
    except requests.exceptions.RequestException as err:
        return Response('Failed to connect to weather API!', mimetype='text/plain')

    try:
        w_summary       = weather['currently']['summary']
        w_temp          = weather['currently']['temperature']
        w_temp_feels    = weather['currently']['apparentTemperature']
        w_humidity      = weather['currently']['humidity']
        w_windspeed     = weather['currently']['windSpeed']
        w_windgusts     = weather['currently']['windGust']
        w_percipchance  = weather['currently']['precipProbability']

        try:
            w_percipdesc = weather['currently']['precipType']
        except:
            w_percipdesc = False

    except Exception as err:
        return Response('Failed to pull weather data! Usually caused by an incorrect API key.', mimetype='text/plain')

    weather_full = '%s with a temperature of %s°C (%s°F)' % (str(w_summary), str(w_temp), str(convert_c2f(w_temp)))

    if float(w_temp_feels) < float(w_temp):
        weather_full += '. It feels like %s°C' % str(w_temp_feels)

    if float(w_windspeed) > 0:
        if float(w_windgusts) > 0:
            weather_full += '. The wind is currently blowing at %skm/h with gusts of %skm/h' % (str(w_windspeed), str(w_windgusts))
        else:
            weather_full += '. The wind is currently blowing at %skm/h' % str(w_windspeed)

        try:
            if float(w_temp_feels) < float(w_temp):
                weather_full += '. The wind chill is %s°C.' % str(w_temp_feels)
            else:
                weather_full += '.'
        except ValueError as err:
            weather_full += '.'
    else:
        weather_full = '%s. There is curently no wind.' % str(weather_full)

    if float(w_humidity) > 0:
        w_humidity_converted = w_humidity * 100
        weather_full += ' The Humidity is %s%%.' % str(int(w_humidity_converted))

    if float(w_percipchance) > 0:
        w_percipchance_converted = w_percipchance * 100

        if w_percipdesc != False:
            weather_full += ' There is a %s%% chance of %s.' % (str(int(w_percipchance_converted)), str(w_percipdesc))


    return Response(weather_full, mimetype='text/plain')


"""
curl -X "GET" "" -H "Accept: application/json" -H "Content-Type: application/json" -H "Authorization: "
"""

@app.route('/music/song')
def music_song():
    """Spotify API stuff doesn't work at all yet"""
    return Response('Song.', mimetype='text/plain')


@app.route('/music/playlist')
def music_playlist():
    """Spotify API stuff doesn't work at all yet"""
    return Response('Playlist.', mimetype='text/plain')


@app.route('/beta_convert/<unit_one>/<unit_two>/<value>')
def convert(unit_one,unit_two,value):
    """Will be a conversion function to convert units of measurement.
    This is entirely test based on a pint example, don't use this
    code for anything ever. Also need to make this user friendly.
    It currently doesn't say the units in a easily readable way."""
    ureg = UnitRegistry()

    try:
        converted = ureg.Quantity(value + ' * ' + unit_one).to(unit_two)
    except Exception as err:
        return Response('Unable to convert ' + unit_one + ' to ' + unit_two + ' [This API is in Beta]', mimetype='text/plain')

    return Response(value + unit_one + ' to ' + unit_two + ' is ' + str(round(converted, 2)) + ' [This API is in Beta]', mimetype='text/plain')

@app.route('/convert/<conversion>/<value>')
def temp_convert(conversion,value):
    """
    A conversion function to convert units of temperature.
    """
    return Response(convert_temp(conversion,value), mimetype='text/plain')

@app.route('/glitch/getid/<username>')
def get_twitch_id(username):
    """Returns the userid of a username on Twitch."""
    twitch_id = twitch_getid(username.lower())
    return Response(twitch_id, mimetype='text/plain')


@app.route('/glitch/getuser/<userid>')
def get_twitch_user(userid):
    """Will return user information from the userid given."""
    return Response('User ID: ' + userid, mimetype='text/plain')


@app.route('/glitch/followage/<channelname>/<username>')
def get_followage(channelname, username):
    """Get how long someone has been following a certain channel."""
    channelid = twitch_getid(channelname.lower())
    userid = twitch_getid(username.lower())
    follow_result = twitch_followage(channelid, userid)

    return Response(follow_result, mimetype='text/plain')


@app.route('/glitch/subage/<channelname>/<username>')
def get_subage(channelname, username):
    """Get how long someone has been subbed a certain channel."""
    channelid = twitch_getid(channelname.lower())
    userid = twitch_getid(username.lower())
    oauth = config.twoauth_new
    sub_result = twitch_subage(channelid, userid, oauth)

    return Response(sub_result, mimetype='text/plain')


@app.route('/glitch/userage/<username>')
def get_userage(username):
    """Get how long someone has been following a certain channel."""
    userid = twitch_getid(username.lower())
    d = twitch_userage(userid)
    response = d.strftime('%B %d, %Y at %I:%M %p %Z')

    return Response(response, mimetype='text/plain')


@app.route('/glitch/title/<channelname>')
def get_title(channelname):
    """Get the title of the stream of <channelname>."""
    channelid = twitch_getid(channelname.lower())
    return Response(twitch_title(channelid), mimetype='text/plain')


@app.route('/glitch/subcount/<channelname>')
def get_subcount(channelname):
    """Get the title of the stream of <channelname>."""
    channelid = twitch_getid(channelname.lower())
    return Response(twitch_subcount(channelid, config.twoauth_new), mimetype='text/plain')


@app.route('/glitch/game/<channelname>')
def get_game(channelname):
    """Get the title of the stream of <channelname>."""
    channelid = twitch_getid(channelname.lower())
    return Response(twitch_getgame(channelid), mimetype='text/plain')


@app.route('/glitch/botcheck/<username>')
def get_botstatus(username):
    """Checks if Twitch knows <username> is a bot."""
    userid = twitch_getid(username.lower())
    return Response(twitch_botcheck(userid), mimetype='text/plain')


@app.route('/glitch/test')
def glitch_test():
    """Test Function to Testing Twitch API stuff."""
    years = 1
    months = 0
    days = 4
    hours = 2
    minutes = 1

    diff_string = string_time(years, months, days, hours, minutes)

    return Response(diff_string, mimetype='text/plain')


@app.route('/conch')
def conch():
    """Returns a random response from SpongeBob's Magic Conch shell."""
    responses = ["Maybe someday.",  "Nothing.", "Neither.", "I don't think so.", "Yes.", "Try asking again."]
    return Response(random.choice(responses), mimetype='text/plain')


@app.route('/8ball')
def eightball():
    """Returns a random response from a magic 8-ball."""
    responses = ['It is certain.', 'It is decidedly so.', 'Without a doubt.', 'Yes definitely.',
                 'You may rely on it.', 'As I see it, yes.', 'Most likely.', 'Outlook good.', 'Yes.',
                 'Signs point to yes.', 'Reply hazy try again.', 'Ask again later.',
                 'Better not tell you now.', 'Cannot predict now.', 'Concentrate and ask again.',
                 'Don\'t count on it.', 'My reply is no.', 'My sources say no.', 'Outlook not so good.', 'Very doubtful.']
    return Response(random.choice(responses), mimetype='text/plain')

@app.route('/snek')
def snek():
    """Returns a random response for Norton the Snake."""
    responses = ["Bitch, I'm back!", "Hi, I'm Norton!", "Oscar and Onion are dead.", "I'm cold. :(", "Feed me bits.", "Thanks for the bits!"]
    return Response(random.choice(responses), mimetype='text/plain')


@app.errorhandler(404)
def page_not_found(error):
    """404 Error Handling function. Just returns a plaintext error."""
    return Response('404 Error: Not an API call.', mimetype='text/plain')


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


def twitch_followage(channelid, userid):
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

            diff_string = string_time(years, months, days, hours, minutes)

            return diff_string
        except Exception as err:
            return 'An error occured in the date comparison.'
    except Exception as err:
        return 'User is not following this channel.'

    return 'An error occured in the lookup.'


def twitch_subage(channelid, userid, oauth):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s/subscriptions/%s' % (channelid, userid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid, 'Authorization': 'OAuth ' + oauth}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        sub_date = request['created_at']
        sub_plan = request['sub_plan']

        formatted_date = datetime.strptime(sub_date, "%Y-%m-%dT%H:%M:%SZ")
        try:
            currentdate = datetime.utcnow()
            difference = relativedelta.relativedelta(currentdate, formatted_date)

            years = difference.years
            months = difference.months
            days = difference.days
            hours = difference.hours
            minutes = difference.minutes

            diff_string = string_time(years, months, days, hours, minutes)

            if sub_plan == 'Prime':
                return 'Prime sub for %s' % diff_string
            elif sub_plan == '1000':
                return '$4.99 sub for %s' % diff_string
            elif sub_plan == '2000':
                return '$9.99 sub for %s' % diff_string
            elif sub_plan == '3000':
                return '$24.99 sub for %s' % diff_string
        except Exception as err:
            return 'An error occured in the date comparison.'
    except Exception as err:
        return 'User is not subscribed to this channel. '

    return 'An error occured in the lookup.'


def twitch_userage(userid):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/kraken/users/%s' % (userid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        result = request['created_at']
        #formatted_date = datetime.strptime(result, "%Y-%m-%d %H:%M:%S.%fZ")
        formatted_date = dateutil.parser.parse(result)

        return formatted_date

    except Exception as err:
        return 'User age could not be found.'

    return 'An error occured in the lookup.'


def twitch_title(channelid):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s' % (channelid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        return request['status']
    except Exception as err:
        return 'Channel title could not be found.'

    return 'An error occured in the lookup.'


def twitch_subcount(channelid, oauth):
    """Get's the sub count of a channel."""
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s/subscriptions?limit=1' % (channelid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid, 'Authorization': 'OAuth ' + oauth}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        print(request)
        return str(request['_total']-4)
    except Exception as err:
        print(request)
        return 'Channel sub count could not be found.'

    return 'An error occured in the lookup.'


def twitch_botcheck(userid):
    """Get's the follow age between two users from the Twitch API."""
    respOne = ''
    respTwo = ''
    resp = ''

    try:
        url = 'https://api.twitch.tv/kraken/users/%s/chat' % (userid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        if request['is_verified_bot'] is True:
            respOne = 'Twitch has verified me as a bot'
        else:
            respOne = 'Twitch has not verified me as a bot yet'

        if request['is_known_bot'] is True:
            respTwo = 'Twitch knows I am a bot'
        else:
            respTwo = 'Twitch does not know I am a bot'

        return respTwo + ' and ' + respOne + '!'

    except Exception as err:
        return 'Channel title could not be found.'

    return 'An error occured in the lookup.'


def twitch_getgame(channelid):
    """Get's the follow age between two users from the Twitch API."""
    try:
        url = 'https://api.twitch.tv/kraken/channels/%s' % (channelid)
        headers = {'Accept': 'application/vnd.twitchtv.v5+json', 'Client-ID': config.twclientid}
        request = requests.get(url, headers=headers)
        try:
            request = request.json()
        except Exception as err:
            return 'Failed to format JSON data from Twitch!'
    except requests.exceptions.RequestException as err:
        return 'Failed to connect to Twitch API server.'

    try:
        return request['game']
    except Exception as err:
        return 'Channel game could not be found.'


    return 'An error occured in the lookup.'


def string_time(years, months, days, hours, minutes):
    """ Figures out what needs to be output between year, month, day, hour, and minute."""
    year_text = pluralize(years, 'year')
    month_text = pluralize(months, 'month')
    day_text = pluralize(days, 'day')
    hour_text = pluralize(hours, 'hour')
    minute_text = pluralize(minutes, 'minute')

    string = '%s %s.' % (str(minutes), minute_text)

    if hours > 0:
        string = '%s %s %s' % (str(hours), hour_text, string)

    if days > 0:
        string = '%s %s %s' % (str(days), day_text, string)

    if months > 0:
        string = '%s %s %s' % (str(months), month_text, string)

    if years > 0:
        string = '%s %s %s' % (str(years), year_text, string)

    return string


def pluralize(number, word):
    """Figures out if a word needs to be pluralized depending on the number provided."""
    if not number == 1:
        word += 's'
    return word

def convert_temp(conversion, value):

    try:
        if (conversion == 'c2f'):
            try:
                num = float(value)

                result_a = convert_c2f(num)
                result_b = convert_c2k(num)

                return(str(num) + '°C is ' + str(result_a) + '°F (or ' + str(result_b) + ' Kelvin).')
            except:
                return('Not a number.')

        elif (conversion == 'f2c'):
            try:
                num = float(value)

                result_a = convert_f2c(num)
                result_b = convert_c2k(result_a)

                return(str(num) + '°F is ' + str(result_a) + '°C (or ' + str(result_b) + ' Kelvin).')
            except:
                return('Not a number.')

        elif (conversion == 'k2f'):
            try:
                num = float(value)

                result_a = convert_k2c(num)
                result_b = convert_c2f(result_a)

                return(str(num) + ' Kelvin is ' + str(result_b) + '°F (or ' + str(result_a) + '°C).')
            except:
                return('Not a number.')

        elif (conversion == 'k2c'):
            try:
                num = float(value)

                result_a = convert_k2c(num)
                result_b = convert_c2f(result_a)

                return(str(num) + ' Kelvin is ' + str(result_a) + '°C (or ' + str(result_b) + '°F).')
            except:
                return('Not a number.')

        elif (conversion == 'f2k'):
            try:
                num = float(value)

                result_a = convert_f2c(num)
                result_b = convert_c2k(result_a)

                return(str(num) + '°F is ' + str(result_b) + ' Kelvin (or ' + str(result_a) + '°C).')
            except:
                return('Not a number.')

        elif (conversion == 'c2k'):
            try:
                num = float(value)

                result_a = convert_c2k(num)
                result_b = convert_c2f(num)

                return(str(num) + '°C is ' + str(result_a) + ' Kelvin (or ' + str(result_b) + '°F).')
            except:
                return('Not a number.')

    except:
        return('Something went terribly wrong.')

    return('Not a conversion.')

def convert_c2f(num):
    result = round((num*9/5)+32,2)
    return(result)

def convert_f2c(num):
    result = round((num-32)*5/9,2)
    return(result)

def convert_k2c(num):
    result = round(num-273.15,2)
    return(result)

def convert_c2k(num):
    result = round(num+273.15,2)
    return(result)



if __name__ == "__main__":
    app.run(debug=True, port=5000)
