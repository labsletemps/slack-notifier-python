# -*- coding: utf-8 -*-

import feedparser
import requests
import pandas as pd
import re
import logging
import sys
import os.path
from define import config

# chemin vers le script
# (permet de lire/ecrire dans le repertoire du script quand on en fait un cronjob)
dir_path = os.path.dirname(os.path.abspath(__file__))

logging.basicConfig(format = '%(asctime)s %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    filename = os.path.join(dir_path, 'notifier.log'),
                    level=logging.INFO)

logging.info('Launch')

def getLastEntries(url, deltaMinutes):
    NewsFeed = feedparser.parse(url)

    df = pd.DataFrame(NewsFeed.entries)
    
    if not 'published' in df.columns:
        logging.error('Column “published” is missing')
        return False
        
    # Conversion en UTC pour calculer le Timedelta
    df['published-utc'] = pd.to_datetime(df['published'], utc=True)
    
    df['published'] = pd.to_datetime(df['published'])
    df['elapsed'] = pd.Timestamp.now(tz='UTC') - df['published-utc']

    # TODO: regler le probleme de timezone
    lastEntries = df[df['elapsed'] < pd.Timedelta(60+deltaMinutes, unit='m')].copy()

    logging.info('RSS: {} entries found, {} in the last {} minutes'.format(len(df), len(lastEntries), deltaMinutes))
    return lastEntries

def removePostedEntries(df_new):
    if os.path.isfile( os.path.join(dir_path, 'last_posted_articles.csv') ):
        df_old = pd.read_csv( os.path.join(dir_path, 'last_posted_articles.csv'), usecols=['link'])
        return df_new[ -df_new['link'].isin( df_old['link'].tolist() ) ]
    else:
        return df_new

def getSection(url, domain):
    if not isinstance(url, str):
        logging.warning('Entry without link')
        return 'n/a'
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
        logging.error (e)
    if response:
        return response.json()
    else:
        return False

def getIsPremium(JSONdata):
    lookup = JSONdata
    
    # TODO: optimize
    i = 0
    for level in config['premium-path']:
        try:
            lookup = lookup[level]
        except ValueError as e:
            logging.warning('Premium: broken JSON path')
            return False
    return lookup
    
def filterEntries(df_unfiltered, filters):
    filterList = []
    for filterKey, filterValue in filters.items():
        if filterKey in df_unfiltered.columns:
            filterList.append(df_unfiltered[filterKey] == filterValue)
        else:
            logging.error('Filter key not found in df columns')
    if len(filterList) == 2:
        return df_unfiltered[ filterList[0] | filterList[1] ]
    elif len(filterList) == 1:
        return df_unfiltered[filterList[0]]
    else:
        return df_unfiltered
        
def postEntries(df_entries):
    for i, row in df_entries.iterrows():
        
        # si http (comme souvent dans vieux RSS)
        legacy_id = row['id'].replace('http', 'https')
        
        published_str = ''
        try:
            published_str = row['published'].time().strftime('%H:%M')
        except:
            logging.warning('Could not strf published time')
            
        title = row['title']
        
        premium_str = '[payant]' if row['premium'] == 1 else ''
        
        data = {'text': '*{}* {} {}\n{} {}'.format(
            published_str,
            row['section'],
            premium_str,
            title,
            legacy_id
        )}
        
        try:
            response = requests.post(config['Slack-webhook'], json=data)
            response.raise_for_status()
        except requests.exceptions.RequestException as e: # on catch tout
            logging.error (e)
            return False
    return True

def registerPostedArticles(df_posted):
    df_posted.to_csv( os.path.join(dir_path, 'last_posted_articles.csv') )

# Articles publiés dans les 28 dernières minutes
df = getLastEntries(config['RSS-feed'], 28)

if df is False:
    logging.error('Could not retrieve entries')
    sys.exit()

if len(df) > 0:
    df = removePostedEntries(df)
    df['section'] = df['link'].apply(lambda x: getSection(x, 'tdg.ch'))
    df['articleId'] = df['id'].apply(getArticleId)
    df['premium'] = 0
    
    logging.info('Getting data about {} entries'.format(len(df)))
    for i, row in df[-df['articleId'].isnull()].iterrows():
        articleData = getJSON(row['articleId'])
        isPremium = getIsPremium(articleData)
        if isPremium:
            logging.info('Premium article found: {}'.format(row['title']))
            df.at[i, 'premium'] = 1
    
    filtered_df = filterEntries(df, {'section': 'geneve', 'premium': 'premium'})
    
    logging.info('Posting {} entries'.format(len(filtered_df)))
    
    postResult = postEntries(filtered_df)
    if postResult == True:
        registerPostedArticles(filtered_df)