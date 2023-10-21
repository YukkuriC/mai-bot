from cache_access import CacheEntry, ensure_cache

proberData = ensure_cache('proberMusicData', 'gen_prober_music_data')
aquaData = ensure_cache('aquaMusicData', 'gen_aqua_music_map')

targets = {}, {}, [], []
p2a, a2p, pOnly, aOnly = targets
same_ids = set()

for music in proberData:
    proberId = int(music['id'])
    proberTitle = music['title']
    mType = music['type']
    if proberTitle in aquaData[mType]:
        aquaId = aquaData[mType][proberTitle]
    else:
        pOnly.append(proberId)
        continue
    if proberId != aquaId:
        p2a[proberId] = aquaId
        a2p[aquaId] = proberId
    else:
        same_ids.add(proberId)
        print('same:', proberId, proberTitle)

for mid in aquaData['diff'].keys():
    if mid not in a2p and mid not in same_ids:
        aOnly.append(mid)

output = {k: v for k, v in locals().items() if v in targets}
CacheEntry.dump('crossMap', output)
