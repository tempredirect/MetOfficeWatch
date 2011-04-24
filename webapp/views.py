from functools import wraps
from flask import Response, render_template, redirect, redirect, request
from models import Site, ObservationTimestep, Forecast, ForecastTimestep
from utils import first, last

from webapp import app
import simplejson as json
from google.appengine.api import users
from google.appengine.ext import db
from datetime import date

import logging

def to_dict(obj):
    return obj.to_dict()

def json_list_response(list):
    return Response(json.dumps(map(to_dict,list)), content_type = 'application/json')

def json_response(value):
    return Response(json.dumps(value.to_dict()), content_type = 'application/json')

def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        current_user = users.get_current_user()
        if users.is_current_user_admin()  or current_user.email() == "gareth@logicalpractice.com" :
            return func(*args, **kwargs)
        return redirect(users.create_login_url(request.url))

    return decorated_view

@app.route('/')
def index():                             
    return render_template('index.html')

@app.route('/sites')
def sites():
    return json_list_response(Site.all().fetch(limit = 200))

@app.route('/sites/<site_id>/latest')
def site_latest(site_id):
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