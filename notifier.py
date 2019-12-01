import feedparser
import requests
import pandas as pd
import re
import logging
import sys
from define import config

sys.path.append(".")

logging.basicConfig(format = '%(asctime)s %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    filename = 'notifier.log',
                    level=logging.INFO)

logging.info('Launch')

def getLastEntries(url, deltaMinutes):
    NewsFeed = feedparser.parse(url)
    logging.info('RSS: ' + str(len(NewsFeed.entries)) + 'entries found.')

    df = pd.DataFrame(NewsFeed.entries)
    
    # Conversion en UTC pour calculer le Timedelta
    df['published-utc'] = pd.to_datetime(df['published'], utc=True)
    df['elapsed'] = pd.Timestamp.now(tz='UTC') - df['published-utc']

    # TODO: regler le probleme de timezone
    lastEntries = df[df['elapsed'] < pd.Timedelta(60+deltaMinutes, unit='m')].copy()

    print(len(lastEntries), 'published during the last {} min.'.format(deltaMinutes))
    return lastEntries

def getSection(url, domain):
    match = re.match(r'.*{domain}\/(.*?)\/.*'.format(domain=domain), url)
    if match:
        return match.group(1)
    else:
        logging.warning('No section found in url'+ url)
        return 'n/a'
        
def getArticleId(shortLink):
    untrustedId = shortLink.split('/')[-1]
    if re.match(r"\d*$", untrustedId):
        return untrustedId
    else:
        return False
        
def getJSON(article_id):
    response = False
    try:
        response = requests.get(config['API-endpoint'] + str(article_id), headers=config['request-headers'])
        response.raise_for_status()
    except requests.exceptions.RequestException as e: # on catch tout
        print (e)
    if response:
        return response.json()
    else:
        return False
        
getJSON('20398201938')