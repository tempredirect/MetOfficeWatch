from jsonproperty import JsonMixin

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
