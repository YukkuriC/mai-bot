import requests, sys

sys.path.append(__file__ + '/../..')
from cache import CacheEntry

obj = requests.get(
    'https://www.diving-fish.com/api/maimaidxprober/music_data').json()
CacheEntry.dump('proberMusicData', obj)
