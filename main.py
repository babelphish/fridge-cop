from google.appengine.api import memcache, users, urlfetch
from bottle import Bottle, SimpleTemplate, static_file, request, response
from fridge_model import FridgeDoorState
from fridge_door import FridgeDoor
from google.appengine.ext import ndb
from datetime import timedelta
from minification_support import getScriptTags, getStyleTags
from const_data import *
from magnet import *
import ConfigParser
import logging
import datetime
import json
import uuid
import sys
import os
import urllib
import re
import fridge_language
from user_points import UserPoints
from user_point import UserPoint
from user_profile import UserProfile
from text import Text

# Run the Bottle wsgi application. We don't need to call run() since our
# application is embedded within an App Engine WSGI application server.
bottle = Bottle()

fridge_door_state_cache_key = "fridgeDoorState"
fridge_last_opened_cache_key = "fridgeLastOpened"
door_ancestor_key = ndb.Key("FridgeDoor", "main")
date_1970 = datetime.datetime.utcfromtimestamp(0)
node_url = "http://node.fridge-cop.com/"
node_dev_url = "http://localhost:8081/"
config = ConfigParser.ConfigParser()
config.read("secure_keys.ini")
state_update_key = config.get("secure_keys", "state_update_key")
user_language = "EN"

is_dev = os.environ['SERVER_SOFTWARE'].startswith('Development')

home_template = SimpleTemplate(name='main.tpl')


def generate_csp_header(development):
    csp_header_addition = "; "

    if (development):
        csp_header_addition = " localhost:* ws://localhost:* 192.168.1.104:8080; "
    csp_header = "default-src *.fridge-cop.com " + csp_header_addition
    csp_header += " connect-src *.fridge-cop.com:* ws://node.fridge-cop.com:8080 ws://node.fridge-cop.com *.fridge-cop.appspot.com fridge-cop.appspot.com " + \
        csp_header_addition
    csp_header += " script-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com www.google.com " + \
        csp_header_addition
    csp_header += " style-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com " + \
        csp_header_addition
    csp_header += " font-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com " + \
        csp_header_addition
    csp_header += " img-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com " + \
        csp_header_addition

    return csp_header

dev_script_tags = getScriptTags(True)
prod_script_tags = getScriptTags(False)

dev_style_tags = getStyleTags(True)
prod_style_tags = getStyleTags(False)

dev_csp_header = generate_csp_header(True)
prod_csp_header = generate_csp_header(False)

# text
generic_error_message = "An error occurred. For details, log in as an administrator."


@bottle.route('/')
def home():
    try:
        script_tags = prod_script_tags
        style_tags = prod_style_tags
        csp_header = prod_csp_header
        if (is_dev):
            csp_header = dev_csp_header
            if (request.query.mode != "PROD"):
                script_tags = dev_script_tags
                style_tags = dev_style_tags

        response.set_header("Content-Security-Policy", csp_header)
        user = users.get_current_user()

        if user:
            url = users.create_logout_url("/")
        else:
            url = users.create_login_url("/")

        current_state = get_current_fridge_entity()

        state_class = "fridgeStateUnknown"

        if (current_state.state == 1):
            state_class = "fridgeStateOpen"
        elif (current_state.state == 2):
            state_class = "fridgeStateClosed"

        return home_template.render(script_tags=script_tags,
                                    style_tags=style_tags,
                                    fridge_state=state_class,
                                    user_url=url)

    except Exception as e:
        return process_exception(e)


@bottle.route('/change_state')
def change_state():
    try:
        new_state = int(request.query.new_state)
        key = request.query.state_update_key
        if (key != state_update_key):  # key has to match
            return json.dumps({"error": True, "message": "Invalid Key"})

        new_state = int(request.query.new_state)

        new_state_id = set_current_state(new_state)
        if (new_state_id is not None):
            current_state = get_serialized_current_state()
            return json.dumps({"new_state_id" : new_state_id, "broadcast" : broadcast_state(current_state) })
        else:
            return json.dumps({"error": True, "message" : "Couldn't set status, status is probably already set."})
    except Exception as e:
        return process_exception(e)


@bottle.route('/timeline_states')
def get_serialized_timeline_states():
    timeline_start_date = datetime.datetime.now() - datetime.timedelta(days=1)
    states = FridgeDoorState.query(
        ancestor=door_ancestor_key,
        filters=FridgeDoorState.change_time > timeline_start_date).fetch()
    state_list = []
    for state in states:
        state_list.append(fridge_state(state))

    return json.dumps(
        {
            "data": state_list,
            "start": str(timeline_start_date),
            "end": str(
                datetime.datetime.now() +
                datetime.timedelta(
                    minutes=10))})

