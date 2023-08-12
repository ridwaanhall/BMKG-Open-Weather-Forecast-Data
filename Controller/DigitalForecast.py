import requests, xmltodict, json
from datetime import datetime


class DigitalForecast:

  @staticmethod
  def read_data_from_url(url):
    try:
      response = requests.get(url)
      response.raise_for_status(
      )  # Raise an exception for 4xx or 5xx status codes
      data_dict = xmltodict.parse(response.content)
      json_data = json.dumps(data_dict)
      return json_data
    except requests.exceptions.RequestException as e:
      # Handle the error case
      print(f"Error: {e}")
      return None

  # =====================================

  @staticmethod
  def read_extract_data(provinceName):
    url = f"https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-{provinceName}.xml"
    json_data = DigitalForecast.read_data_from_url(url)
    data = DigitalForecast.extract_data(json_data)
    return data

  @staticmethod
  def selectProvince(provinceName):
    data = DigitalForecast.read_extract_data(provinceName)

    areas = {
      "area_id": data["area_id"],
      "coordinate": data["coordinate"],
      "description": data["description"],
      "domain": data["domain"],
      "latitude": data["latitude"],
      "level": data["level"],
      "longitude": data["longitude"],
      "names": data["names"]
    }

    issue_info = data["issue"]

    forecast = {"issue": issue_info, "area": areas}
    return forecast

  @staticmethod
  def selectAreaID(provinceName, area_id):
    data = DigitalForecast.read_extract_data(provinceName)
    # Find the area with the specified area_id
    area_info = next((a for a in data['area'] if a['area_id'] == area_id),
                     None)
    if area_info:
      parameters = area_info['parameters']
    else:
      parameters = []

    return parameters

  @staticmethod
  def selectParameterID(provinceName, area_id, parameter_id):
    data = DigitalForecast.read_extract_data(provinceName)
    # Find the area with the specified area_id
    area_info = next((a for a in data['area'] if a['area_id'] == area_id),
                     None)
    if area_info:
      parameters = area_info['parameters']
      parameter_info = next(
        (p for p in parameters if p['parameter_id'] == parameter_id), None)
      if parameter_info:
        #parameter_description = parameter_info['description']
        timeranges = parameter_info['timeranges']
        # Format datetime for each timerange
        #for timerange in timeranges:
        #  datetime_str = timerange['datetime']
        #  datetime_obj = datetime.strptime(datetime_str, "%Y%m%d%H%M")
        #  formatted_time = datetime_obj.strftime("%H:%M")
        #  formatted_day = datetime_obj.strftime("%A")
        #  formatted_date = datetime_obj.strftime("%d %B %Y")
        #  timerange['formatted_time'] = formatted_time
        #  timerange['formatted_day'] = formatted_day
        #  timerange['formatted_date'] = formatted_date

        return timeranges

    return "Parameter not found"

  @staticmethod
  def selectTimerange(provinceName, area_id, parameter_id, timerange):
    data = DigitalForecast.read_extract_data(provinceName)
    # Find the area with the specified area_id
    area_info = next((a for a in data['area'] if a['area_id'] == area_id),
                     None)
    if area_info:
      parameters = area_info['parameters']
      parameter_info = next(
        (p for p in parameters if p['parameter_id'] == parameter_id), None)
      if parameter_info:
        #parameter_description = parameter_info['description']
        timeranges = parameter_info['timeranges']

        if parameter_info['type'] == 'hourly':
          timerange_info = next(
            (t for t in timeranges
             if t['type'] == 'hourly' and t['h'] == timerange), None)
        elif parameter_info['type'] == 'daily':
          timerange_info = next(
            (t for t in timeranges
             if t['type'] == 'daily' and t['day'] == timerange), None)
        else:
          timerange_info = None

        if timerange_info:
          values = timerange_info['values']
          if values:
            # Format datetime
            #datetime_str = timerange_info['datetime']
            #datetime_obj = datetime.strptime(datetime_str, "%Y%m%d%H%M")
            #formatted_time = datetime_obj.strftime("%H:%M")
            #formatted_day = datetime_obj.strftime("%A")
            #formatted_date = datetime_obj.strftime("%d %B %Y")

            return values
          else:
            return "No values available for the specified parameter and timerange."

    return "Parameter or timerange not found"

  # ====================

  @staticmethod
  def extract_data(json_data):
    data = json.loads(json_data)
    issue = data['data']['forecast']['issue']
    area = data['data']['forecast']['area']

    timestamp = issue['timestamp']
    year = issue['year']
    month = issue['month']
    day = issue['day']
    hour = issue['hour']
    minute = issue['minute']
    second = issue['second']

    area_info = []
    for a in area:
      area_id = a['@id']
      description = a['@description']
      latitude = a['@latitude']
      longitude = a['@longitude']
      coordinate = a['@coordinate']
      area_type = a['@type']
      region = a['@region']
      level = a['@level']
      domain = a['@domain']
      tags = a['@tags']

      names = {}
      for name in a['name']:
        lang = name['@xml:lang']
        text = name['#text']
        if lang == 'id_ID':
          names[lang] = text

      for name in a['name']:
        lang = name['@xml:lang']
        text = name['#text']
        if lang == 'en_US':
          names[lang] = text

      parameters = []
      for parameter in a.get('parameter', []):
        parameter_id = parameter['@id']
        parameter_description = parameter['@description']
        parameter_type = parameter['@type']

        timeranges = []
        for timerange in parameter.get('timerange', []):
          if isinstance(timerange, dict):
            timerange_type = timerange['@type']
            timerange_day = timerange.get('@day')
            timerange_h = timerange.get('@h')
            timerange_datetime = timerange['@datetime']

            datetime_str = timerange['@datetime']
            datetime_obj = datetime.strptime(datetime_str, "%Y%m%d%H%M")
            formatted_time = datetime_obj.strftime("%H:%M")
            formatted_day = datetime_obj.strftime("%A")
            formatted_date = datetime_obj.strftime("%d %B %Y")
            #  timerange['formatted_time'] = formatted_time
            #  timerange['formatted_day'] = formatted_day
            #  timerange['formatted_date'] = formatted_date

            values = []
            value = timerange.get('value')
            if isinstance(value, list):
              for val in value:
                value_unit = val.get('@unit')
                value_text = val.get('#text')
                if parameter_id == 'weather':
                  value_text = DigitalForecast.get_weather_description(
                    value_text)
                elif parameter_id == 'wd':
                  if value_unit == 'CARD':
                    value_text = DigitalForecast.get_wind_direction_description(
                      value_text)
                values.append({'unit': value_unit, 'text': value_text})
            elif isinstance(value, dict):
              value_unit = value.get('@unit')
              value_text = value.get('#text')
              if parameter_id == 'weather':
                value_text = DigitalForecast.get_weather_description(
                  value_text)
              elif parameter_id == 'wd':
                if value_unit == 'CARD':
                  value_text = DigitalForecast.get_wind_direction_description(
                    value_text)
              values.append({'unit': value_unit, 'text': value_text})

            timeranges.append({
              'type': timerange_type,
              'day': timerange_day,
              'h': timerange_h,
              'datetime': timerange_datetime,
              'formatted_time': formatted_time,
              'formatted_day': formatted_day,
              'formatted_date': formatted_date,
              'values': values
            })

        parameters.append({
          'parameter_id': parameter_id,
          'description': parameter_description,
          'type': parameter_type,
          'timeranges': timeranges
        })

      area_info.append({
        'area_id': area_id,
        'description': description,
        'latitude': latitude,
        'longitude': longitude,
        'coordinate': coordinate,
        'type': area_type,
        'region': region,
        'level': level,
        'domain': domain,
        'tags': tags,
        'names': names,
        'parameters': parameters
      })

    return {
      'issue': {
        'timestamp': timestamp,
        'year': year,
        'month': month,
        'day': day,
        'hour': hour,
        'minute': minute,
        'second': second
      },
      'area': area_info
    }

  @staticmethod
  def get_weather_description(code):
    weather_code = {
      "0": "Cerah / Clear Skies",
      "1": "Cerah Berawan / Partly Cloudy",
      "2": "Cerah Berawan / Partly Cloudy",
      "3": "Berawan / Mostly Cloudy",
      "4": "Berawan Tebal / Overcast",
      "5": "Udara Kabur / Haze",
      "10": "Asap / Smoke",
      "45": "Kabut / Fog",
      "60": "Hujan Ringan / Light Rain",
      "61": "Hujan Sedang / Rain",
      "63": "Hujan Lebat / Heavy Rain",
      "80": "Hujan Lokal / Isolated Shower",
      "95": "Hujan Petir / Severe Thunderstorm",
      "97": "Hujan Petir / Severe Thunderstorm"
    }

    return weather_code.get(code, "")

  @staticmethod
  def get_wind_direction_description(code):
    wind_direction_code = {
      "N": "North",
      "NNE": "North-Northeast",
      "NE": "Northeast",
      "ENE": "East-Northeast",
      "E": "East",
      "ESE": "East-Southeast",
      "SE": "Southeast",
      "SSE": "South-Southeast",
      "S": "South",
      "SSW": "South-Southwest",
      "SW": "Southwest",
      "WSW": "West-Southwest",
      "W": "West",
      "WNW": "West-Northwest",
      "NW": "Northwest",
      "NNW": "North-Northwest",
      "VARIABLE": "berubah-ubah"
    }

    return wind_direction_code.get(code, "")
