from google.appengine.ext import db
from jsonproperty import JsonMixin, JsonProperty
from lib.iso8601 import parse_date
from models import DictModel, Site, jsonvalue, Weather

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


class ForecastDay(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    forecast_date = db.DateProperty()
    forecasts = JsonProperty(Forecasts)


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
