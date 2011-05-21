from google.appengine.api import memcache

from models import Site, ObservationTimestep, ForecastTimestep

from utils import first, SparseList
from itertools import ifilter

def to_dict_excl_sites(o):
    if o is not None:
        return o.to_dict(excluding=['site'])
    return None

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
                                                                  limit=50)
        closest_forecast = first(forecasts)
        if closest_forecast:
            matching_obs = first(filter(lambda o: o.observation_datetime == closest_forecast.forecast_datetime, obs))
            matching_forecasts = ifilter(lambda f: f.forecast_datetime == closest_forecast.forecast_datetime, forecasts)
            if matching_obs:
                #finally have both... a single obs report and multiple forecasts

                obs_dict = to_dict_excl_sites(matching_obs)
                obs_dict['best_forecast'] = map(to_dict_excl_sites,  make_five_day_list(matching_forecasts))
                result = {
                    'site': site.to_dict(),
                    'observation': obs_dict
                }
                memcache.set(site_id, result, 60 * 60, namespace='site_latest')

    return result

def make_five_day_list(forecasts, min = 5):
    slist = SparseList([None for i in range(0,min)])
    for f in forecasts:
        r = f.forecast_range()
        if slist[r] is None:
            slist[r] = [f]
        else:
            slist[r].append(f)

    return map(lambda a: first(a), slist)