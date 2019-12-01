import feedparser
import requests
import pandas as pd
import re
import logging
from os import getcwd
from define import config

def getLastEntries(url, deltaMinutes):
    return
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
