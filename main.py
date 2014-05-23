from google.appengine.api import memcache, users, urlfetch
from bottle import Bottle, SimpleTemplate, static_file, request, response
from fridge_model import FridgeDoorState
from fridge_door import FridgeDoor
from google.appengine.ext import ndb
from datetime import timedelta
import ConfigParser
import logging
import datetime
import json
import uuid
import sys, os
import urllib
from user_points import UserPoints
from user_point import UserPoint
from text import Text

# Run the Bottle wsgi application. We don't need to call run() since our
# application is embedded within an App Engine WSGI application server.
bottle = Bottle()

home_template = SimpleTemplate(name='main.tpl')

fridge_door_state_cache_key = "fridgeDoorState"
fridge_last_opened_cache_key = "fridgeLastOpened"
door_ancestor_key = ndb.Key("FridgeDoor", "main")
date_1970 = datetime.datetime.utcfromtimestamp(0)
node_url = "http://node.fridge-cop.com/"

config = ConfigParser.ConfigParser()
config.read("secure_keys.ini")
state_update_key = config.get("secure_keys", "state_update_key")

def development():
        return os.environ['SERVER_SOFTWARE'].startswith('Development')

csp_header_addition = ""
if (development()):
        csp_header_addition = " localhost:8080 192.168.1.104:8080 "

csp_header =  "default-src *.fridge-cop.com  localhost:8080 " + csp_header_addition
csp_header += " connect-src *.fridge-cop.com:* ws://node.fridge-cop.com:8080 ws://node.fridge-cop.com *.fridge-cop.appspot.com fridge-cop.appspot.com" + csp_header_addition
csp_header += " script-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com www.google.com" + csp_header_addition
csp_header += " style-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com" + csp_header_addition
csp_header += " font-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com" + csp_header_addition
csp_header += " img-src *.fridge-cop.com:* *.fridge-cop.appspot.com fridge-cop.appspot.com" + csp_header_addition


@bottle.route('/')
def home():
        try:
                response.set_header("Content-Security-Policy", csp_header)
                user = users.get_current_user()

                if user:
                        url = users.create_logout_url("/")
                else:
                        url = users.create_login_url("/")

                current_state = get_current_fridge_entity()
                
                stateClass = "fridgeStateUnknown"

                if (current_state.state == 1):
                        state_class = "fridgeStateOpen"
                elif (current_state.state == 2):
                        state_class = "fridgeStateClosed"

                return home_template.render(fridge_state = state_class,
                                            user_url = url)

        except Exception as e:
                return str(e)

@bottle.route('/change_state')
def change_state():
        try:
                new_state = int(request.query.new_state)
                key = request.query.state_update_key
                if (key != state_update_key): #key has to match
                        return json.dumps({ "error" : True, "message" : "Invalid Key"})

                new_state = int(request.query.new_state)
 
                set_state_success = set_current_state(new_state)
                if (set_state_success):
                        current_state = get_serialized_current_state()
                        return broadcast_state(current_state)
                else:
                        return "Same Status"
        except Exception as e:
                return str(e)

#get the correct delayed state
@bottle.route('/timeline_states')
def get_serialized_timeline_states():
        timeline_start_date = datetime.datetime.now() - datetime.timedelta(days = 1)
        states = FridgeDoorState.query(ancestor = door_ancestor_key, filters = FridgeDoorState.change_time > timeline_start_date).fetch()
        state_list = []
        for state in states:
                state_list.append(fridge_state(state))

        return json.dumps({ "data" : state_list,
                            "start" : str(timeline_start_date),
                            "end" : str(datetime.datetime.now() + datetime.timedelta(minutes = 10))
                         })

def broadcast_state(message):
        final_url = node_url
        
        final_url += "state_change_broadcast?environment="

        if (development()):
                final_url += "DEV"
        else:
                final_url += "PROD"
        try:
                form_fields =  {
                        "message" : message
                }
                form_data = urllib.urlencode(form_fields)
                result= urlfetch.fetch(url=final_url,
                        payload=form_data,
                        method=urlfetch.POST,
                        headers={'Content-Type': 'application/x-www-form-urlencoded'})
                return message
        except Exception as e:
                return str(e)

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
                                return json.dumps({ "error" : True, "errorMessage" : Text.get(Text.ALREADY_GOT_POINT), "time" : str(click_time) })
                else:
                        return json.dumps({ "error" : True, "errorMessage" : "Fridge is closed :(" })
        except Exception as e:
                if users.is_current_user_admin():
                        exc_type, exc_obj, exc_tb = sys.exc_info()
                        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                        result = str(exc_type) + str(fname) + str(exc_tb.tb_lineno)                        
                        error_message = "Unknown Error." + result + " " + str(e)
                else:
                        error_message = "Unknown Error."

                return json.dumps({ "error" : True, "errorMessage" : error_message })

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
        return UserPoints.get_or_insert(user_id, user_id = user_id, email_address=user.email())

@bottle.route('/current_state')
def get_serialized_current_state():
        current_state = get_current_fridge_entity()
        return json.dumps(fridge_state(current_state))

def fridge_state(state):
        found_state = {
                "s" : str(state.state),
                "t" : str(state.change_time),
                "ls" : str(state.last_state),
                "type" : "fridge"
        }
        return found_state

def get_current_fridge_entity():
        door_entity = FridgeDoorState.get_by_id(parent = door_ancestor_key, id = 'current')
        if (not door_entity):
                door_entity = FridgeDoorState(parent = door_ancestor_key, id = 'current')
                door_entity.last_state = 3 #unknown
                door_entity.change_time = datetime.datetime.now()

        return door_entity

@bottle.route('/init.js')
def js_init():
        response.content_type = 'application/javascript'
        response.set_header("Cache-Control", "no-cache, no-store, must-revalidate")
        response.set_header("Pragma", "no-cache")
        response.set_header("Expires", "0");
        
       
        user = users.get_current_user()
        logged_in = (user is not None)
        fridge_points = 0

        if user:
                userPoints = get_user_points(user)
                fridge_points = userPoints.all_time_total

        serialized_state = get_serialized_current_state()
        
        return SimpleTemplate(name='init.js.tpl').render(logged_in = logged_in,
                                                         fridge_points = fridge_points,
                                                         serialized_state = serialized_state)

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
