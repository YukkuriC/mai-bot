import os, json, shelve

HERE = os.path.dirname(__file__)


def tryUseIntKey(obj):
    if not isinstance(obj, dict):
        return obj
    num_key = all(k.lstrip('-').isdigit() for k in obj)
    if not num_key:
        return obj
    return {int(k): v for k, v in obj.items()}


class CacheEntry:
    _CACHED = {}

    @classmethod
    def load(cls, name, refresh=False):
        if name not in cls._CACHED or refresh:
            path = os.path.join(HERE, f'{name}.json')
            if not os.path.isfile(path):
                return None
            with open(path, 'r', encoding='utf-8') as f:
                cls._CACHED[name] = json.load(f, object_hook=tryUseIntKey)
        return cls._CACHED[name]

    @classmethod
    def dump(cls, name, obj):
        cls._CACHED[name] = obj
        path = os.path.join(HERE, f'{name}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, separators=',:', ensure_ascii=0)


class CacheShelve:

    @classmethod
    def _getShelve(cls, name):
        return shelve.open(os.path.join(HERE, name))

    @classmethod
    def get(cls, name, default=None, group='default'):
        with cls._getShelve(group) as s:
            return s.get(name, default)

    @classmethod
    def set(cls, name, value, group='default'):
        with cls._getShelve(group) as s:
            s[name] = value
