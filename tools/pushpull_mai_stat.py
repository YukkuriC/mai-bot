import aiohttp
import asyncio
import json
from functools import partial
import os

BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)
from cfg_reader import *
from cache_access import CacheEntry, ensure_cache

dumper = CacheEntry.dump
loader = CacheEntry.load

if 'steps':

    # 1. pull from dxprober
    async def fetchProber(username=PROBER_USERNAME, password=PROBER_PASSWORD):
        async with aiohttp.ClientSession() as session:
            async with session.post(
                    "https://www.diving-fish.com/api/maimaidxprober/login",
                    json={
                        'username': username,
                        'password': password
                    }) as login:
                print(await login.json())
            async with session.get(
                    "https://www.diving-fish.com/api/maimaidxprober/player/records"
            ) as resp:
                return await resp.json()

    # 2. pull from aqua
    async def fetchAqua(dbId=AQUA_INNER_ID):
        loc = f'http://{AQUA_HOST}/api/game/maimai2/export?aimeId={dbId}'
        async with aiohttp.ClientSession() as session:
            async with session.get(loc) as login:
                return await login.json()

    # 3. merge data
    if 'transfer data':
        fcmap = ',fc,fcp,ap,app'.split(',')
        fsmap = ',fs,fsp,fsd,fsdp'.split(',')
        rankmap = 'd,c,b,bb,bbb,a,aa,aaa,s,sp,ss,ssp,sss,sssp'.split(',')
        diffmap = 'Basic,Advanced,Expert,Master,Re:Master'.split(',')

        def createAquaEntry(musicId: int, levelIdx: int):
            return {
                "musicId": musicId,
                "level": levelIdx,
                "playCount": 1,
                "achievement": 0,
                "comboStatus": 0,
                "syncStatus": 0,
                "deluxscoreMax": 0,
                "scoreRank": 0,
                "extNum1": 0
            }

        def setMaxHelper(record, key, newv):
            oldv = record[key]
            setv = max(record[key], newv)
            record[key] = setv
            return oldv != setv

        def assignProberToAqua(proberData, aquaData):
            infoMap = ensure_cache('aquaMusicData', 'gen_aqua_music_map')

            mapper = {}
            for record in aquaData['userMusicDetailList']:
                mapper[record["musicId"], record["level"]] = record
            for recordProber in proberData['records']:
                # get aqua id
                title = recordProber["title"]
                if not title in infoMap[recordProber["type"]]:
                    print(f'missing: {title}')
                    continue

                # get record
                mid = infoMap[recordProber["type"]][title]
                diff = recordProber["level_index"]
                mkey = (mid, diff)
                create, update = False, False

                if not mkey in mapper:
                    mapper[mkey] = (newRecord := createAquaEntry(mid, diff))
                    aquaData['userMusicDetailList'].append(newRecord)
                    create = True
                recordAqua = mapper[mkey]

                # update
                setter = partial(setMaxHelper, recordAqua)
                update = \
                    setter("achievement", int(recordProber["achievements"] * 10000)) \
                    | setter("deluxscoreMax", recordProber["dxScore"]) \
                    | setter("comboStatus", fcmap.index(recordProber["fc"])) \
                    | setter("syncStatus", fsmap.index(recordProber["fs"])) \

                # not important & often sync fail
                setter("scoreRank", rankmap.index(recordProber["rate"]))

                # log
                if create or update:
                    print(
                        f"""{'Created' if create else 'Updated'}: {title} {diffmap[diff]} {recordAqua["achievement"]/10000}"""
                    )

    # 4. upload to aqua
    async def uploadAquaData(obj):
        async with aiohttp.ClientSession() as session:
            loc = f'http://localhost/api/game/maimai2/import'
            async with session.post(loc, json=obj) as upload:
                print(await upload.json())


# separate stages with output
if 'stages':

    async def stage1():
        data = await fetchProber()
        dumper('prober', data)
        return data

    async def stage2():
        data = await fetchAqua()
        dumper('aqua', data)
        return data

    async def stage3():
        step1 = loader('prober')
        step2 = loader('aqua')
        assignProberToAqua(step1, step2)
        dumper('output', step2)
        return step2

    async def stage4():
        step3 = loader('output')
        await uploadAquaData(step3)


# merge workflow
async def main():
    print('Step 1: fetch DXProber'.center(30, '='))
    step1 = await fetchProber()
    print('Step 2: fetch Aqua'.center(30, '='))
    step2 = await fetchAqua()
    print('Step 3: merge data'.center(30, '='))
    assignProberToAqua(step1, step2)
    print('Step 4: upload to aqua'.center(30, '='))
    await uploadAquaData(step2)


if __name__ == '__main__':
    import sys
    try:
        func = locals()[sys.argv[1]]
    except:
        func = main
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(func())