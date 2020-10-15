# API service for LC App Phase 2

This is a Flask app which optimally sizes solar PV and storage batteries for a complex of one or more buildings. API endpoints and data science model are contained within this service.


- Incoming requests to some endpoints can be optionally required to authenticate via a JSON Web Token (JWT) included in the HTTP header.
- Calls to some endpoints are logged in the LC App Phase 2 postgres DB, including authentication IDs required for rate limiting and billing
- Files uploaded through the API are stored with sanitised file names in the server's local filesystem


## To run a test DB locally on Ubuntu machine (not for production):
    
1. Install docker if not already installed

        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh
        sudo usermod -aG docker <your-user>
        reboot

1. Start a postgres instance against localhost

        docker run -d --name postgres -e POSTGRES_PASSWORD=password postgres


## To run inline tests of .py modules (N.B. not all modules have an inline test)

1. Create a virtual environment

        python3 -m venv venv

1. Activate virtual environment and install dependencies

        source ./venv/bin/activate
        pip install -r requirements.txt

1. Run the module, e.g. billing.py . Information on pass/fail states will be printed.

        python3 <module>.py

1. Stop the test if it does not exit after running

        <CTRL-C>


## To run API service locally

1. Run test DB locally if required (see instructions above) 

        docker run -d --name postgres -e POSTGRES_PASSWORD=password postgres

1. Edit config.py DB connection strings to point to local DB if required (comment production string and uncomment test string around lines 15-40)

        Use these for local testing:
        BILLING_DB_CONN_STR = "host=localhost "\
        ...

1. Create and activate virtual environment

        python3 -m venv venv
        source ./venv/bin/activate
        pip install -r requirements.txt

1. Run the application module. API HTTP server will run against localhost:5000

        python3 application.py 

1. Point browser to localhost:5000 for API documentation

1. Use postman collection to test API
- lcapp2.postman_collection.json



## To deploy in production

1. Ensure following four dependencies are running (if required by config choices):

- Billing service (Python3 Docker) - https://bitbucket.org/OrxaGridRepo/solarpv_battery/src/billing_db/billing/
- Subscription service (C# dotnet) - https://bitbucket.org/OrxaGridRepo/contosoampbasic/src/dev/
- Frontend (React.js) - https://bitbucket.org/OrxaGridRepo/solarpv-phase2/src/master/
- Database (postgres Azure) - lcapppostgreserver.postgres.database.azure.com

1. Push all source files, excluding /venv and /tmp directories to Azure flask runtime

1. Use postman collection to test API
- lcapp2.postman_collection.json
        


