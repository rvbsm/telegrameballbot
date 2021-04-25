import os

API_TOKEN = "1708019201:AAEMfsUPDVNNbgsRP4rA-7jgVKOMk0c65xQ"
APP_NAME = "telegrameballbot"
DATABASE = {
	'dbhost': 'rvbsm-postgre.ct4bvuutiewe.eu-west-1.rds.amazonaws.com',
	'dbport': 5432,
	'dbname': 'fivelyceumbot_postgre',
	'dbuser': 'master',
	'dbpass': '22rusbesm22'
}
WEBHOOK_HOST = f'https://{APP_NAME}.herokuapp.com/' # Webhook hosting
WEBHOOK_PATH = f'/webhook/{API_TOKEN}' # Webhook path for bot (better is using API_TOKEN)
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
WEBAPP_PORT = os.getenv("PORT")
