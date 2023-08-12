from flask import Flask
from Controller.DigitalForecast import DigitalForecast

app = Flask(__name__)

# ======================


@app.route("/<provinceName>")
def Province(provinceName):
  data = DigitalForecast.read_extract_data(provinceName)
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