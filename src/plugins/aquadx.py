from nonebot import on_command
from nonebot.params import CommandArg
from src.libraries import aqua
from cache import CacheShelve

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