import os, glob

BASE_DIR = os.path.dirname(__file__)
for file in glob.glob(f'{BASE_DIR}/**/*.py', recursive=True):
    file = os.path.relpath(file, BASE_DIR)[:-3]
    modname = file.replace(os.path.sep, '.')
    if modname.endswith('__init__'):
        modname = modname[:-9]
    if not modname:
        continue
    modname = __name__ + '.' + modname
    __import__(modname)

__all__ = []
