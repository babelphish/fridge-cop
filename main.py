from google.appengine.api import channel, memcache
from bottle import Bottle, SimpleTemplate, static_file, request, response
from fridge_model import FridgeDoorState
from fridge_door import FridgeDoor
from user_channel import UserChannel
from google.appengine.ext import ndb
from google.appengine.api import channel, users
from datetime import timedelta
import logging
import datetime
import json
import uuid
import sys, os
from user_points import UserPoints
from user_point import UserPoint

# Run the Bottle wsgi application. We don't need to call run() since our
# application is embedded within an App Engine WSGI application server.
bottle = Bottle()

home_template = SimpleTemplate(name='main.tpl')

fridge_door_state_cache_key = "fridgeDoorState"
fridge_last_opened_cache_key = "fridgeLastOpened"
channel_duration_minutes = 60 * 24
current_delay_seconds = 10
door_ancestor_key = ndb.Key("FridgeDoor", "main")
date_1970 = datetime.datetime.utcfromtimestamp(0)

@bottle.route('/')
def home():
        try:
                user = users.get_current_user()
                logged_in = (user is not None)

                if user:
                        serialized_states = get_serialized_current_state()
                        url = users.create_logout_url("/")
                        polling_state = "fastPolling"
                        token = request_channel()
                        delay_seconds = 0
                else:
                        serialized_states = get_serialized_initial_delayed_state()
                        url = users.create_login_url("/")
                        polling_state = "slowPolling"
                        token = 'null'
                        delay_seconds = get_current_delay()

                server_time = datetime.datetime.now()
                return home_template.render(serialized_states = serialized_states,
                                            polling_state = polling_state,
                                            logged_in = logged_in,
                                            user_url = url,
                                            channel_data = token,
                                            delay_seconds = delay_seconds,
                                            server_time = str(server_time))
        except Exception as e:
                return str(e)

@bottle.route('/change_state')
def change_state():
        new_state = int(request.query.new_state)

        set_state_success = set_current_state(new_state)
        if (set_state_success): #then we broadcast the new state to all our channels
                current_state = get_serialized_current_state()
                broadcast_state(current_state)
                return "New Status"
        else:
                return "Same Status"

def broadcast_state(message):
        channel_list = active_channels()
        for active_channel in channel_list:
                channel.send_message(active_channel.user_id, message)
        

#this all has to be in a transaction, otherwise the get state/set state can be inconsistent
@ndb.transactional
def set_current_state(new_state):        
        current_fridge_entity = get_current_fridge_entity()
        if (current_fridge_entity.state == new_state): #then the state didn't actually change
                return False
        
        #we store the old one as a regular entity
        current_fridge_entity.key = ndb.Key(FridgeDoor, 'main', FridgeDoorState, str(uuid.uuid4()))
        current_fridge_entity.put()
        
        #then we change back to the current key and update the last_door_state appropriately
        current_fridge_entity.key = ndb.Key(FridgeDoor, 'main', FridgeDoorState, 'current')
        current_fridge_entity.last_state = current_fridge_entity.state
        current_fridge_entity.state = new_state
        current_fridge_entity.change_time = datetime.datetime.now()
        current_fridge_entity.put()
        return True #we know if we got here then the state changed

@bottle.route('/fridge_point_click')
def fridge_point_click():
        click_time = datetime.datetime.now()
        try:
                user = users.get_current_user()
                if (not user):
                        return json.dumps({ "error" : True, "errorMessage" : "User not logged in."})

                current_fridge_entity = get_current_fridge_entity()

                if (current_fridge_entity.state == 1):
                        total_points = increment_user_point(user, current_fridge_entity)

                        if (total_points is not None):
                                return json.dumps({ "error" : False,  "points" : total_points })
                        else:
                                return json.dumps({ "error" : True, "errorMessage" : "You already got a point for this one!", "time" : str(click_time) })
                else:
                        return json.dumps({ "error" : True, "errorMessage" : "Fridge is closed :(" })
        except Exception as e:
                #exc_type, exc_obj, exc_tb = sys.exc_info()
                #fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                #result = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)
                return json.dumps({ "error" : True, "errorMessage" : "Unknown Error." }) # + result + " " + str(e) })

@ndb.transactional(xg=True)
def increment_user_point(user, current_fridge_entity):
        user_id = str(user.user_id())
        point_key = ndb.Key('UserPoints', user_id, 'UserPoint', current_fridge_entity.equality_key())
        point = point_key.get()
        if (point is None):
                point = UserPoint(key=point_key)
                point.user_id = user_id
                point.datetime_awarded = datetime.datetime.now()
                point_future = point.put_async()
                userPoints = UserPoints.get_or_insert(user_id, user_id = user_id)
                userPoints.all_time_total += 1
                points_future = userPoints.put_async()
                points_future.get_result()
                point_future.get_result()
                return userPoints.all_time_total
        else:
                return None

