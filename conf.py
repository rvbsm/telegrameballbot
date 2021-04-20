import os

API_TOKEN = "1708019201:AAEMfsUPDVNNbgsRP4rA-7jgVKOMk0c65xQ"
APP_NAME = " rvbsm"
WEBHOOK_HOST = f'https://{APP_NAME}.pythonanywhere.com' # Webhook hosting
WEBHOOK_PATH = f'/webhook/{API_TOKEN}' # Webhook path for bot (better is using API_TOKEN)
WEBHOOK_URL = f'{WEBHOOK_HOST}{WEBHOOK_PATH}'
WEBAPP_HOST = '0.0.0.0'
try:
	WEBAPP_PORT = int(os.environ["PORT"])
except:
	WEBAPP_PORT = 5000
