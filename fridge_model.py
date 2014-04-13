from google.appengine.ext import ndb

"""
class ContainerState:
		OPEN = 1
        CLOSED = 2
        UNKNOWN = 3
        TRANSITION = 4
"""

class FridgeDoorState(ndb.Model):
	door_state = ndb.IntegerProperty(required=True)
	last_door_state = ndb.IntegerProperty(required=True)
	state_time = ndb.DateTimeProperty(auto_now=False, required=True)
	
