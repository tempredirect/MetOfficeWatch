import dataccess
from flask import Response, render_template, redirect, redirect, request
from models import Site, ObservationTimestep, Forecast, ForecastTimestep, ForecastDay, make_key_name, ObservationDay
from utils import first, last, parse_yyyy_mm_dd_date

from webapp import app
import simplejson as json
from datetime import date

def to_dict(obj):
    return obj.to_dict()

def json_list_response(list):
    return Response(json.dumps(map(to_dict,list)), content_type = 'application/json')

def json_response(value):
    dict_value = value if isinstance(value, dict) else value.to_dict()
    return Response(json.dumps(dict_value), content_type = 'application/json')

@app.route('/sites')
def sites():
    return json_list_response(Site.all().fetch(limit = 200))

@app.route('/sites/<site_id>')
def site_by_id(site_id):
    site = Site.get_by_key_name(site_id)
    if site is None:
        return Response(status = 404)
    return json_response(site)

@app.route('/sites/<site_id>/forecasts')
def site_forecasts(site_id):
    site = Site.get_by_key_name(site_id)
    if site is None:
        return Response(status = 404)

    if request.args.has_key('day'):
        p = request.args.get('day')
        day = parse_yyyy_mm_dd_date(p)
    else:
        return Response("day query parameter is required",status = 400)

    forecast_day = ForecastDay.get_by_key_name(make_key_name(site,day))

    if forecast_day is None:
        return Response(status = 404)

    return json_response(forecast_day)

@app.route('/sites/<site_id>/observations')
def site_observations(site_id):
    site = Site.get_by_key_name(site_id)
    if site is None:
        return Response(status = 404)

    if request.args.has_key('day'):
        p = request.args.get('day')
        day = parse_yyyy_mm_dd_date(p)
    else:
        return Response("day query parameter is required",status = 400)

    observation_day = ObservationDay.get_by_key_name(make_key_name(site,day))

    if observation_day is None:
        return Response(status = 404)

    return json_response(observation_day)


@app.route('/sites/<site_id>/latest')
def site_latest(site_id):
    result = dataccess.latest_obs_and_forecast(site_id)
    if result is None:
        return Response(status = 404)

    return Response(json.dumps(result), content_type = "application/json")

@app.route('/sites/<site_id>/detail')
def site_detail(site_id):
    site = Site.get_by_key_name(site_id)
    if site is None:
        return Response(status = 404)

    obs = ObservationTimestep.find_latest_by_site(site = site, limit = 24)
    forecasts = []
    if len(obs) > 0:
        first_obs = first(obs)
        last_obs = last(obs)

        forecasts = ForecastTimestep.find_by_site_between_dates( site = site,
                                                                 from_dt = last_obs.observation_datetime,
                                                                 to_dt = first_obs.observation_datetime)
    return Response(json.dumps({
       'site': site.to_dict(),
       'observations': map(lambda o: o.to_dict(excluding = ['site']), obs),
       'forecasts': map(lambda f: f.to_dict(excluding = ['site']), forecasts)
    }), content_type = "application/json")


@app.route('/sites/<site_id>/series')
def site_graph_data(site_id):
    site = Site.get_by_key_name(site_id)
    if site is None:
        return Response(status = 404)

    day = date.today()
    if request.args.has_key('day'):
        p = request.args.get('day')
        day = parse_yyyy_mm_dd_date(p)

    # obs data first
    obs = ObservationTimestep.find_by_site_and_date(site, day)

    series = [make_series('Observation temperature &degC', obs, 'observation_datetime', 'temperature')]

    return json_response({'day': str(day), 'series': series})

def make_series(title, values, time_name, value_name):
    return {
        'name': title,
        'data': map(lambda x: (getattr(x,time_name).isoformat(), getattr(x, value_name)), values if values is not None else [])
    }