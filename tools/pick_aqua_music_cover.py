from cache_access import ensure_cache
from cfg_reader import OPTION_ROOT
import glob, os, shutil

TARGET_DIR = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        '../src/static/cover_aqua_tmp',
    ))

if not os.path.isdir(TARGET_DIR):
    os.makedirs(TARGET_DIR, exist_ok=1)

crossMap = ensure_cache('crossMap', 'gen_music_crossmap')
missing_ids = set(i % 10000 for i in crossMap['aOnly'])

cover_pattern = fr'{OPTION_ROOT}/*/AssetBundleImages/jacket/ui_jacket_*.ab'
all_covers = glob.glob(cover_pattern)
cover_map = {}
for path in all_covers:
    cid = os.path.splitext(path)[0].rsplit('_', 1)[-1]
    cover_map[int(cid)] = path

for i in missing_ids:
    frm = cover_map.get(i)
    if not frm:
        continue
    too = os.path.join(f'{TARGET_DIR}/{i}.ab')
    shutil.copy2(frm, too)

# 后续转手动，输出至static/mai/cover_aqua