from notifier import getLastEntries
import pandas as pd

def test_getLastEntries():
    # doit retourner un DataFrame
    test_df = getLastEntries('https://paulronga.ch/feed/', 60*24*365*2)
    assert type(test_df) == pd.core.frame.DataFrame
    assert len(test_df) > 0