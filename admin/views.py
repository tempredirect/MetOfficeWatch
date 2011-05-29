from google.appengine.api import urlfetch,taskqueue
from google.appengine.api.datastore_types import GeoPt
from google.appengine.ext import db
from flask import Response, render_template, redirect, request
from flask.helpers import url_for, flash

from admin   import app
from models import Site, ForecastTimestep, ObservationTimestep, ForecastDay, ObservationDay, make_key_name, Weather, Observations

import simplejson as json
import logging
from utils import chunks, snake_case
from datetime import datetime
from lib.iso8601 import parse_date

@app.route('/admin')
def index():                             
    return render_template('index.html')


def parse_locations(content):
    data = json.loads(content)
    for i in data["xs"]["x"]:
        yield {
            "id":i["@i"],
            "name":i["@n"],
            "type":i["@t"],
            "location": [float(i["@l"]),float(i["@g"])],
            "region":i["@r"]
        }

@app.route('/admin/sites')
def sites():
    return render_template("sites.html", sites = Site.all().fetch(limit = 200))

@app.route('/admin/sites/refresh')
def sites_update():
    master_list = "http://www.metoffice.gov.uk/public/data/PWSCache/Locations/MasterList?format=application/json"
#    master_list = "http://localhost/~gareth/MasterList.json"

    result = urlfetch.fetch(master_list)

    if result.status_code == 200:
        obs_sites = filter(lambda loc: loc["type"] == "Observing Site", parse_locations(result.content))
        for chunk in chunks(obs_sites,10):
            taskqueue.add(url="/admin/sites/store", params = {"sites":json.dumps(chunk)})
        flash("Started load of %d sites" % len(obs_sites))
    else:
        flash("Error fetching MasterList: [%d] - %s" % (result.status_code, result.status_message))

    return redirect(url_for('index'))


@app.route('/admin/sites/store', methods = ['post'])
def sites_store():
    for loc in json.loads(request.form.get("sites")):
        def _tx():
            site = Site.get_by_key_name(loc["id"])
            if site is None:
                site = Site(key_name=loc["id"])
            site.location = GeoPt(lat = loc["location"][0], lon = loc["location"][1])
            site.name = loc["name"]
            site.region = loc["region"]
            site.save()
        db.run_in_transaction(_tx)
    return Response(status = 204)


def parse_forecast(content):
    return json.loads(content)["BestFcst"]["Forecast"]

def parse_observation(content):
    return json.loads(content)["BestFcst"]["Observations"]

def ensure_array(value):
    if isinstance(value, list) or value is None:
        return value
    # else wrap it up
    return [value]

def timesteps(data):
    days = data["Location"]["Day"]
    for day in ensure_array(days):
        date = day["@date"]
        for ts in ensure_array(day["TimeSteps"]["TimeStep"]):
            time = ts["@time"]
            timestamp = parse_date("%sT%s.000Z" % (date, time))
            yield timestamp, ts["WeatherParameters"]

@app.route('/admin/forecast/update')
def forecast_update_all():

    sites = Site.all().fetch(limit = 200)
    for site in sites:
        taskqueue.add(url = "/admin/forecast/%s/update" % site.key().id_or_name(), queue_name="update")

    if request.args.get("redirect"):
        flash("Started update forecast tasks for all sites")
        return redirect(url_for('sites'))

    return Response(status = 204)

@app.route('/admin/observation/update')
def observation_update_all():

    sites = Site.all().fetch(limit = 200)
    for site in sites:
        taskqueue.add(url = "/admin/sites/%s/observation/update" % site.key().id_or_name(), queue_name="update")
        taskqueue.add(url = "/admin/sites/%s/observation/update2" % site.key().id_or_name(), queue_name="update")

    if request.args.get("redirect"):
        flash("Started update observation tasks for all sites")
        return redirect(url_for('sites'))

    return Response(status = 204)

@app.route('/admin/forecast/<site_key>/update', methods = ['post'])
def forecast_update(site_key):
    site = Site.get_by_key_name(site_key)
    if site is None:
        return Response(status = 404)

    forecast_url = "http://www.metoffice.gov.uk/public/data/PWSCache/BestForecast/Forecast/%s?format=application/json" % site_key

    result = urlfetch.fetch(forecast_url)
    if result.status_code == 200:
        forecast = parse_forecast(result.content)
        issued_date = parse_date(forecast["@dataDate"])
        for date, data in timesteps(forecast):
            forecast_timestep = ForecastTimestep.find_by_site_and_dates(site, date, issued_date)
            if forecast_timestep is None:
                forecast_timestep = ForecastTimestep(site = site, forecast_datetime = date, issued_datetime = issued_date, forecast_date = date.date())

                for k,v in data.items():
                    prop_name = snake_case(k)
                    if hasattr(forecast_timestep, prop_name):
                        if v == "missing":
                            v = None
                        setattr(forecast_timestep, prop_name, v)

                forecast_timestep.save()

    return Response(status = 204)

@app.route('/admin/sites/<site_key>/observation/update', methods = ['post'])
def observation_update(site_key):
    site = Site.get_by_key_name(site_key)
    if site is None:
        return Response(status = 404)

    url = "http://www.metoffice.gov.uk/public/data/PWSCache/BestForecast/Observation/%s?format=application/json" % site_key

    obs = {}
    def get_db_observation(date):
        key_name = make_key_name(site, date.date())
        if key_name in obs:
            return obs[key_name]

        o = ObservationDay.get_by_key_name(key_name)
        if o is None:
            o = ObservationDay(key_name=key_name)
            o.site = site
            o.observation_date = date.date()
            o.observations = Observations()

        obs[key_name] = o
        return o

    result = urlfetch.fetch(url)
    if result.status_code == 200:
        observations = parse_observation(result.content)

        issue_date = parse_date(observations['@issueDate'])
        site.last_obs_issue_datetime = issue_date
        site.last_obs_update_datetime = datetime.now()
        for date, data in timesteps(observations):
            o = get_db_observation(date)
            o.lastdata_datetime = issue_date
            w = Weather({})
            for k,v in data.items():
                prop_name = snake_case(k)
                if hasattr(w, prop_name):
                    if v == "missing":
                        v = None
                    elif prop_name == 'temperature':
                        v = float(v)
                    setattr(w, prop_name, v)
            o.observations.add(date.time().isoformat(), w)

        for o in obs.values():
            o.save()
        site.save()

    return Response(status = 204)


# keep the old update routine for now :)
@app.route('/admin/sites/<site_key>/observation/update2', methods = ['post'])
def observation_update2(site_key):
    site = Site.get_by_key_name(site_key)
    if site is None:
        return Response(status = 404)

    url = "http://www.metoffice.gov.uk/public/data/PWSCache/BestForecast/Observation/%s?format=application/json" % site_key

    result = urlfetch.fetch(url)
    if result.status_code == 200:
        observations = parse_observation(result.content)
#        issued_date = parse_date(forecast["@dataDate"])
        for date, data in timesteps(observations):
            obs_timestep = ObservationTimestep.get_by_site_and_datetime(site, date)
            if obs_timestep is None:
                obs_timestep = ObservationTimestep(site = site, observation_datetime = date, observation_date = date.date())

                for k,v in data.items():

                    prop_name = snake_case(k)
                    if hasattr(obs_timestep, prop_name):
                        if v == "missing":
                            v = None
                        elif prop_name == 'temperature':
                            v = float(v)
                        setattr(obs_timestep, prop_name, v)

                obs_timestep.save()
            #logging.info("%s, %s" % (str(date), str(ObservationTimestep)))

    return Response(status = 204)