import json

import library

class DummyRequest():
	pass


valid_json = """
        {
            "sub":"abc-xyz-234",
            "oid":"123-gty-pqr",
            "lat": 18.51,
            "lon": 73.85,
            "country": "India",
            "currency":"INR",
            "import_cost_kwh": 0.08,
            "export_price_kwh": 0.0,
            "pv_cost_kwp": 1000,
            "pv_life_yrs": 20,
            "battery_life_cycles": 6000,
            "battery_cost_kwh": 300,
            "load_profile_csv_optional": "",
            "building_data": [
                {
                    "name": "building 1",
                    "building_type": "domestic",
                    "roof_size_m2": 250,
                    "azimuth_deg": 180,
                    "pitch_deg": 30,
                    "num_ev_chargers": 3,
                    "pv_size_kwp_optional": 3.0,
                    "load_profile_csv_optional": "",
                    "annual_kwh_consumption_optional": 8000
                },
                {
                    "name": "building 2",
                    "building_type": "commercial",
                    "roof_size_m2": 250,
                    "azimuth_deg": 150,
                    "pitch_deg": 15,
                    "num_ev_chargers": 5,
                    "pv_size_kwp_optional": 5.0,
                    "load_profile_csv_optional": "",
                    "annual_kwh_consumption_optional": 12000
                }
            ]
        }
"""

accesstoken = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsImtpZCI6Ilg1ZVhrNHh5b2pORnVtMWtsMll0djhkbE5QNC1jNTdkTzZRR1RWQndhTmsifQ.eyJleHAiOjE1OTk3NDg5NDYsIm5iZiI6MTU5OTc0NTM0NiwidmVyIjoiMS4wIiwiaXNzIjoiaHR0cHM6Ly9kZXJhcHAuYjJjbG9naW4uY29tLzZiMGM5ZmE2LTgwZjEtNDcwNi04N2ZlLTM5YjViODQ2YWI2Ny92Mi4wLyIsInN1YiI6ImY1N2UwYmVjLWU4NTEtNGIyMy04MGI2LTM4YmUxNzA3Y2ZlZSIsImF1ZCI6ImY1MzYyOGQ1LWExY2ItNDNlMC1hMjk1LTcwOTczZTkyOTlmYyIsIm5vbmNlIjoiZGVmYXVsdE5vbmNlIiwiaWF0IjoxNTk5NzQ1MzQ2LCJhdXRoX3RpbWUiOjE1OTk3NDUzNDYsImNvdW50cnkiOiJJbmRpYSIsIm5hbWUiOiJTYW5qZWV2IEt1bWFyIiwiam9iVGl0bGUiOiJEYXRhIFNjaWVudGlzdCIsImVtYWlscyI6WyJzYW5qZWV2a3VtYXIuc3IzMDBAZ21haWwuY29tIl0sInRmcCI6IkIyQ18xX3NpZ25fdXBfc2lnbl9pbiJ9.VGmCibWL8jmJ91z1fgNBRhrI4mBIn-239AkjJdLXRAcOV8OEwE8AblbpAYPhOZ3nvsBx6uhC345zfwOhaNUqq--EkGDJJddv4y5FVPYZ8fvY3ryAnThcjO-068JBFy0QmoA0awpe6ZeDu82IsYGeevAaYc2yleDI8N2yy5gDS381M90tYH9NRIKHQdPwBpkZ1tAskrGdU5X7LvV7yIURq050r0a7hschz8lvPM6uW815iOfS3yYq9dg34gZ3XDrO7OozBnq-MQuYxVvPFwS_FUUP7CdQWjP5rC1YTJ-w2mkceSqd05xZ4zbIcUnNGCpGiqWE8RTBBh3wbAwxgGkQjg"

        
request = DummyRequest()
request.json = json.loads(valid_json)
request.headers = {"Authorization" : "Bearer " + accesstoken}




