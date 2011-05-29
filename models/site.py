from google.appengine.ext import db
from models import DictModel

class Site(DictModel):
    name = db.StringProperty()
    location = db.GeoPtProperty()
    region = db.StringProperty()
    last_obs_issue_datetime = db.DateTimeProperty()
    last_obs_update_datetime = db.DateTimeProperty()
