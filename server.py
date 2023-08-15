from flask import Flask, redirect, url_for
from Controller.DigitalForecast import DigitalForecast
from Controller.HomeController import HomeController

app = Flask(__name__)


@app.route("/")
def Home():
  return redirect(url_for('HomeXML'))

@app.route("/home-json")
def HomeJSON():
  data = HomeController.load_home_json()
  return data


@app.route("/home-xml")
def HomeXML():
  data = HomeController.load_home_xml()
  return data


@app.route("/<provinceName>")
def Province(provinceName):
  data = DigitalForecast.selectProvince(provinceName)
  return data


@app.route("/<provinceName>/<area_id>")
def areaID(provinceName, area_id):
  data = DigitalForecast.selectAreaID(provinceName, area_id)
  return data


@app.route("/<provinceName>/<area_id>/<parameter_id>")
def parameterID(provinceName, area_id, parameter_id):
  data = DigitalForecast.selectParameterID(provinceName, area_id, parameter_id)
  return data


@app.route("/<provinceName>/<area_id>/<parameter_id>/<timerange>")
def Timerange(provinceName, area_id, parameter_id, timerange):
  data = DigitalForecast.selectTimerange(provinceName, area_id, parameter_id,
                                         timerange)
  return data


# Define the route for /favicon.ico
@app.route('/favicon.ico')
def favicon():
  return '', 404  # Return a 404 response to block favicon requests
