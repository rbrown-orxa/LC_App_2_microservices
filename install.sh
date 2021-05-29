# EDIT THE VALUES BELOW AS APPROPRIATE

DEPLOY_KEY=<your_deploy_key_provided_by_orxagrid>
SERVER_URL=http://<your_server_url_or_ip>
COMPANY_LOGO_URL=<url_for_your_company_logo>
COMPANY_WEBSITE_URL=<url_for_your_company_website>

# DO NOT EDIT BELOW THIS LINE

set -e

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
chmod +x /usr/local/bin/docker-compose


cat <<EOT > docker-compose-deploy.yml
version: '3'


services:

  frontend:
    container_name:
      frontend-prod
    image: rabwent11/lcapp2:frontend-v1
    environment:
      - "GENERIC_API_URL_FROM_ENV=$SERVER_URL:5000/"
      - "COMPANY_LOGO_URL=$COMPANY_LOGO_URL"
      - "COMPANY_WEBSITE_URL=$COMPANY_WEBSITE_URL"
    restart: always
    ports:
      - '80:80'


  api:
    container_name:
      api-prod
    image: rabwent11/lcapp2:api-v1
    restart: always  
    ports:
      - '5000:5000'
    environment:
      - "PYTHONUNBUFFERED=1"
      - "BROKER_URL=amqp://rabbitmq:5672"
      - "CELERY_BACKEND=mongo"
      - "MINIO_CONN_STR=minio:9000"
      - "MINIO_USER=user"
      - "MINIO_PW=password"
      - "MINIO_RAW_BUCKET=raw-uploads"
      - "MINIO_CLEANED_BUCKET=cleaned-uploads"
      

  worker:
    container_name:
      worker-prod
    image: rabwent11/lcapp2:api-v1
    restart: always    
    environment:
      - "PYTHONUNBUFFERED=1"
      - "BROKER_URL=amqp://rabbitmq:5672"
      - "CELERY_BACKEND=mongo"
      - "MINIO_CONN_STR=minio:9000"
      - "MINIO_USER=user"
      - "MINIO_PW=password"
      - "MINIO_RAW_BUCKET=raw-uploads"
      - "MINIO_CLEANED_BUCKET=cleaned-uploads"
    command: celery -A tasks worker --loglevel=INFO


  minio:
    container_name:
      object-store-prod
    image: minio/minio:RELEASE.2021-05-27T22-06-31Z
    restart: always   
    volumes:
      - minio_vol_deploy:/data
    environment:
      - 'MINIO_ROOT_USER=user'
      - 'MINIO_ROOT_PASSWORD=password'
    command: server /data


  rabbitmq:
    container_name:
      task-queue-prod    
    image: rabbitmq:3.8.16
    restart: always  


  mongo:
    container_name:
      nosql-db-prod    
    image: mongo:4.4.6
    restart: always
    volumes:
      - mongo_vol_deploy:/data/db


volumes:
  minio_vol_deploy:
  mongo_vol_deploy:
EOT

docker login -u rabwent11 -p $DEPLOY_KEY

docker-compose -f docker-compose-deploy.yml pull

docker-compose -f docker-compose-deploy.yml up -d

echo "installation completed"

