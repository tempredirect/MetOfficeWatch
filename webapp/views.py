from functools import wraps
from flask import Response, render_template, redirect, redirect, request

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