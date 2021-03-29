
### Start redis
	docker run -d -p 6379:6379 redis

### Start rabbitmq
	docker run -d -p 5672:5672 rabbitmq


### Start celery workers
	celery -A tasks worker --loglevel=INFO