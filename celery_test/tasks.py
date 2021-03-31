from celery import Celery
from time import sleep


# celery = Celery(
# 	'tasks',
# 	broker='amqp://',
# 	backend='redis://'
# 	)

BROKER_URL = 'amqp://'

celery = Celery('tasks', broker=BROKER_URL)
celery.config_from_object('celeryconfig')


@celery.task
def add(x, y):
	sleep(10)
	# raise NotImplementedError
	# raise ValueError('error')
	# return x
	return {'value': x + y}
