from google.appengine.ext import ndb
import json

class UserPoints(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        all_time_total = ndb.IntegerProperty(required=True, default=0)
