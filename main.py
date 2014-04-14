from google.appengine.api import channel, memcache
from bottle import Bottle, SimpleTemplate, static_file, request
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

# Run the Bottle wsgi application. We don't need to call run() since our
# application is embedded within an App Engine WSGI application server.
bottle = Bottle()

home_template = SimpleTemplate(name='main.tpl')

fridge_door_state_cache_key = "fridgeDoorState"
fridge_last_opened_cache_key = "fridgeLastOpened"
channel_duration_minutes = 60 * 24
current_delay_seconds = 60
door_ancestor_key = ndb.Key("FridgeDoor", "main")


@bottle.route('/')
def home():
	current_state = int(get_current_state())
	if (current_state == 1):
		fridgeCSSClass = 'fridgeStateOpen'
	elif (current_state == 2):
		fridgeCSSClass = 'fridgeStateClosed'
	elif (current_state == 3):
		fridgeCSSClass = 'fridgeStateUnknown'
	elif (current_state == 4):
		fridgeCSSClass = 'fridgeStateTransition'

        last_opened_time = get_last_opened_time()
        if (last_opened_time is None):
                last_opened_time = ""

        url = users.create_login_url("/")
        logged_in = False
        polling_state = "slowPolling"
        user = users.get_current_user()
        token = ''
        if user:
                url = users.create_logout_url("/")
                logged_in = True
                polling_state = "fastPolling"
                token = request_channel()

        server_time = datetime.datetime.now()
	return home_template.render(fridge_state = fridgeCSSClass,
                                    last_opened_time = str(last_opened_time),
                                    polling_state = polling_state,
                                    logged_in = logged_in,
                                    user_url = url,
                                    channel_token = token,
                                    delay_seconds = current_delay_seconds,
                                    server_time = str(server_time))

@bottle.route('/change_state')
def change_state():
        new_state = int(request.query.new_state)

        set_state_success = set_current_state(new_state)
        if (set_state_success): #then we broadcast the new state to all our channels
                state_change = json.dumps({ 'fridge' : { 'state' : new_state } })
                broadcast_state(state_change)
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
        current_state = int(get_current_state())
        if (current_state == new_state): #then the state didn't actually change
                return False
        
	updated_door_entity = FridgeDoorState.get_by_id(parent = door_ancestor_key, id = 'current')
        if (not updated_door_entity):
                updated_door_entity = FridgeDoorState(parent = door_ancestor_key, id = 'current')
                updated_door_entity.last_door_state = 3 #unknown
                updated_door_entity.state_time = datetime.datetime.now()
        else:   #we store the old one as a regular entity
                updated_door_entity.key = ndb.Key(FridgeDoor, 'main', FridgeDoorState, str(uuid.uuid4()))
                updated_door_entity.put()
                #then we update the last_door_state appropriately
                updated_door_entity.key = ndb.Key(FridgeDoor, 'main', FridgeDoorState, 'current')
                updated_door_entity.last_door_state = updated_door_entity.door_state

        updated_door_entity.door_state = new_state
        updated_door_entity.state_time = datetime.datetime.now()
        updated_door_entity.put()
        return True #we know if we got here then the state changed

def get_last_opened_time():
        current_state = FridgeDoorState.get_by_id(parent = door_ancestor_key, id = 'current')
        if (current_state is None):
                last_opened_time = None
        else:
                last_opened_time = current_state.state_time

        return last_opened_time

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
                token = channel.create_channel(user_id, duration_minutes = channel_duration_minutes)
                expiration_time = datetime.datetime.now() + timedelta(minutes = channel_duration_minutes)
                existing_channel = UserChannel(id = user_id,
                                               user_id = user_id,
                                               token = token,
                                               active = True,
                                                expiration_time = expiration_time)         
                existing_channel.put()
        
                
        return token

def active_channels():
        now = datetime.datetime.now()
        active_channels = UserChannel.query(UserChannel.expiration_time > now,
                          UserChannel.active == True).fetch()
        return active_channels

def get_current_delay():
        return current_delay_seconds

@bottle.route('/delayed_state')
def get_delayed_state():
        try:
                now = datetime.datetime.now()
                seconds = (now- datetime.datetime.utcfromtimestamp(0)).total_seconds()
                normalized_timestamp = now - datetime.timedelta(milliseconds=int((seconds % get_current_delay()) * 1000))
                door_states = FridgeDoorState.query(ancestor = door_ancestor_key, filters = FridgeDoorState.state_time > normalized_timestamp).fetch()

                state_data = {
                        "states" : []
                }
                for state in door_states:
                        found_state = { "fridge" : { "state" : 1 }}
                        state_data["states"].append(found_state)
                         
                return json.dumps(state_data)
        except Exception as e:
                return str(e)

@bottle.route('/fridge_state')
def get_current_state():
        state_value = 3
        current_state = FridgeDoorState.get_by_id(id = 'current', parent = door_ancestor_key)
        if (current_state is not None):
                state_value = current_state.door_state

        return str(state_value)

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
