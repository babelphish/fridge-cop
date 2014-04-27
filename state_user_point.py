from google.appengine.ext import ndb
import json

class StateUserPoint(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        datetime_awarded = ndb.DateTimeProperty(required=True)
        associated_state = ndb.KeyProperty(required = True)
