import requests, xmltodict, json, difflib
from datetime import datetime

# make process data.


class DataValidation:

  @staticmethod
  def get_reference_texts():
    return {
      "Aceh", "Bali", "BangkaBelitung", "Banten", "Bengkulu", "DIYogyakarta",
      "DKIJakarta", "Gorontalo", "Jambi", "JawaBarat", "JawaTengah",
      "JawaTimur", "KalimantanBarat", "KalimantanSelatan", "KalimantanTengah",
      "KalimantanTimur", "KalimantanUtara", "KepulauanRiau", "Lampung",
      "Maluku", "MalukuUtara", "NusaTenggaraBarat", "NusaTenggaraTimur",
      "Papua", "PapuaBarat", "Riau", "SulawesiBarat", "SulawesiSelatan",
      "SulawesiTengah", "SulawesiTenggara", "SulawesiUtara", "SumateraBarat",
      "SumateraSelatan", "SumateraUtara", "Indonesia"
    }


class DigitalForecast:

  @staticmethod
  def read_data_from_url(url):
    try:
      response = requests.get(url)
      if response.status_code == 200:
        data_dict = xmltodict.parse(response.content)
        json_data = json.dumps(data_dict)
        return json_data
      elif response.status_code == 404:
        return None
      else:
        print(f"Error: Unexpected status code - {response.status_code}")
        return None
    except requests.exceptions.RequestException as e:
      # Handle other request exceptions
      print(f"Error: {e}")
      return None

  # =====================================

  @staticmethod
  def read_extract_data(provinceName):
    url = f"https://data.bmkg.go.id/DataMKG/MEWS/DigitalForecast/DigitalForecast-{provinceName}.xml"
    json_data = DigitalForecast.read_data_from_url(url)
    data = DigitalForecast.extract_data(json_data, provinceName)
    return data

  # ====================

  @staticmethod
  def extract_data(json_data, provinceName):
    reference_texts = DataValidation.get_reference_texts()
    if json_data is None:
      suggestion = difflib.get_close_matches(provinceName.lower(),
                                             reference_texts,
                                             n=1)
      if suggestion:
        suggestion = suggestion[0]
      else:
        return {
          'code':
          404,
          'messageOwner':
          f"apaan dah ni '{provinceName}'.isi yang bener ya, sodara. jangan banyak typo!!"
        }

      return {
        'code':
        404,
        'message':
        f"Province with Name '{provinceName}' not found. did you mean '{suggestion}'?"
      }

    try:
      data = json.loads(json_data)
      if 'data' in data and 'forecast' in data['data']:
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
      else:
        print("Error: Invalid JSON data format")
        return None, None
    except json.JSONDecodeError:
      print("Error: Unable to decode JSON data")
      return None, None

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

  # ===========================================

  @staticmethod
  def selectProvince(provinceName):
    data = DigitalForecast.read_extract_data(provinceName)
    reference_texts = DataValidation.get_reference_texts()
    # Initialize a new JSON structure to store the extracted data
    extracted_result = {"areas": [], "issue_info": {}}

    if 'area' in data:
      # Extract area information
      area_data = data["area"]
      for area in area_data:
        area_info = {
          "area_id": area["area_id"],
          "description": area["description"],
          "domain": area["domain"],
          "coordinate": area["coordinate"],
          "latitude": area["latitude"],
          "longitude": area["longitude"],
          "level": area["level"],
          "region": area["region"],
          "tags": area["tags"],
          "type": area["type"],
          "names": {
            "en_US": area["names"]["en_US"],
            "id_ID": area["names"]["id_ID"]
          }
        }
        extracted_result["areas"].append(area_info)

      # Extract issue timestamp
      issue_data = data["issue"]
      extracted_result["issue_info"] = {
        "timestamp":
        issue_data["timestamp"],
        "date":
        f"{issue_data['year']}-{issue_data['month']}-{issue_data['day']}",
        "time":
        f"{issue_data['hour']}:{issue_data['minute']}:{issue_data['second']}"
      }
    else:
      suggestion = difflib.get_close_matches(provinceName.lower(),
                                             reference_texts,
                                             n=1)
      if suggestion:
        suggestion = suggestion[0]
      else:
        return {
          'code':
          404,
          'messageOwner':
          f"apaan dah ni '{provinceName}'.isi yang bener ya, sodara. jangan banyak typo!!"
        }

      extracted_result = {
        "code":
        404,
        "message":
        f"Province with Name '{provinceName}' not found. Did you mean '{suggestion}'?"
      }, 404

    return extracted_result

  @staticmethod
  def selectAreaID(provinceName, area_id):
    data = DigitalForecast.read_extract_data(provinceName)
    reference_texts = DataValidation.get_reference_texts()

    if 'area' in data:
      # Find the area with the specified area_id
      area_info = next((a for a in data['area'] if a['area_id'] == area_id),
                       None)
      if area_info:
        parameters = area_info['parameters'], 200
      else:
        parameters = {
          "code": 404,
          "message": f"'Area with ID '{area_id}' not found."
        }, 404
    else:
      suggestion = difflib.get_close_matches(provinceName.lower(),
                                             reference_texts,
                                             n=1)
      if suggestion:
        suggestion = suggestion[0]
      else:
        return {
          'code':
          404,
          'messageOwner':
          f"apaan dah ni '{provinceName}'.isi yang bener ya, sodara. jangan banyak typo!!"
        }

      parameters = {
        "code":
        404,
        "message":
        f"Province with Name '{provinceName}' not found. Did you mean '{suggestion}'?"
      }, 404

    return parameters

  @staticmethod
  def selectParameterID(provinceName, area_id, parameter_id):
    data = DigitalForecast.read_extract_data(provinceName)
    reference_texts = DataValidation.get_reference_texts()

    if 'area' in data:
      # Find the area with the specified area_id
      area_info = next((a for a in data['area'] if a['area_id'] == area_id),
                       None)
      if area_info:
        parameters = area_info['parameters']
        parameter_info = next(
          (p for p in parameters if p['parameter_id'] == parameter_id), None)
        if parameter_info:
          timeranges = parameter_info['timeranges']
          return timeranges
        else:
          return {
            "code": 404,
            "message": f"Parameter with ID '{parameter_id}' not found."
          }, 404
      else:
        return {
          "code": 404,
          "message": f"Area with ID '{area_id}' not found."
        }, 404
    else:
      suggestion = difflib.get_close_matches(provinceName.lower(),
                                             reference_texts,
                                             n=1)
      if suggestion:
        suggestion = suggestion[0]
      else:
        return {
          'code':
          404,
          'messageOwner':
          f"apaan dah ni '{provinceName}'.isi yang bener ya, sodara. jangan banyak typo!!"
        }

      return {
        "code":
        404,
        "message":
        f"'Province with Name '{provinceName}' not found. Did you mean '{suggestion}'?"
      }, 404

  @staticmethod
  def selectTimerange(provinceName, area_id, parameter_id, timerange):
    data = DigitalForecast.read_extract_data(provinceName)
    reference_texts = DataValidation.get_reference_texts()

    if 'area' in data:
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

          else:
            return {
              "code": 404,
              "message": f"Parameter with Timerange '{timerange}' not found."
            }, 404

        else:
          return {
            "code": 404,
            "message": f"Parameter with ID '{parameter_id}' not found."
          }, 404

      else:
        return {
          "code": 404,
          "message": f"Area with ID '{area_id}' not found."
        }, 404

    else:
      suggestion = difflib.get_close_matches(provinceName.lower(),
                                             reference_texts,
                                             n=1)
      if suggestion:
        suggestion = suggestion[0]
      else:
        return {
          'code':
          404,
          'messageOwner':
          f"apaan dah ni '{provinceName}'.isi yang bener ya, sodara. jangan banyak typo!!"
        }

      return {
        "code":
        404,
        "message":
        f"Province with Name '{provinceName}' not found. Did you mean '{suggestion}'?"
      }, 404


# ======================
