import json, xmltodict
from flask import Response

class HomeController:

  @staticmethod
  def load_home_json():
    with open('Data/home.json', 'r') as json_file:
      data = json.load(json_file)
    return data

  @staticmethod
  def load_home_xml():
    data = HomeController.load_home_json()
    xml_data = xmltodict.unparse({"data": data}, pretty=True)
    return Response(xml_data, content_type='text/xml')