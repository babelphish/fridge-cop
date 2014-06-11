from google.appengine.ext import ndb
from xml.sax.saxutils import escape
import json

html_escape_table = {
        '"': "&quot;",
        "'": "&#x27;",
        "/": "&#x2F;"
        }

class UserProfile(ndb.Model):
        user_id = ndb.StringProperty(required=True)
        email_address = ndb.StringProperty(required=False)
        visible_name = ndb.StringProperty(required=False, default="Anonymous FridgeClicker")

        def sanitized_visible_name(self):
                return escape(self.visible_name, html_escape_table)
