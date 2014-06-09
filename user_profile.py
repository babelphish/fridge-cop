from google.appengine.ext import ndb
import json

class UserProfile(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        email_address = ndb.StringProperty(required=False)
        visible_name = ndb.StringProperty(required=False, default="Anonymous FridgeClicker")
