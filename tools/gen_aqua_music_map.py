import glob, os, json
from xml.dom.minidom import parse

os.sys.path.append(os.path.dirname(__file__))
from cfg_reader import OPTION_ROOT
from cache_access import CacheEntry

sdMap, dxMap, versionMap, versionNameMap = {}, {}, [], []


def parseStrIdNode(node):
    id = int(node.getElementsByTagName('id')[0].firstChild.data)
    str = node.getElementsByTagName('str')[0].firstChild.data
    return id, str


def readMusicFile(path):
    musicId = int(os.path.basename(os.path.dirname(path))[5:])
    isDx = musicId // 10000 > 0
    doc = parse(path).documentElement
    id2, title = parseStrIdNode(doc.getElementsByTagName('name')[0])
    assert musicId == id2

    vid, vname = parseStrIdNode(doc.getElementsByTagName('AddVersion')[0])
    if vid not in versionMap:
        while len(versionNameMap) < vid + 1:
            versionMap.append([])
            versionNameMap.append(None)
        versionNameMap[vid] = vname
    versionMap[vid].append(musicId)

    if musicId == 383:
        title = 'Link(CoF)'

    target = dxMap if isDx else sdMap
    if title in target:
        if target[title] != musicId:
            print(title, musicId, target[title])
    else:
        target[title] = musicId


for path in glob.glob(fr'{OPTION_ROOT}/*/Music/*/Music.xml'):
    readMusicFile(path)

CacheEntry.dump('aquaMusicData', {
    "SD": sdMap,
    "DX": dxMap,
    "version": versionMap,
    "versionName": versionNameMap
})
