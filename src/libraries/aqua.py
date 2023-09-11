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


__all__ = [k for k, v in locals().items() if getattr(v, '__call__', None)]
