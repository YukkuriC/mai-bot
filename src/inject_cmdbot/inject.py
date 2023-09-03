import sys

FAKE_MODULE_PATH = 'inject_cmdbot.fake_module.'


def inject():
    parent = sys.modules[__name__[:-7]]
    parent.__name__ = 'nonebot'
    sys.modules['nonebot'] = parent

    filter_keys = [*sys.modules.keys()]
    for k in filter_keys:
        if FAKE_MODULE_PATH in k:
            i = k.index(FAKE_MODULE_PATH)
            subkey = 'nonebot.' + k[i + len(FAKE_MODULE_PATH):]
            sys.modules[subkey] = sys.modules[k]
