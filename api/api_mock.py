import json
import werkzeug

import library

class DummyRequest():
	pass


valid_json = """
        {
            "lat": 1.0,
            "lon": 1.0,
            "import_cost_kwh": 1.0,
            "export_price_kwh": 1.0,
            "pv_cost_kwp": 1.0,
            "pv_life_yrs": 1,
            "battery_life_cycles": 1,
            "battery_cost_kwh": 1.0,
            "load_profile_csv_optional": "",
            "building_data": [
                {
                    "name": "building 1",
                    "building_type": "residential",
                    "roof_size_m2": 1.0,
                    "azimuth_deg": 1,
                    "pitch_deg": 1,
                    "num_ev_chargers": 1,
                    "pv_size_kwp_optional": 1.0,
                    "load_profile_csv_optional": "../examples/tests/Factory_Heavy_loads_15min.csv",
                    "annual_kwh_consumption_optional": 1.0
                },
                {
                    "name": "building 2",
                    "building_type": "commercial",
                    "roof_size_m2": 1.0,
                    "azimuth_deg": 1,
                    "pitch_deg": 1,
                    "num_ev_chargers": 1,
                    "pv_size_kwp_optional": 1.0,
                    "load_profile_csv_optional": "",
                    "annual_kwh_consumption_optional": 1.0
                }
            ]
        }
"""

dummy_request = DummyRequest()
dummy_request.json = json.loads(valid_json)



if __name__ == '__main__':
	rv = library._optimise(dummy_request)
	print(rv)


	# pass
	# # print(valid_json)
	# # print(json.loads(valid_json))




