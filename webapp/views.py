from functools import wraps
import dataccess
from flask import Response, render_template, redirect, redirect, request
from models import Site, ObservationTimestep, Forecast, ForecastTimestep
from utils import first, last, parse_yyyy_mm_dd_date

from webapp import app
import simplejson as json
from google.appengine.api import users
from google.appengine.ext import db
from datetime import date
from lib.iso8601 import parse_date
import logging

def to_dict(obj):
    return obj.to_dict()

def json_list_response(list):
    return Response(json.dumps(map(to_dict,list)), content_type = 'application/json')

def json_response(value):
    dict_value = value if isinstance(value, dict) else value.to_dict()
    return Response(json.dumps(dict_value), content_type = 'application/json')

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

@app.route('/sites/<site_id>/graph')
def site_graph(site_id):
    site = Site.get_by_key_name(site_id)
    if site is None:
        return Response(status = 404)

    return render_template('graph.html', site = site)

