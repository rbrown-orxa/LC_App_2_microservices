import json
import werkzeug

import library

class DummyRequest():
	pass


valid_json = """
        {
<<<<<<< HEAD
            "lat": 18.51,
            "lon": 73.85,
            "import_cost_kwh": 0.14,
            "export_price_kwh": 0.04,
            "pv_cost_kwp": 1000,
            "pv_life_yrs": 20,
            "battery_life_cycles": 5000,
            "battery_cost_kwh": 1000,
=======
            "lat": 1.0,
            "lon": 1.0,
            "import_cost_kwh": 1.0,
            "export_price_kwh": 1.0,
            "pv_cost_kwp": 1.0,
            "pv_life_yrs": 1,
            "battery_life_cycles": 1,
            "battery_cost_kwh": 1.0,
>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace
            "load_profile_csv_optional": "",
            "building_data": [
                {
                    "name": "building 1",
<<<<<<< HEAD
                    "building_type": "domestic",
                    "roof_size_m2": 250,
                    "azimuth_deg": 180,
                    "pitch_deg": 30,
                    "num_ev_chargers": 10,
                    "pv_size_kwp_optional": 3.0,
                    "load_profile_csv_optional": "../examples/tests/Factory_Heavy_loads_15min.csv",
                    "annual_kwh_consumption_optional": 0.0
=======
                    "building_type": "residential",
                    "roof_size_m2": 1.0,
                    "azimuth_deg": 1,
                    "pitch_deg": 1,
                    "num_ev_chargers": 1,
                    "pv_size_kwp_optional": 1.0,
                    "load_profile_csv_optional": "../examples/tests/Factory_Heavy_loads_15min.csv",
                    "annual_kwh_consumption_optional": 1.0
>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace
                },
                {
                    "name": "building 2",
                    "building_type": "commercial",
<<<<<<< HEAD
                    "roof_size_m2": 250,
                    "azimuth_deg": 150,
                    "pitch_deg": 15,
                    "num_ev_chargers": 15,
                    "pv_size_kwp_optional": 5.0,
                    "load_profile_csv_optional": "",
                    "annual_kwh_consumption_optional": 6000.0
=======
                    "roof_size_m2": 1.0,
                    "azimuth_deg": 1,
                    "pitch_deg": 1,
                    "num_ev_chargers": 1,
                    "pv_size_kwp_optional": 1.0,
                    "load_profile_csv_optional": "",
                    "annual_kwh_consumption_optional": 1.0
>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace
                }
            ]
        }
"""

<<<<<<< HEAD
request = DummyRequest()
request.json = json.loads(valid_json)

if __name__ == '__main__':
   rv = library._optimise(request)
   print(rv)
   
   ffields = ['lon', 'lat', 'cost_per_kWp', 'import_cost_kwh', 
               'export_price_kwh','pv_cost_kwp', 'pv_life_yrs', 
               'battery_life_cycles', 'battery_cost_kwh',
                    'load_profile_csv_optional']
   
   print({field : request.json.get(field, None) for field in ffields})
   
   vfields=['name','building_type','roof_size_m2', 'azimuth_deg','pitch_deg',
            'num_ev_chargers','pv_size_kwp_optional','load_profile_csv_optional',
            'annual_kwh_consumption_optional']
   
   
   building_data = request.json.get('building_data')
   size = len(building_data)
   
   super_dict = {}
   for d in building_data:
    for k, v in d.items():
        super_dict.setdefault(k, []).append(v)
        
   print(super_dict)
   
  
   
   	# pass
   	# # print(valid_json)
   	# # print(json.loads(valid_json))
=======
dummy_request = DummyRequest()
dummy_request.json = json.loads(valid_json)



if __name__ == '__main__':
	rv = library._optimise(dummy_request)
	print(rv)


	# pass
	# # print(valid_json)
	# # print(json.loads(valid_json))




>>>>>>> 3a66c48bf832a3da065cffda53de1966c82deace
