End-to-end test

1. Install Postman - https://www.postman.com/downloads/
2. Postman > Import > File > Upload Files > solarpv_battery/test/LCAPP2.postman_collection.json
3. LCAPP2 > optimise > Auth > Get New Access Token > Request Token > (sign in with test credentials) > Use Token
4. $ cd solarpv_battery/api
5. $ python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
6. Edit config file to suit test being performed > $ nano config.py
7. $ python3 application.py
8. Postman > Send
9. Check results in Postman response
10. $ <CTRL> - C
11. $ deactivate