import glob, os, json
from xml.dom.minidom import parse

os.sys.path.append(os.path.dirname(__file__))
from cfg_reader import OPTION_ROOT, BASE_DIR

sdMap, dxMap = {}, {}

for path in glob.glob(fr'{OPTION_ROOT}/*/Music/*/Music.xml'):
    musicId = int(os.path.basename(os.path.dirname(path))[5:])
    isDx = musicId // 10000 > 0
    doc = parse(path).documentElement
    nameNode = doc.getElementsByTagName('name')[0]
    title = nameNode.getElementsByTagName('str')[0].firstChild.data
    # id2 = int(nameNode.getElementsByTagName('id')[0].firstChild.data)
    # assert musicId == id2

    target = dxMap if isDx else sdMap
    if title in target:
        if target[title] != musicId:
            print(title, musicId, target[title])
    else:
        target[title] = musicId

    with open(os.path.join(BASE_DIR, 'musicMap.json'), 'w',
              encoding='utf-8') as f:
        json.dump([sdMap, dxMap], f, indent=4, ensure_ascii=0)
