import json

import library

class DummyRequest():
	pass


valid_json = """
        {
            "lat": 18.51,
            "lon": 73.85,
            "import_cost_kwh": 0.14,
            "export_price_kwh": 0.0,
            "pv_cost_kwp": 1840,
            "pv_life_yrs": 20,
            "battery_life_cycles": 6000,
            "battery_cost_kwh": 407,
            "load_profile_csv_optional": "",
            "building_data": [
                {
                    "name": "building 1",
                    "building_type": "domestic",
                    "roof_size_m2": 250,
                    "azimuth_deg": 180,
                    "pitch_deg": 30,
                    "num_ev_chargers": 10,
                    "pv_size_kwp_optional": 3.0,
                    "load_profile_csv_optional": "tmpvsgz75u3",
                    "annual_kwh_consumption_optional": 0.0
                },
                {
                    "name": "building 2",
                    "building_type": "commercial",
                    "roof_size_m2": 250,
                    "azimuth_deg": 150,
                    "pitch_deg": 15,
                    "num_ev_chargers": 15,
                    "pv_size_kwp_optional": 5.0,
                    "load_profile_csv_optional": "",
                    "annual_kwh_consumption_optional": 6000.0
                }
            ]
        }
"""
        
request = DummyRequest()
request.json = json.loads(valid_json)

if __name__ == '__main__':
   rv = library._optimise(request)
   print(rv)
   




