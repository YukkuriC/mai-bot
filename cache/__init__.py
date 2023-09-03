import os, json

HERE = os.path.dirname(__file__)


class CacheEntry:
    _CACHED = {}

    @classmethod
    def load(cls, name, refresh=False):
        if name not in cls._CACHED or refresh:
            path = os.path.join(HERE, f'{name}.json')
            if not os.path.isfile(path):
                return None
            with open(path, 'r', encoding='utf-8') as f:
                cls._CACHED[name] = json.load(f)
        return cls._CACHED[name]

    @classmethod
    def dump(cls, name, obj):
        cls._CACHED[name] = obj
        path = os.path.join(HERE, f'{name}.json')
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, separators=',:', ensure_ascii=0)
