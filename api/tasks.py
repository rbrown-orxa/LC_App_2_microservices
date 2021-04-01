from celery import Celery
from time import sleep



BROKER_URL = 'amqp://'

celery = Celery('tasks', broker=BROKER_URL)
celery.config_from_object('celeryconfig')


@celery.task
def add(x, y):
	sleep(10)
	return {'value': x + y}