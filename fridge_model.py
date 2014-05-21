from google.appengine.ext import ndb
import datetime
"""
class ContainerState:
        OPEN = 1
        CLOSED = 2
        UNKNOWN = 3
        TRANSITION = 4
"""

date_1970 = datetime.datetime.utcfromtimestamp(0)

class FridgeDoorState(ndb.Model):
	state = ndb.IntegerProperty(required=True)
	last_state = ndb.IntegerProperty(required=True)
	change_time = ndb.DateTimeProperty(auto_now=False, required=True)
	
        def equality_key(self):
                #the implication here is no more than 1 point per item/state/second
                epoch_seconds = str(int((self.change_time - date_1970).total_seconds()))
                return self.kind() + "_" + epoch_seconds + "_" + str(self.state)

        def kind(self):
                return "fridge_door"

