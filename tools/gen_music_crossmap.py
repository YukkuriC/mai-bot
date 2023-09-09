from cache_access import CacheEntry

proberData = CacheEntry.load('proberMusicData')
aquaData = CacheEntry.load('aquaMusicData')

targets = {}, {}, [], []
p2a, a2p, pOnly, aOnly = targets

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
        print('same:', proberId, proberTitle)

for mid in aquaData['diff'].keys():
    if not mid in a2p:
        aOnly.append(mid)

output = {k: v for k, v in locals().items() if v in targets}
CacheEntry.dump('crossMap', output)
