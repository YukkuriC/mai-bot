from .aqua import queryMusic, queryNickname
from .maimai_rating_base import ChartInfo, BestList
from cache import CacheEntry
from .maimai_best_50 import DrawBest
from .maimai_best_40 import DrawBest as DrawBest_B40


async def NULL_AWAIT(*a, **kw):
    pass


def GetCrossMap():
    if getattr(GetCrossMap, '_cache', None):
        return GetCrossMap._cache
    raw = CacheEntry.load('crossMap', True)
    raw['pOnly'] = set(raw['pOnly'])
    raw['aOnly'] = set(raw['aOnly'])
    GetCrossMap._cache = raw
    return raw


def GetAquaData():
    if getattr(GetAquaData, '_cache', None):
        return GetAquaData._cache
    raw = CacheEntry.load('aquaMusicData', True)
    for i, grp in enumerate(raw['version']):
        raw['version'][i] = set(grp)

    titleMap = {}
    for key in 'SD', 'DX':
        for t, i in raw[key].items():
            titleMap[i] = t
    raw['id2title'] = titleMap
    GetAquaData._cache = raw
    return raw


async def GetAquaLists(host,
                       userId,
                       old=35,
                       new=15,
                       new_id=-1,
                       sender=NULL_AWAIT,
                       flags=[],
                       predicates=[]):
    '''
        supported flags: noVersion
    '''

    # check metadata
    if not (crossMap := GetCrossMap()):
        await sender("missing crossmap, run tools/gen_music_crossmap.py first")
        return
    if not (aquaData := GetAquaData()):
        await sender("missing aqua data, run tools/gen_aqua_music_map.py first"
                     )
        return

    # fetch raw data
    data, status = await queryMusic(host, userId)
    if status != 200:
        await sender(f"query userId={userId} in {host} error: {status}")
        return

    # map all to prober format
    lstOld, lstNew = [], []
    newMap = aquaData['version'][new_id]
    for unit in data:
        aquaId = unit['musicId']
        aquaId_cover = aquaId % 10000
        if aquaId in crossMap['aOnly']:
            proberId = -aquaId_cover
        else:
            proberId = crossMap['a2p'].get(aquaId, aquaId)

        lvl_idx = unit['level']
        try:
            ds = aquaData['diff'][aquaId][lvl_idx]
        except:
            await sender(f"no diff info for music#{aquaId} level#{lvl_idx}")
            continue

        chart = ChartInfo(
            idNum=proberId,
            diff=lvl_idx,
            tp='DX' if aquaId >= 10000 else 'SD',
            achievement=unit['achievement'] * 1e-4,
            comboId=unit['comboStatus'],
            scoreId=unit['scoreRank'],
            title=aquaData['id2title'].get(aquaId, f'Title#{aquaId}'),
            ds=ds,
            lv=str(int(ds)) + ('+' if ds - int(ds) >= 0.7 else ''),
        )

        # filter & flags
        for p in predicates:
            if not p(chart):
                continue

        if 'noversion' in flags or aquaId in newMap:
            lstNew.append(chart)
        else:
            lstOld.append(chart)

    if 'noversion' in flags:
        lstNew.sort(reverse=1)
        blOld, blNew = BestList(old), BestList(new)
        blOld.data = lstNew[:old]
        blNew.data = lstNew[old:old + new]
    else:
        blOld, blNew = BestList(old), BestList(new)
        blOld.data = sorted(lstOld, reverse=1)[:old]
        blNew.data = sorted(lstNew, reverse=1)[:new]

    return blOld, blNew


async def GetUserNickname(host, userId):
    try:
        raw = await queryNickname(host, userId)
        print(raw)
        return raw['userName']
    except:
        return str(userId)


def _splitArgs(args):
    args = [x.lower() for x in args]
    # TODO split predicates
    return args, []


async def GenBest(host, userId, is_b40, sender=NULL_AWAIT, extra_args=[]):
    flags, predicates = _splitArgs(extra_args)
    kwargs, drawing = {}, DrawBest
    if is_b40:
        kwargs['old'] = 25
        drawing = DrawBest_B40
    data = await GetAquaLists(host,
                              userId,
                              sender=sender,
                              flags=flags,
                              predicates=predicates,
                              **kwargs)
    if not data:
        return data

    pic = drawing(*data, await GetUserNickname(host, userId)).getDir()
    return pic
