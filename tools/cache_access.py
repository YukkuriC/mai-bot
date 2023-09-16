import sys

sys.path.append(__file__ + '/../..')

from cache import CacheEntry

sys.path.pop()
del sys


def ensure_cache(name, import_if_missing=None):
    data = CacheEntry.load(name, True)
    if (not data) and import_if_missing:
        __import__(import_if_missing)
        data = CacheEntry.load(name, True)
    return data
