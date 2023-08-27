import aiohttp
import asyncio
import json
from functools import partial
import os

BASE_DIR = os.path.dirname(__file__)
os.chdir(BASE_DIR)
from cfg_reader import *

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
                print(await login.text())
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
            with open('musicMap.json', 'r', encoding='utf-8') as f:
                infoMap = json.load(f)

            mapper = {}
            for record in aquaData['userMusicDetailList']:
                mapper[record["musicId"], record["level"]] = record
            for recordProber in proberData['records']:
                # get aqua id
                title = recordProber["title"]
                isDx = recordProber["type"] == 'DX'
                if not title in infoMap[isDx]:
                    print(f'missing: {title}')
                    continue

                # get record
                mid = infoMap[isDx][title]
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


# separate stages with output
if 'stages':

    def dumper(path: str, obj):
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(obj, f, indent=4, ensure_ascii=0)

    def loader(path: str):
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data

    async def stage1():
        data = await fetchProber()
        dumper('prober.json', data)
        return data

    async def stage2():
        data = await fetchAqua()
        dumper('aqua.json', data)
        return data

    async def stage3(dump=True):
        print('Stage 3: merge data'.center(30, '='))
        step1 = loader('prober.json')
        step2 = loader('aqua.json')
        assignProberToAqua(step1, step2)
        if dump:
            dumper('output.json', step2)
        return step2


# merge workflow
async def main():
    print('Step 1: fetch DXProber'.center(30, '='))
    step1 = await fetchProber()
    print('Step 2: fetch Aqua'.center(30, '='))
    step2 = await fetchAqua()
    print('Step 3: merge data'.center(30, '='))
    assignProberToAqua(step1, step2)
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(step2, f, separators=',:')
    print('TODO Step 4: upload to aqua'.center(30, '='))


if __name__ == '__main__':
    import sys
    try:
        func = locals()[sys.argv[1]]
    except:
        func = main
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(func())