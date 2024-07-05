import json, os

OPTION_ROOT = 'path to A??? folders'
OPTION_ROOT2 = 'path to H??? folders'
PROBER_USERNAME = PROBER_PASSWORD = 'prober login user'
AQUA_HOST = 'localhost'
AQUA_INNER_ID = 'read from export json link'
BASE_DIR = os.path.dirname(__file__)
CACHE_DIR = os.path.abspath(os.path.join(BASE_DIR, '../cache'))

with open(os.path.join(BASE_DIR, 'CONFIG.JSON'), 'r', encoding='utf-8') as f:
    CFG = json.load(f)
    locals().update(CFG)

__all__ = [
    "OPTION_ROOT",
    "OPTION_ROOT2",
    "PROBER_USERNAME",
    "PROBER_PASSWORD",
    "AQUA_HOST",
    "AQUA_INNER_ID",
    "BASE_DIR",
    "CACHE_DIR",
]
