from google.appengine.api import memcache

from models import Site, ObservationTimestep, ForecastTimestep

from utils import first
from itertools import ifilter

def latest_obs_and_forecast(site_id):
    result = memcache.get(site_id, "site_latest")
    if result:
        return result

    site = Site.get_by_key_name(site_id)
    if site is None:
        return None

    obs = ObservationTimestep.find_latest_by_site(site, limit=6)
    result = None

    if len(obs) > 0:
        forecasts = ForecastTimestep.find_by_site_closest_by_date(site, first(obs).observation_datetime,
                                                                  limit=15)
        closest_forecast = first(forecasts)
        if closest_forecast:
            matching_obs = first(filter(lambda o: o.observation_datetime == closest_forecast.forecast_datetime, obs))
            matching_forecasts = ifilter(lambda f: f.forecast_datetime == closest_forecast.forecast_datetime, forecasts)
            if matching_obs:
                #finally have both... a single obs report and multiple forecasts
                result = {
                    'site': site.to_dict(),
                    'observation': matching_obs.to_dict(excluding = ['site']),
                    'forecasts': map(lambda f: f.to_dict(excluding=['site']),  matching_forecasts)
                }
                memcache.set(site_id, result, 60 * 60, namespace='site_latest')

    return result
