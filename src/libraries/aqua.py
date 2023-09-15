import aiohttp, json

HEADER = {
    "Content-Type": "application/json;charset=utf-8",
    "Accept": "application/json",
}


def poster(loc, data):
    return aiohttp.request('POST',
                           loc,
                           data=json.dumps(data, separators=',:'),
                           headers=HEADER)


async def queryAime(aqua_host: str, aimeId: str):
    loc = f'http://{aqua_host}/api/sega/aime/getByAccessCode'
    async with poster(loc, {'accessCode': aimeId}) as r:
        return await r.json()


async def queryMusic(aqua_host: str, userId: str):
    loc = f'http://{aqua_host}/Maimai2Servlet/Maimai2Servlet/GetUserMusicApi' 
    async with poster(loc, {
            "userId": userId,
            "nextIndex": 0,
            "maxCount": 114514
    }) as r:
        if r.status != 200:
            return None, r.status
        raw = await r.json()
        try:
            return raw['userMusicList'][0]['userMusicDetailList'], 200
        except:
            return None, 500


__all__ = [k for k, v in locals().items() if getattr(v, '__call__', None)]
