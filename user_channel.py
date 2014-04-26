from google.appengine.ext import ndb
import json

"""
class ContainerState:
		OPEN = 1
        CLOSED = 2
        UNKNOWN = 3
        TRANSITION = 4
"""

class UserChannel(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        token = ndb.StringProperty(required=True)
        active = ndb.BooleanProperty(required=True, default=True)
	expiration_time = ndb.DateTimeProperty(required=True)


        def serialize(self):
                return json.dumps({
                                "token" : self.token,
                                "expiration" : str(self.expiration_time),
                                "active" : str(self.active)
                        }) 
