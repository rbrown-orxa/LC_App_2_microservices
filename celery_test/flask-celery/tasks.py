from celery import Celery
from time import sleep


app = Celery(
	'tasks',
	broker='amqp://',
	backend='redis://'
	)


@app.task
def add(x, y):
	sleep(10)
	# raise NotImplementedError
	return x + y


