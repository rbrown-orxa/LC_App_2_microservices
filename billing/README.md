# Billing service for LC App Phase 2

This is a docker container service which calculates Azure SaaS bills every n seconds (3600 typical) based on the number of unbilled queries over the past n hours (24 typical) and posts the bills to SaaS API.

- Queries, bills and subscription references are handled in the LC App Phase 2 postgres DB.
- Subscription status is handled by SaaS API


## To install Docker locally on Ubuntu machine (not for production):
    
1. Get the convenience script:

        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh

2. Add permissions (replace <your-user> with your user name)

        sudo usermod -aG docker <your-user>
        reboot


## To run inline test locally:

1. Start a postgres instance against localhost

        docker run -d --name postgres -e POSTGRES_PASSWORD=password postgres

2. Create a virtual environment

        python3 -m venv venv

3. Activate virtual environment and install dependencies

        source ./venv/bin/activate
        pip install -r requirements.txt

4. Run the script. A billing job should run against dummy data

        python3 billing_service.py


## To run production version of billing service locally:

1. Build the image

        docker build -t billing_service:v1 .

2. Run the container in background

        docker run -d --name billing billing_service:v1

3. Check the logs

        docker logs -f billing 

4. Check if container is up

        docker container ls -a

5. Stop billing service

        docker stop billing
        
6. Remove billing service

        docker rm billing

