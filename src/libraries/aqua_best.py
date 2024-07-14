from .aqua import queryMusic, queryNickname
from .maimai_rating_base import ChartInfo, BestList, computeRa
from cache import CacheEntry
from .maimai_best_50 import DrawBest
from .maimai_best_40 import DrawBest as DrawBest_B40
from .maimaidx_music import total_list as prober_list
import re


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
            if 'debug' in flags:
                await sender(f"no diff info for music#{aquaId} level#{lvl_idx}"
                             )
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
            lv=str(int(ds)) + ('+' if ds - int(ds) - 0.7 >= -1e-5 else ''),
        )

        # filter & flags
        pass_test = True
        for p in predicates:
            if not p(chart):
                pass_test = False
                continue
        if not pass_test:
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


if 'parse extra args':
    FOO_CHART = ChartInfo('666', 5, 'DX', 114.514, 3, 5, 'YJSP', 1919.810,
                          '15+')

    FIELD_ALIAS = [
        ['idNum', ['id']],
        ['achievement', ['result']],
        ['ra', ['rating']],
        ['comboId', ['comboid']],
        ['scoreId', ['scoreid']],
        ['title', ['name']],
        ['lv', ['level']],
    ]
    FIELD_ALIAS_MAP = {}
    for orig, aliases in FIELD_ALIAS:
        for a in aliases:
            FIELD_ALIAS_MAP[a] = orig

    PREDICATE_REGEX = re.compile(r'([\w\.+]+)([<>=!]+)([\w\.+]+)')

    LEVEL_TRANS = lambda lvStr: float(lvStr.replace('+', '.5'))

    def _genCmp(field, op, val: str):
        if field == 'lv':
            val = LEVEL_TRANS(val)
            return lambda c: eval(f'{LEVEL_TRANS(c.lv)}{op}{val}')

        def cmp_both(c):
            raw = getattr(c, field)
            try:
                return eval(f'{str(raw)}{op}{str(val)}')
            except:
                return eval(f'{repr(raw)}{op}{repr(val)}')

        return cmp_both

    def _splitArgs(args):
        args = [x.lower() for x in args]

        flags, predicates = [], []
        # split predicates
        for raw in args:
            is_predicate = False
            matcher = PREDICATE_REGEX.match(raw)
            if matcher:
                field, op, val = matcher.groups()
                field = FIELD_ALIAS_MAP.get(field, field)

                try:
                    func = _genCmp(field, op, val)
                    func(FOO_CHART)
                except Exception as e:
                    pass
                else:
                    is_predicate = True

            else:  # special flags
                is_predicate = True
                if raw == 'fc':
                    func = lambda c: c.comboId > 0
                elif raw in ('fc+', 'fcp'):
                    func = lambda c: c.comboId > 1
                elif raw == 'ap':
                    func = lambda c: c.comboId > 2
                elif raw in ('ap+', 'app'):
                    func = lambda c: c.comboId > 3
                else:
                    is_predicate = False

            if is_predicate:
                predicates.append(func)
            else:
                flags.append(raw)

        return flags, predicates


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


_score_rev = [
    'd', 'c', 'b', 'bb', 'bbb', 'a', 'aa', 'aaa', 's', 'sp', 'ss', 'ssp',
    'sss', 'sssp'
]
_fc_rev = ['', 'fc', 'fcp', 'ap', 'app']


async def GetAquaDiffDataForProber(host, userId, sender=NULL_AWAIT):
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

    lstOld, lstNew = [], []
    for unit in data:
        aquaId = unit['musicId']
        if aquaId in crossMap['aOnly']: continue
        proberId = crossMap['a2p'].get(aquaId, aquaId)
        lvl_idx = unit['level']

        try:
            prober_info = prober_list.by_id(str(proberId))
            ds = prober_info['ds'][lvl_idx]
            is_new = prober_info['basic_info']['is_new']
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
            title=prober_info['title'],
            ds=ds,
            lv=str(int(ds)) + ('+' if ds - int(ds) - 0.7 >= -1e-5 else ''),
        )
        rating = computeRa(ds, unit['achievement'] * 1e-4)
        # aliases
        data = {
            'song_id': proberId,
            'level_index': lvl_idx,
            'diff': lvl_idx,
            'ra': rating,
            'achievements': unit['achievement'] * 1e-4,
            'ds': ds,
            'title': prober_info['title'],
            'level':
            str(int(ds)) + ('+' if ds - int(ds) - 0.7 >= -1e-5 else ''),
            'rate': _score_rev[unit['scoreRank']],
            'fc': _fc_rev[unit['comboStatus']],
            'type': 'DX' if aquaId >= 10000 else 'SD',
        }
        (lstNew if is_new else lstOld).append(data)

    return {
        'charts': {
            'dx': lstNew,
            'sd': lstOld,
        },
        'nickname': await GetUserNickname(host, userId)
    }
