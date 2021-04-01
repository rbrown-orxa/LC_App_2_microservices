
<!-- ### Start redis
	docker run -d -p 6379:6379 redis -->

### Start rabbitmq
	docker run -d -p 5672:5672 --name rabbit rabbitmq

### Start mongodb
	docker run -d -p 27017:27017 --name mongo mongo

### Start celery workers
	celery -A tasks worker --loglevel=INFO

