from cache_access import ensure_cache
from cfg_reader import OPTION_ROOT, OPTION_ROOT2
import glob, os, shutil


def get_path(from_static):
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), '../src/static', from_static))


TARGET_DIR = get_path('cover_aqua_tmp')
TARGET_DIR_2 = get_path('cover_missing_tmp')

for d in [TARGET_DIR, TARGET_DIR_2]:
    if not os.path.isdir(d):
        os.makedirs(d, exist_ok=1)

crossMap = ensure_cache('crossMap', 'gen_music_crossmap')
missing_ids = set(i % 10000 for i in crossMap['aOnly'] if i < 20000)
# TODO 宴谱以后再说

# 有查分器数据但无封面
COVER_DIR = get_path('mai/cover')
proberData = ensure_cache('proberMusicData', 'gen_prober_music_data')
exist_covers = set(int(os.path.splitext(n)[0]) for n in os.listdir(COVER_DIR))
needed_covers = set(x for x in (int(m['id']) for m in proberData) if x < 20000)
needed_covers -= exist_covers

all_covers = glob.glob(
    fr'{OPTION_ROOT}/*/AssetBundleImages/jacket/ui_jacket_*.ab')
all_covers.extend(
    glob.glob(fr'{OPTION_ROOT2}/*/AssetBundleImages/jacket/ui_jacket_*.ab'))
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

for i in needed_covers:
    frm = cover_map.get(i % 10000)
    if not frm:
        continue
    too = os.path.join(f'{TARGET_DIR_2}/{i}.ab')
    shutil.copy2(frm, too)

# TODO 然后这边就寄了，ab跟内部资源名字不统一玩毛