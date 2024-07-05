import glob, os, json
from xml.dom.minidom import parse

from cfg_reader import OPTION_ROOT, OPTION_ROOT2
from cache_access import CacheEntry

sdMap, dxMap, versionMap, versionNameMap = {}, {}, [], []
diffMap = {}


def parseStrIdNode(node):
    id = int(node.getElementsByTagName('id')[0].firstChild.data)
    str = node.getElementsByTagName('str')[0].firstChild.data
    return id, str


def readVersionFile(path):
    doc = parse(path).documentElement
    id, name = parseStrIdNode(doc.getElementsByTagName('name')[0])
    while len(versionMap) <= id:
        versionMap.append([])
        versionNameMap.append(None)
    versionNameMap[id] = name


def readMusicFile(path):
    musicId = int(os.path.basename(os.path.dirname(path))[5:])
    isDx = musicId // 10000 > 0
    doc = parse(path).documentElement
    id2, title = parseStrIdNode(doc.getElementsByTagName('name')[0])
    assert musicId == id2

    vid, vname = parseStrIdNode(doc.getElementsByTagName('AddVersion')[0])
    try:
        pool = versionMap[vid]
    except:
        pool = versionMap[-1]
    pool.append(musicId)

    if musicId == 383:
        title = 'Link(CoF)'

    target = dxMap if isDx else sdMap
    if title in target:
        if target[title] != musicId:
            print(title, musicId, target[title])
    else:
        target[title] = musicId

    diffList = [0] * 5
    diffMap[musicId] = diffList
    notesData = doc.getElementsByTagName('Notes')
    for i in range(min(5, len(notesData))):
        level = int(
            notesData[i].getElementsByTagName('level')[0].firstChild.data)
        levelSub = int(notesData[i].getElementsByTagName('levelDecimal')
                       [0].firstChild.data)
        diffList[i] = level + levelSub / 10


for option_root in [OPTION_ROOT, OPTION_ROOT2]:
    for path in glob.glob(fr'{option_root}/*/musicVersion/*/MusicVersion.xml'):
        readVersionFile(path)

    for path in glob.glob(fr'{option_root}/*/Music/*/Music.xml'):
        readMusicFile(path)

CacheEntry.dump(
    'aquaMusicData', {
        "SD": sdMap,
        "DX": dxMap,
        "version": versionMap,
        "versionName": versionNameMap,
        'diff': diffMap
    })