@bottle.route('/request_new_channel')
def request_new_channel():
        user = users.get_current_user()
        if (not user):
                return json.dumps({ "error" : True, "errorMessage" : "Not logged in." })

        user_id = user.user_id()
        return generate_new_channel(user_id).serialize()

@bottle.route('/request_channel')
def request_channel():
        user = users.get_current_user()
        if (not user):
                return ''
                
        user_id = user.user_id()
        existing_channel = UserChannel.get_by_id(user_id)
        if (existing_channel) and (existing_channel.expiration_time > datetime.datetime.now()):
                token = existing_channel.token
                if (not existing_channel.active):
                        existing_channel.active = True
                        existing_channel.put()
        else:
                existing_channel = generate_new_channel(user_id)
                
        return existing_channel.serialize()

def generate_new_channel(user_id):
        token = channel.create_channel(user_id, duration_minutes = channel_duration_minutes)
        expiration_time = datetime.datetime.now() + timedelta(minutes = channel_duration_minutes)
        existing_channel = UserChannel(id = user_id,
                                       user_id = user_id,
                                       token = token,
                                       active = True,
                                        expiration_time = expiration_time)         
        existing_channel.put()
        return existing_channel

def active_channels():
        now = datetime.datetime.now()
        active_channels = UserChannel.query(UserChannel.expiration_time > now,
                          UserChannel.active == True).fetch()
        return active_channels

def get_current_delay():
        return current_delay_seconds

def get_normalized_timestamp_start(server_time):
        delay = get_current_delay()
        delayed_start = server_time - datetime.timedelta(seconds = delay)
        seconds_from_1970 = int((delayed_start - date_1970).total_seconds())
        normalized_timestamp_start = delayed_start - datetime.timedelta(seconds= (seconds_from_1970 % delay))
        normalized_timestamp_start = normalized_timestamp_start.replace(microsecond = 0) #zero out microseconds
        return normalized_timestamp_start

#get the correct delayed state
def get_serialized_initial_delayed_state():
        delay = get_current_delay()
        now = datetime.datetime.now()
        delayed_time = now - datetime.timedelta(seconds=delay)
        state = FridgeDoorState.query(ancestor = door_ancestor_key, filters = FridgeDoorState.change_time < delayed_time).order(-FridgeDoorState.change_time).get()
        if (state is None):
                return '{ states : [] }'
        return serialized_state_list([state])

@bottle.route('/delayed_states')
def get_delayed_states_with_headers():
        try:
                response.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
                response.set_header("Pragma", "no-cache")
                response.set_header("Expires", "0")
                return get_serialized_delayed_states()

        except Exception as e:
                return str(e)

def get_serialized_current_state():
        current_state = get_current_fridge_entity()
        return serialized_state_list([current_state])

def get_serialized_delayed_states():
        #calculate everything associated with getting state
        server_time = datetime.datetime.now()
        normalized_timestamp_start = get_normalized_timestamp_start(server_time)
        cache_key = str((normalized_timestamp_start - date_1970).total_seconds())
        state_data = memcache.get(cache_key)

        if state_data is None:
                normalized_timestamp_end = normalized_timestamp_start + datetime.timedelta(seconds = get_current_delay())
                door_states = FridgeDoorState.query(ancestor = door_ancestor_key,
                                                    filters = ndb.AND(FridgeDoorState.change_time >= normalized_timestamp_start
                                                                      , FridgeDoorState.change_time < normalized_timestamp_end)
                                                    ).order(FridgeDoorState.change_time).fetch()

                state_data = serialized_state_list(door_states)
                memcache.add(cache_key, state_data)

        return state_data

def serialized_state_list(states):
        state_data = {
                "states" : [],
        }
        for state in states:
                found_state = {
                        "s" : str(state.state),
                        "t" : str(state.change_time),
                        "ls" : str(state.last_state),
                        "type" : "fridge"
                }
                state_data["states"].append(found_state)

        return json.dumps(state_data)

def get_current_fridge_entity():
        door_entity = FridgeDoorState.get_by_id(parent = door_ancestor_key, id = 'current')
        if (not door_entity):
                door_entity = FridgeDoorState(parent = door_ancestor_key, id = 'current')
                door_entity.last_state = 3 #unknown
                door_entity.change_time = datetime.datetime.now()

        return door_entity

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
