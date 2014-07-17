from google.appengine.ext import ndb
from google.appengine.ext.ndb import polymodel


class Magnet(polymodel.PolyModel):
    IMAGE = 1
    WORD = 2
    CHARACTER = 3
    
    owner = ndb.KeyProperty(kind='UserProfile', repeated=False)
    text = ndb.StringProperty()

    def get_width():
        return 0

    def get_height():
        return 0

class ImageMagnet(Magnet):

    def get_width():
        return 2

    def get_height():
        return 2

    def get_type():
        return Magnet.IMAGE

class WordMagnet(Magnet):

    def get_width():
        return len(text)

    def get_height():
        return 1

    def get_type():
        return Magnet.WORD

class CharacterMagnet(Magnet):

    def get_width():
        return 1

    def get_height():
        return 1

    def get_type():
        return Magnet.CHARACTER

class MagnetFactory():
    @staticmethod
    def get_magnet(type_id):
        if type_id == Magnet.CHARACTER:
            return CharacterMagnet()
        elif type_id == Magnet.WORD:
            return WordMagnet()
        elif type_id == Magnet.IMAGE:
            return ImageMagnet()

class MagnetLocation(ndb.Model):
    pass


class MagnetLayout(ndb.Model):
    user_id = ndb.StringProperty(required=True)
    locations = ndb.LocalStructuredProperty(MagnetLocation)


#Queries we care about:
    #1 List of users containers
    
