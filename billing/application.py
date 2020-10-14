import logging
import configparser

import billing_service

config = configparser.ConfigParser()
if not config.read('config.ini'):
    config.read(os.path.join(os.getcwd(), 'config.ini'))


loglevel = getattr(logging, config['DEBUG']['loglevel'].upper())
logging.basicConfig(level=loglevel)


if __name__ == '__main__':
	logging.info('Starting billing service')
	try:
		billing_service.run_service()
	except:
		logging.warning('Billing service exited unexpectedly')

