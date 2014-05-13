from google.appengine.api import memcache, users, urlfetch
from bottle import Bottle, SimpleTemplate, static_file, request, response
from fridge_model import FridgeDoorState
from fridge_door import FridgeDoor
from google.appengine.ext import ndb
from datetime import timedelta
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

@bottle.route('/')
def home():
        try:
                user = users.get_current_user()
                logged_in = (user is not None)
                points = 0
                serialized_state = get_serialized_current_state()

                if user:
                        url = users.create_logout_url("/")
                        userPoints = get_user_points(user)
                        points = userPoints.all_time_total
                else:
                        url = users.create_login_url("/")
 
                return home_template.render(serialized_state = serialized_state,
                                            logged_in = logged_in,
                                            user_url = url,
                                            fridge_points = points)
        except Exception as e:
                return str(e)

@bottle.route('/change_state')
def change_state():
        try:
                new_state = int(request.query.new_state)

                set_state_success = set_current_state(new_state)
                if (set_state_success):
                        current_state = get_serialized_current_state()
                        return broadcast_state(current_state)
                else:
                        return "Same Status"
        except Exception as e:
                return str(e)

def development():
        return os.environ['SERVER_SOFTWARE'].startswith('Development')

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
                return "broadcast"
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
        return serialized_state(current_state)

def serialized_state(state):
        found_state = {
                "s" : str(state.state),
                "t" : str(state.change_time),
                "ls" : str(state.last_state),
                "type" : "fridge"
        }
        return json.dumps(found_state)

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