# get the correct delayed state


@bottle.route('/point_ranks')
def get_serialized_point_ranks():
    points = UserPoints.query().order(-UserPoints.all_time_total).fetch(10)
    user = users.get_current_user()
    user_id = "nope"
    if (user is not None):
        user_id = user.user_id()

    ranks = []
    for point in points:
        profile = UserProfile.get_or_insert(point.user_id,
                                            user_id=point.user_id)

        result = {
            "p": point.all_time_total,
            "n": profile.sanitized_visible_name()
        }
        if (user_id == point.user_id):
            result["s"] = True

        ranks.append(result)

    return json.dumps({
        "error": False,
        "ranks": ranks,
        "startRank": 1
    })


def broadcast_state(message):
    if (is_dev):
        final_url = node_dev_url
    else:
        final_url = node_url

    final_url += "state_change_broadcast?environment="

    try:
        form_fields = {
            "message": message
        }
        form_data = urllib.urlencode(form_fields)
        result = urlfetch.fetch(
            url=final_url,
            payload=form_data,
            method=urlfetch.POST,
            headers={
                'Content-Type': 'application/x-www-form-urlencoded'})
        return message
    except Exception as e:
        return process_exception(e)


# this all has to be in a transaction, otherwise the get state/set state
# can be inconsistent
@ndb.transactional
def set_current_state(new_state):
    current_fridge_entity = get_current_fridge_entity()
    # then the state didn't actually change
    if (current_fridge_entity.state == new_state):
        return None

    new_state_id = str(uuid.uuid4())

    historical_fridge_entity = FridgeDoorState(parent=door_ancestor_key, id=new_state_id)
    historical_fridge_entity.state = new_state
    historical_fridge_entity.last_state = current_fridge_entity.state
    historical_fridge_entity.change_time = datetime.datetime.now()
    wait_historical_entity = historical_fridge_entity.put_async()    

    #assert ndb.in_transaction()
    
    current_fridge_entity.last_state = current_fridge_entity.state
    current_fridge_entity.state = new_state
    current_fridge_entity.change_time = datetime.datetime.now()
    wait_current_entity = current_fridge_entity.put_async()

    wait_historical_entity.get_result()
    wait_current_entity.get_result()
    return new_state_id  # return the historical id of our new state

@bottle.route('/fridge_point_click')
def fridge_point_click():
    click_time = datetime.datetime.now()
    try:
        user = users.get_current_user()
        if (not user):
            return json.dumps(
                {"error": True, "errorMessage": "User not logged in."})

        current_fridge_entity = get_current_fridge_entity()

        if (current_fridge_entity.state == 1):
            total_points = increment_user_point(user, current_fridge_entity)

            if (total_points is not None):
                return json.dumps({"error": False, "points": total_points})
            else:
                return json.dumps({"error": True,
                                   "errorMessage": Text.get(Text.ALREADY_GOT_POINT),
                                   "time": str(click_time)})
        else:
            return json.dumps(
                {"error": True, "errorMessage": "Fridge is closed :("})
    except Exception as e:
        return process_exception(e)


@ndb.transactional(xg=True)
def increment_user_point(user, current_fridge_entity):
    user_id = str(user.user_id())
    point_key = ndb.Key(
        'UserPoints',
        user_id,
        'UserPoint',
        current_fridge_entity.equality_key())
    point = point_key.get()
    if (point is None):
        point = UserPoint(key=point_key)
        point.user_id = user_id
        point.datetime_awarded = datetime.datetime.now()
        point_future = point.put_async()
        userPoints = get_user_points(user)
        userPoints.all_time_total += 1
        points_future = userPoints.put_async()
        points_future.get_result()
        point_future.get_result()
        return userPoints.all_time_total
    else:
        return None


def get_user_points(user):
    user_id = str(user.user_id())
    return UserPoints.get_or_insert(
        user_id,
        user_id=user_id,
        email_address=user.email())


