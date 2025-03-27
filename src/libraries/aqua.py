import aiohttp

from tools.cfg_reader import *


async def fetchAqua():
    if fetchAqua.cachedAquaData:
        return fetchAqua.cachedAquaData
    loc = f'{AQUA_HOST}/aqua/api/v2/game/mai2/export?token={AQUA_INNER_ID}'
    async with aiohttp.ClientSession() as session:
        async with session.get(loc) as dump:
            res = await dump.json()
            fetchAqua.cachedAquaData = res
            return res


fetchAqua.cachedAquaData = None


async def fetchMusic():
    return (await fetchAqua())["userMusicDetailList"]


async def fetchNickname():
    return (await fetchAqua())["userData"]["userName"]


__all__ = [k for k, v in locals().items() if getattr(v, '__call__', None)]
