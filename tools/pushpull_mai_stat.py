import aiohttp
import asyncio
import json
from functools import partial
import os
import colorama

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
        fsmap = ',fs,fsp,fsd,fsdp,sync'.split(',')
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

        def setMaxHelper(record, key, newv, output=None, displayMapper=None):
            oldv = record[key]
            setv = max(record[key], newv)
            record[key] = setv
            ret = oldv != setv
            if output != None:
                try:
                    oldd = displayMapper[oldv]
                except:
                    oldd = oldv
                try:
                    setd = displayMapper[setv]
                except:
                    setd = setv
                if ret:
                    output.append(f'- {key}: {oldd} -> {setd}')
            return ret

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
                output = []
                setter = partial(setMaxHelper, recordAqua)
                update = \
                    setter("scoreRank", rankmap.index(recordProber["rate"]), output, rankmap) \
                    | setter("achievement", int(recordProber["achievements"] * 10000), output) \
                    | setter("deluxscoreMax", recordProber["dxScore"], output) \
                    | setter("comboStatus", fcmap.index(recordProber["fc"]), output, fcmap) \
                    | setter("syncStatus", fsmap.index(recordProber["fs"]), output, fsmap)

                # log
                if diff >= 3:
                    if create:
                        print(
                            f"""{colorama.Fore.YELLOW}Created: {title} {diffmap[diff]} {recordAqua["achievement"]/10000}{colorama.Style.RESET_ALL}"""
                        )
                    elif update:
                        print(
                            f"""{colorama.Fore.GREEN}Updated: {title} {diffmap[diff]}{colorama.Style.RESET_ALL}"""
                        )
                        for line in output:
                            print(line)

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