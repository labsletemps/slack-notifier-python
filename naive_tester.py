from notifier import getLastEntries, getSection, getArticleId, getJSON
import pandas as pd
import os.path

def test_getLastEntries():
    # getLastEntries() doit retourner un DataFrame
    test_df = getLastEntries('https://paulronga.ch/feed/', 60*24*365*2)
    assert type(test_df) == pd.core.frame.DataFrame
    assert len(test_df) > 0
    
def test_logFile():
    # le fichier notifier.log doit etre cree
    assert os.path.isfile('notifier.log')
    
def test_getSection():
    # doit retourner une rubrique / un tag ou n/a
    assert getSection('https://www.domain.biz/asdf/rognogno', 'domain.biz') == 'asdf'
    assert getSection('https://www.external.net/boom', 'domain.biz') == 'n/a'
    
def test_getArticleId():
    # doit retourner une serie de chiffres (en str)
    assert getArticleId('https://www.domain.biz/asdf/2154321321654') == '2154321321654'
    assert getArticleId('https://www.domain.biz/asdf/rheuu') == False
    
def test_getJSON():
    # doit retourner du JSON ou "FAUX"
    assert getJSON('asdf') == False
    #assert type(getJSON('asdf')) == 