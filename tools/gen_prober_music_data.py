import requests, sys

from cache_access import CacheEntry

obj = requests.get(
    'https://www.diving-fish.com/api/maimaidxprober/music_data').json()
CacheEntry.dump('proberMusicData', obj)
