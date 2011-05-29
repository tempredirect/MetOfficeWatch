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

class Weather(JsonMixin):
    property_names = ['wind_gust',
                      'wind_speed',
                      'wind_direction',
                      'pressure',
                      'pressure_tendency',
                      'screen_relative_humidity',
                      'weather_type',
                      'temperature',
                      'visibility',
                      'feels_like_temperature',
                      'max_uv_index',
                      'screen_relative_humidity']

    def __init__(self, values):
        for name in Weather.property_names:
            if name in values:
                setattr(self, name, values[name])
            else:
                setattr(self, name, None)

    def to_json(self):
        result = {}
        for name in Weather.property_names:
            value = getattr(self,name)
            if value is not None:
                result[name] = value

        return result

    @classmethod
    def from_json(cls, json):
        return Weather(json)

class Forecast(Weather):

    def __init__(self, values):
        super(values)
        self.issued = parse_date(values.issued)

    def to_json(self):
        result = super.to_json()
        result.issued = jsonvalue(self.issued)
        return result

    @classmethod
    def from_json(cls, json):
        return Forecast(json)

class Forecasts(JsonMixin):
    def __init__(self):
        self.forecasts = {}

    def add(self, time, forecast):
        if time in self.forecasts:
            self.forecasts[time].append(forecast)
        else:
            self.forecasts[time] = [forecast]

    def __getitem__(self, item):
        return self.forecasts[item]

    def to_json(self):
        result = {}
        for k,v in self.forecasts.items():
            result[k] = v.to_json()
        return result

    @classmethod
    def from_json(cls, json):
        f = Forecasts()
        for k,v in json.items():
            f.add(k, Forecasts(v))
        return f

class Observations(JsonMixin):
    def __init__(self):
        self.observations = {}

    def add(self, time, weather):
        self.observations[time] = weather

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

class Site(DictModel):
    name = db.StringProperty()
    location = db.GeoPtProperty()
    region = db.StringProperty()
    last_obs_issue_datetime = db.DateTimeProperty()
    last_obs_update_datetime = db.DateTimeProperty()

class ForecastDay(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    forecast_date = db.DateProperty()
    forecasts = JsonProperty(Forecasts)


class ObservationDay(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    observation_date = db.DateProperty()
    lastdata_datetime = db.DateTimeProperty()
    observations = JsonProperty(Observations, default=Observations())


class ForecastTimestep(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    forecast_datetime = db.DateTimeProperty()
    forecast_date = db.DateProperty()
    issued_datetime = db.DateTimeProperty()

    feels_like_temperature = db.IntegerProperty()
    temperature = db.IntegerProperty()
    max_uv_index = db.IntegerProperty()
    wind_gust = db.IntegerProperty()
    pressure = db.IntegerProperty()
    screen_relative_humidity = db.IntegerProperty()
    weather_type = db.IntegerProperty()
    visibility = db.IntegerProperty()
    wind_direction = db.StringProperty()
    wind_speed = db.IntegerProperty()

    @classmethod
    def find_by_site_and_dates(cls, site, forecast_date, issued_date):
        q = ForecastTimestep.all()
        q.filter("site =", site)
        q.filter("forecast_datetime =", forecast_date)
        q.filter("issued_datetime =", issued_date)

        return q.get()

    @classmethod
    def find_by_site_between_dates(cls, site, from_dt, to_dt):
        q = (ForecastTimestep.all()
                .filter("site =", site)
                .filter("forecast_datetime >=", from_dt)
                .filter("forecast_datetime <=", to_dt))

        return q.fetch(limit = 500)

    @classmethod
    def find_by_site_closest_by_date(cls, site, date_and_time, limit=1):
        q = (ForecastTimestep.all()
                .filter("site =", site)
                .filter("forecast_datetime <=", date_and_time)
                .order("-forecast_datetime"))
        return q.fetch(limit = limit)

    def forecast_range(self):
        """Returns the number of days this forecast was give out at.
           0 == issued on the day of forecast
           4 == fifth day forecast
        """
        delta = self.forecast_date - self.issued_datetime.date()
        return delta.days

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


