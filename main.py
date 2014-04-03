from google.appengine.api import channel, memcache
from bottle import Bottle, SimpleTemplate, static_file, request
from fridge_model import FridgeDoorState
from google.appengine.ext import ndb
from google.appengine.api import channel, users
import logging
import datetime
import json


# Run the Bottle wsgi application. We don't need to call run() since our
# application is embedded within an App Engine WSGI application server.
bottle = Bottle()

home_template = SimpleTemplate(name='main.tpl')

fridge_door_state_cache_key = "fridgeDoorState"
fridge_last_opened_cache_key = "fridgeLastOpened"

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
        if user:
                url = users.create_login_url("/")
                logged_in = True
                polling_state = "fastPolling"
	
	return home_template.render(fridge_state = fridgeCSSClass,
                                    last_opened_time = str(last_opened_time),
                                    polling_state = polling_state,
                                    logged_in = logged_in,
                                    user_url = url)

@bottle.route('/change_state')
def change_state():
	new_state = int(request.query.new_state)
	current_state = int(get_current_state())

	if (current_state == new_state):
		return "Same Status"
	else:
		set_current_state(new_state)
		return "New Status"

def set_current_state(new_state):
	updated_door_entity = FridgeDoorState.get_by_id('current')
        updated_door_entity.door_state = new_state
	updated_door_entity.put()

def get_last_opened_time():
        current_state = FridgeDoorState.get_by_id('current')
        if (current_state is None):
                last_opened_time = None
        else:
                last_opened_time = current_state.state_time

        return last_opened_time
                
@bottle.route('/request_channel')
def request_channel():
        return "nada"
        #generate and store 


@bottle.route('/fridge_state')
def get_current_state():
        state_value = 3
        current_state = FridgeDoorState.get_by_id('current')
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
