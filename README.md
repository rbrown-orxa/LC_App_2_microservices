	cd api
	python3 -m venv venv
	source venv/bin/activate
	pip install -r requirements.txt
	python3 application.py

	docker run --rm -d --name orxa_postgres -p 5432:5432 -e POSTGRES_PASSWORD=password postgres

Point broswer at localhost:5000 for API documentation


# LC App Phase 2

This repo contains the API and billing services for LC App Phase 2, which optimally sizes solar PV and battery storage for a complex containing one or more buildings.

Instructions for testing and deploying these services are given in readme files at /api and /billing respectively.

## Dependencies

LC App Phase 2 consists of five services:

	- API service (Python3 Flask) - https://bitbucket.org/OrxaGridRepo/solarpv_battery/src/master/api/
    - Billing service (Python3 Docker) - https://bitbucket.org/OrxaGridRepo/solarpv_battery/src/master/billing/
    - Subscription service (C# dotnet) - https://bitbucket.org/OrxaGridRepo/contosoampbasic/src/dev/
    - Frontend (React.js) - https://bitbucket.org/OrxaGridRepo/solarpv-phase2/src/master/
    - Database (postgres Azure) - lcapppostgreserver.postgres.database.azure.com


