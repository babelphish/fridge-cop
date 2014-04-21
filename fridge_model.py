from google.appengine.ext import ndb

"""
class ContainerState:
		OPEN = 1
        CLOSED = 2
        UNKNOWN = 3
        TRANSITION = 4
"""

class FridgeDoorState(ndb.Model):
	state = ndb.IntegerProperty(required=True)
	last_state = ndb.IntegerProperty(required=True)
	change_time = ndb.DateTimeProperty(auto_now=False, required=True)
	
