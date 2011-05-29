from sets import Set
from google.appengine.ext import db
import datetime
from jsonproperty import JsonProperty, JsonMixin
from lib.iso8601 import parse_date

SIMPLE_TYPES = (int, long, float, bool, dict, basestring, list)

def make_key_name(site, reference_date):
    return "%s/%s" % (site.key().name(),reference_date.isoformat())

def jsonvalue(value):
    if value is None or isinstance(value, SIMPLE_TYPES):
        return value
    elif isinstance(value, datetime.date):
        return value.isoformat()
    elif isinstance(value, db.GeoPt):
        return {'lat': value.lat, 'lon': value.lon}
    elif hasattr(value, 'to_dict'):
        return value.to_dict()
    elif hasattr(value, 'to_json'):
        return value.to_json()
    else:
        raise ValueError('cannot encode ' + repr(prop))

class DictModel(db.Model):
    #noinspection PyDefaultArgument
    def to_dict(self, excluding = []):
        output = {}
        exclude_props = Set(excluding)
        for key, prop in self.properties().iteritems():
            if key not in exclude_props:
                value = getattr(self, key)
                output[key] = jsonvalue(value)

        output['id'] = self.key().id_or_name()
        return output
