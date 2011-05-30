from datetime import datetime
from google.appengine.ext import db
from jsonproperty import JsonMixin, JsonProperty
from lib.iso8601 import parse_date
from models import DictModel, Site, jsonvalue, Weather
from utils import SparseList

def forecast_range(forecast, issued):
    """Returns the number of days this forecast was give out at.
       0 == issued on the day of forecast
       4 == fifth day forecast
    """
    if isinstance(forecast, datetime):
        forecast = forecast.date()
    if isinstance(issued, datetime):
        issued = issued.date()
    delta = forecast - issued
    return delta.days

class Forecast(Weather):

    def __init__(self, values = {}):
        super(Forecast,self).__init__(values)
        self.issued = parse_date(values['issued']) if 'issued' in values else None

    def to_json(self):
        result = super(Forecast,self).to_json()
        result['issued'] = jsonvalue(self.issued)
        return result

    @classmethod
    def from_json(cls, json):
        return Forecast(json)

class Forecasts(JsonMixin):
    """
     [0, {
            "10:00:00": [
                       { forecast1 },
                       { forecast2 },
                    ]
         }
      1, {}
      2, {}]
    """
    def __init__(self):
        self.forecasts = SparseList()

    def add(self, forecast_datetime, forecast):
        r = forecast_range(forecast_datetime, forecast.issued)

        time = forecast_datetime.time().isoformat()
        forecasts_by_time = self.forecasts[r]
        if forecasts_by_time is None:
            forecasts_by_time = self.forecasts[r] = {}

        if time in forecasts_by_time:

            forecast_list = forecasts_by_time[time]
            # check for existing forecast by issue
            def indexof():
                issued = forecast.issued
                for i,f in enumerate(forecast_list):
                    if f.issued == issued:
                        return i
                return -1
            i = indexof()

            if i > -1:
                forecast_list[i] = forecast
            else:
                forecast_list.append(forecast)
        else:
            forecasts_by_time[time] = [forecast]

    def __getitem__(self, item):
        return self.forecasts[item]

    def to_json(self):
        result = []
        for v in self.forecasts:
            if v is not None:
                forecasts_by_time = {}
                for time,forecast_list in v.iteritems():
                    forecasts_by_time[time] = map(lambda f: f.to_json(), forecast_list)
                result.append(forecasts_by_time)
            else:
                result.append(None)
        return result

    @classmethod
    def from_json(cls, json):
        f = Forecasts()
        for v in json:
            if v is not None:
                forecasts_by_time = {}
                for time, forecast_list in v.iteritems():
                    forecasts_by_time[time] = map(lambda v: Forecast.from_json(v), forecast_list)
                f.forecasts.append(forecasts_by_time)
            else:
                f.forecasts.append(None)
        return f


class ForecastDay(DictModel):
    site = db.ReferenceProperty(reference_class=Site)
    forecast_date = db.DateProperty()
    lastdata_datetime = db.DateTimeProperty()
    forecasts = JsonProperty(Forecasts, default=Forecasts())


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
