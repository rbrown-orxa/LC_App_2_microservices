
# OrxaGrid B2B2C Low Carbon App 2

## Description

This application is a solar PV and battery system optimiser designed to be
deployed by system installers for integration with their company website.


## Architecture

 - Reverse Proxy routes requests to the relevent service (todo)
 - Web App serves HTML/CSS/JS content
 - REST API interchanges data between the Web App and all other backend services
 - Rate limiter prevents a single user over using the api (todo)
 - Task queue routes work between API and data factories
 - File processor is a data factory for cleaning uploaded files
 - Low Carbon Optimiser is a data factory for sizing battery and solar PV systems
 - Solar Hindcast provides solar generation data for a given location (todo)
 - Object Store persists uploaded and cleaned files
 - Document DB persists optimisation results
 - Relational DB stores app usage statistics
 - License Manager restricts operation of the optimiser to licensed installations (todo)
 - Whitelabel Config enables custom branding of the Web App
 - Whitelabel Templates enables custom branding of the optimisation reports (todo)
 - Push Notifications generates sales leads and sends to system installers (todo)
 - Dashboard displays business intelligence about how the app is being used (todo)

![Architecture Diagram](architecture.png)

## Build Environment
This application should be built using Linux Docker on a Mac, Linux or Windows
host with x64 architecture.

## Deploy Environment
This application has been tested on a Linux Ubuntu host with x64 architecture,
but should be deployable on any modern linux host with Docker installed.

## Development
- Install Docker (https://docs.docker.com/get-docker/)
- Insall Docker Compose (https://docs.docker.com/compose/install/)  

### Run the following commands to start the app in dev mode
	docker-compose pull
	docker-compose build .
	docker-compose up -d


### Check the services which came up
 	docker stats

### Check the logs
	docker-compose logs -f


## Testing


## Local Deployment


## Production Deployment (manual)


## Production Deployment (automatic)


	docker build -t rabwent11/lcapp2:api-v1 -f ./api/Dockerfile.prod ./api
	docker push rabwent11/lcapp2:api-v1

	docker build -t rabwent11/lcapp2:frontend-v1 -f ./frontend/Dockerfile.prod ./frontend
	docker push rabwent11/lcapp2:frontend-v1
