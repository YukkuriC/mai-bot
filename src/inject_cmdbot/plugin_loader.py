import os, traceback

_LOADED_PLUGINS = {}


def load_plugins(path: str):
    for file in os.listdir(path):
        if not file.endswith('.py'):
            continue
        if file in _LOADED_PLUGINS:
            continue
        try:
            mod = __import__(f'src.plugins.{os.path.splitext(file)[0]}')
            _LOADED_PLUGINS[file] = mod
        except:
            print(f'error when loading {file}:')
            traceback.print_exc()
        else:
            print(f'loaded plugin: {file}')
