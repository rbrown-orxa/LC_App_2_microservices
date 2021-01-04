
# Add a test AAD subscription for an app which is in preview mode

(instructions modified from https://github.com/Ercenk/ContosoAMPBasic)

0. Request Sanjeev to give your OrxaGrid account the correct permissions
1. Log in to Azure Portal with an OrxaGrid account - https://portal.azure.com
2. Create A Resource > Search The Marketplace > 'low carbon app'
3. 'Low Carbon App V2 (preview)' > Basic Plan > Set up + subscribe
4. Subscription: Microsoft Azure Sponsorship, Name: Test > Review + subscribe
5. Add contact details > Subscribe > Configure account now > Sign in again > Submit



# End-to-end tests

## With AAD account and valid subscription:

**IMPORTANT**
*Ensure Postman collection variables are not masked by any environment variables.*
I.e. Set *'Environment'* to *'No Environment'* in top right corner

1. Install Postman - https://www.postman.com/downloads/
2. Postman > Import > File > Upload Files > solarpv_battery/test/LCAPP2_AAD.postman_collection.json
3. Follow 'Add a test AAD subscription for an app which is in preview mode' instructions
4. LCAPP2 > 'optimise with AAD and sub' > Auth > Get New Access Token > Request Token > (sign in with your credentials) > Token Name: 'AAD sub' > Use Token
	Grant type: Implicit
	Callback URL: {{callback_url}}
	Auth url: {{auth_url}}
	Client ID: {{client_id}}
	scope: {{scope}}
	state: {{state}}
5. $ cd solarpv_battery/api
6. $ python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
7. Edit config file to suit test being performed > $ nano config.py
8. $ python3 application.py
9. Postman > Send, expect "error": "402 User not subscribed"
10. $ <CTRL> - C
11. $ deactivate



## With B2C account (no subscription):

**IMPORTANT**
*Ensure Postman collection variables are not masked by any environment variables.*
I.e. Set *'Environment'* to *'No Environment'* in top right corner

1. Install Postman - https://www.postman.com/downloads/
2. Postman > Import > File > Upload Files > solarpv_battery/test/LCAPP_B2C.postman_collection.json
3. LCAPP2 > 'optimise with B2C' > Auth > Get New Access Token > Request Token > (sign in with test credentials) > Token Name: 'B2C' > Use Token > Gmail
	Grant type: Implicit
	Callback URL: {{callback_url}}
	Auth url: {{auth_url}}
	Client ID: {{client_id}}
	scope: {{scope}}
	state: {{state}}
	User: orxagridlcapp2test
	Pass: 5gc8TMnSjOv3uvcOgs84
4. $ cd solarpv_battery/api
5. $ python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
6. Edit config file to suit test being performed > $ nano config.py
7. $ python3 application.py
8. Postman > Send
9. Check results in Postman response
10. $ <CTRL> - C
11. $ deactivate


## With AAD account and no valid subscription:

**IMPORTANT**
*Ensure Postman collection variables are not masked by any environment variables.*
I.e. Set *'Environment'* to *'No Environment'* in top right corner

1. Install Postman - https://www.postman.com/downloads/
2. Postman > Import > File > Upload Files > LCAPP_bad_accounts.postman_collection.json
3. LCAPP2 > 'optimise AAD no sub' > Auth > Get New Access Token > Request Token > (sign in with test credentials) > Token Name: 'AAD no sub' > Use Token
	Grant type: Implicit
	Callback URL: {{callback_url}}
	Auth url: {{auth_url}}
	Client ID: {{client_id}}
	scope: {{scope}}
	state: {{state}}
	User: dummy@orxagrid.com
	Pass: SANlcappv212#
4. $ cd solarpv_battery/api
5. $ python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
6. Edit config file to suit test being performed > $ nano config.py
7. $ python3 application.py
8. Postman > Send
9. Check results in Postman response
10. $ <CTRL> - C
11. $ deactivate



## With no account:

1. Install Postman - https://www.postman.com/downloads/
2. Postman > Import > File > Upload Files > LCAPP_bad_accounts.postman_collection.json
3. LCAPP2 > 'optimise no account'
4. $ cd solarpv_battery/api
5. $ python3 -m venv venv && source venv/bin/activate && pip install -r requirements.txt
6. Edit config file to suit test being performed > $ nano config.py
7. $ python3 application.py
8. Postman > Send
9. Check results in Postman response
10. $ <CTRL> - C
11. $ deactivate




### Actual Auth Parameters used in Postman collection variables:

#### AAD:
	Grant type: Implicit
	Callback URL: https://jwt.ms
	Auth url: https://login.microsoftonline.com/f0e8a3c1-f57f-446b-b105-37b6d1ee94cc/oauth2/v2.0/authorize
	Client ID: 454f560c-4e04-46dc-bb7d-a74f753f3952
	Scope: api://454f560c-4e04-46dc-bb7d-a74f753f3952/User.read
	State: 1234

#### B2C:
	Grant type: Implicit
	Callback URL: https://jwt.ms
	Auth url: https://derapp.b2clogin.com/derapp.onmicrosoft.com/oauth2/v2.0/authorize?p=B2C_1_sign_up_sign_in
	Client ID: b249bf9e-9569-4c14-b12a-46b2563b2090
	scope: https://derapp.onmicrosoft.com/apirjs/demo.read
	State: 1234


### Postman variables:
	callback_url
	auth_url
	client_id
	scope
	state

