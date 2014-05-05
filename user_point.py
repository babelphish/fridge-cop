from google.appengine.ext import ndb
import json

class UserPoint(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        datetime_awarded = ndb.DateTimeProperty(required=True)
