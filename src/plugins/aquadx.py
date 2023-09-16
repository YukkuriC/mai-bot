from nonebot import on_command
from nonebot.params import CommandArg
from src.libraries import aqua, aqua_best
from src.libraries.image import *
from cache import CacheShelve
from nonebot.adapters.onebot.v11 import Message, MessageSegment

if 'shelve interface':
    K_USERID = 'aime_user_id'
    K_HOST = 'aqua_host'

    def getAqua():
        return CacheShelve.get(K_HOST, 'localhost')

    def getUserId():
        return CacheShelve.get(K_USERID)


h_aqua = on_command('aqua')


@h_aqua.handle()
async def _(message=CommandArg()):
    args = str(message).strip().split()
    if not args:
        return await h_aqua.finish(f'Current aqua server is: {getAqua()}')
    if len(args) == 1 and args[0] != 'help':
        CacheShelve.set(K_HOST, args[0])
        return await h_aqua.finish(f'Current aqua server set to: {args[0]}')

    await h_aqua.send(f'''Usage:
1) "aqua" to query current aqua server')
2) "aqua <location>" to set new aqua server''')


h_aime = on_command('aime')


@h_aime.handle()
async def _(message=CommandArg()):
    args = str(message).strip().split()
    if not args:
        code = getUserId()
        if code:
            await h_aime.send(f'Saved user id is: {code}')
        else:
            await h_aime.send(f'No saved user id')
        return
    if len(args) == 1 and args[0] != 'help':
        data = await aqua.queryAime(getAqua(), aimeId=args[0])
        if data and (code := data.get('extId')):
            CacheShelve.set(K_USERID, code)
            return await h_aime.finish(f'User id saved: {code}')
        else:
            return await h_aime.finish(f'Query error: {data}')

    await h_aime.send(f'''Usage:
1) "aime" to view current saved aime user id')
2) "aime <code>" to query user id with access code & save to database''')


h_b50 = on_command('aqua_b50', priority=114514)


@h_b50.handle()
async def _():
    host = getAqua()
    user = getUserId()

    raw = await aqua_best.GenB50(host, user, sender=h_b50.send)
    await h_b50.send(
        Message([
            MessageSegment("image", {
                "file":
                f"base64://{str(image_to_base64(raw), encoding='utf-8')}"
            })
        ]))


h_b40 = on_command('aqua_b40', priority=114514)


@h_b40.handle()
async def _():
    host = getAqua()
    user = getUserId()

    raw = await aqua_best.GenB40(host, user, sender=h_b50.send)
    await h_b40.send(
        Message([
            MessageSegment("image", {
                "file":
                f"base64://{str(image_to_base64(raw), encoding='utf-8')}"
            })
        ]))
