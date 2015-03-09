from google.appengine.ext import ndb

class ContainerEventMedia(ndb.Model):
    thumbnail_url = ndb.TextProperty(required=False)
    image_url = ndb.TextProperty(required=False)
    gif_url = ndb.TextProperty(required=False)
    full_width = ndb.IntegerProperty(required=False)
    full_height = ndb.IntegerProperty(required=False)
    thumbnail_width = ndb.IntegerProperty(required=False)
    thumbnail_height = ndb.IntegerProperty(required=False)
    
    def get_thumbnail_url(self):            
        return thumbnail_url

    def get_image_url(self):
        return image_url

    def get_gif_url(self):
        return gif_url
