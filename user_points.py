from google.appengine.ext import ndb
import json

class UserPoints(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        all_time_total = ndb.IntegerProperty(required=True, default=0)
        email_address = ndb.StringProperty(required=False)
        visible_name = ndb.StringProperty(required=False, default="Anonymous FridgeClicker")
