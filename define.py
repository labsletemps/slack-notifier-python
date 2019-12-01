from dotenv import load_dotenv
import os
load_dotenv()

config = {
    'RSS-feed': os.getenv('RSS-FEED'),
    'API-endpoint': os.getenv('API-ENDPOINT'),
    'Slack-webhook': os.getenv('SLACK-WEBHOOK'),
}