@bottle.route('/set_name', method='POST')
def set_user_name():
    try:
        new_name = request.forms.get('name')
        if (new_name is None):
            return {"error": True,
                    "errorMessage": "'new_name' param must be set."}

        if (len(new_name) < min_visible_name_length):
            return {
                "error": True,
                "errorMessage": "Name can't be less than " +
                str(min_visible_name_length) +
                " characters."}

        if (len(new_name) > max_visible_name_length):
            return {
                "error": True,
                "errorMessage": "Name can't be more than " +
                str(max_visible_name_length) +
                " characters."}

        if (not visible_name_pattern.match(new_name)):
            return {"error": True,
                    "errorMessage": "Name must be alphanumeric."}

        user = users.get_current_user()
        id_to_change = str(user.user_id())

        # if we're an admin, allow changing anyone's name with the right id
        if (user and users.is_current_user_admin()
                and request.forms.get('id') is not None):
            id_to_change = request.forms.get('id')

        # get profile and set new name
        profile = UserProfile.get_or_insert(id_to_change,
                                            user_id=id_to_change,
                                            visible_name=new_name)
        profile.visible_name = new_name
        profile.put()

        return {"error": False
                }
    except Exception as e:
        return process_exception(e)


def generate_initial_magnets(user_id):
    magnets = []
    lang = fridge_language.get_fridge_language(user_language)
    for i in range(3):
        temp_magnet = CharacterMagnet(
            owner=user_id,
            text=lang.get_random_letter()
        )
        magnets.append(temp_magnet)
    return magnets


@bottle.route('/magnets/mine')
def get_my_magnets():
    try:
        user = users.get_current_user()
        requesting_user_id = str(user.user_id())
        return get_magnet_inventory(requesting_user_id)
    except Exception as e:
        return process_exception(e)


@bottle.route('/magnets/<user_id>')
def get_user_magnets():
    return get_magnets(user_id)


@bottle.route('/magnets/add/<user_id>', method='POST')
def add_user_magnet():
    user = users.get_current_user()
    if (user and users.is_current_user_admin()):  # only admins can add magnets
        magnet_type = request.forms.get('type')
        magnet = MagnetFactory.get_magnet(magnet_type)
        magnet.owner = user_id
        magnet.text = request.forms.get('text')


def get_magnets(user_id):
    user_key = ndb.Key('UserPoints', user_id)
    user_magnets = Magnet.query(filters=Magnet.owner == user_key).fetch()

    if (magnet_inventory is None):
        magnet_inventory = MagnetInventory(id=user_id, parent=user_key)
        magnet_inventory.user_id = user_id
        magnet_inventory.magnets = generate_initial_magnets()
        magnet_inventory.put()

    return json.dumps(magnet_inventory.to_dict())


@bottle.route('/current_state')
def get_serialized_current_state():
    current_state = get_current_fridge_entity()
    return json.dumps(fridge_state(current_state))

def fridge_state(state):
    found_state = {
        "s": str(state.state),
        "t": str(state.change_time),
        "ls": str(state.last_state),
        "type": "fridge"
    }
    return found_state

def process_exception(e):
    if users.is_current_user_admin():
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        result = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
        error_message = "Unknown Error." + result + " " + str(e)
    else:
        error_message = generic_error_message

    return json.dumps({"error": True, "errorMessage": error_message})

def get_current_fridge_entity():
    door_entity = FridgeDoorState.get_by_id(
        parent=door_ancestor_key,
        id='current')
    if (not door_entity):
        door_entity = FridgeDoorState(parent=door_ancestor_key, id='current')
        door_entity.state = 3  # unknown
        door_entity.last_state = 3  # unknown
        door_entity.change_time = datetime.datetime.now()

    return door_entity


@bottle.route('/init.js')
def js_init():
    response.content_type = 'application/javascript'
    response.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
    response.set_header("Pragma", "no-cache")
    response.set_header("Expires", "0")

    user = users.get_current_user()
    logged_in = (user is not None)
    fridge_points = 0

    if user:
        userPoints = get_user_points(user)
        fridge_points = userPoints.all_time_total

    serialized_state = get_serialized_current_state()

    return SimpleTemplate(
        name='init.js.tpl').render(
        logged_in=logged_in,
        fridge_points=fridge_points,
        serialized_state=serialized_state)


@bottle.route('/magnettest')
def magnets():
    try:
        return SimpleTemplate(name='test_magnets.tpl').render()
    except Exception as e:
        return process_exception(e)


@bottle.route('/admin/test')
def home():
    return SimpleTemplate(name='test_points.tpl').render()


@bottle.route('/js/<filename>')
def js_static(filename):
    return static_file(filename, root='/js/')


@bottle.route('/images/<filename>')
def images_static(filename):
    return static_file(filename, root='/images/')


@bottle.route('/css/<filename>')
def css_static(filename):
    return static_file(filename, root='/css')


@bottle.route('/fonts/<filename>')
def fonts_static(filename):
    return static_file(filename, root='/fonts')


@bottle.error(404)
def error_404(error):
    """Return a custom 404 error."""
    return 'Sorry, Nothing at this URL.'

if __name__ == "__main__":
    main()
