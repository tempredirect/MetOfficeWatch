from datetime import datetime
from google.appengine.ext import db
from jsonproperty import JsonMixin, JsonProperty
from models import Weather, DictModel, Site, make_key_name

class Observations(JsonMixin):
    def __init__(self):
        self.observations = {}

    def add(self, obs_time, weather):
        if  isinstance(obs_time,datetime):
            obs_time = obs_time.time().isoformat()
        self.observations[obs_time] = weather

    def to_json(self):
        result = {}
        for k,v in self.observations.items():
            result[k] = v.to_json()
        return result

    @classmethod
    def from_json(cls, json):
        o = Observations()
        for k,v in json.items():
            o.add(k, Weather(v))
        return o

class ObservationDay(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    observation_date = db.DateProperty()
    lastdata_datetime = db.DateTimeProperty()
    observations = JsonProperty(Observations, default=Observations())

    @classmethod
    def get_by(cls, site, date, not_found_return_new = False):
        r =  ObservationDay.get_by_key_name(make_key_name(site,date))
        if r is None and not_found_return_new:
            r = ObservationDay(key_name=make_key_name(site,date), site = site, observation_date = date)
        return r

class ObservationTimestep(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    observation_datetime = db.DateTimeProperty()
    observation_date = db.DateProperty()

    wind_gust = db.IntegerProperty()
    wind_speed = db.IntegerProperty()
    wind_direction = db.StringProperty()
    pressure = db.IntegerProperty()
    pressure_tendency = db.StringProperty()
    screen_relative_humidity = db.IntegerProperty()
    weather_type = db.IntegerProperty()
    temperature = db.FloatProperty()
    visibility = db.IntegerProperty()

    @classmethod
    def get_by_site_and_datetime(cls, site, date):
        q = (ObservationTimestep.all()
                .filter("site =", site)
                .filter("observation_datetime =", date))
        return q.get()

    @classmethod
    def find_latest_by_site(cls, site, limit = 100):
        q = (ObservationTimestep.all()
                .filter("site =", site)
                .order("-observation_datetime"))

        return q.fetch(limit = limit)

    @classmethod
    def find_by_site_and_date(cls, site, obs_date, offset = 0, limit = 50):
        q = (ObservationTimestep.all()
                .filter("site =", site)
                .filter("observation_date", obs_date)
                .order("-observation_datetime"))
        return q.fetch(offset = offset, limit = limit)


