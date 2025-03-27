from nonebot import on_command, on_regex
from nonebot.params import CommandArg, EventMessage
from src.libraries.maimai_best_50 import generate50_diff, generate50_query
from src.libraries.maimai_rating_base import build_prober_payload
from src.libraries import aqua_best
from src.libraries.image import *
from nonebot.adapters.onebot.v11 import Message, MessageSegment

h_b40_b50 = on_regex(r'aqua_b[45]0', priority=114514)


@h_b40_b50.handle()
async def _(message=EventMessage()):
    all_args = str(message).split()
    raw = await aqua_best.GenBest(is_b40=all_args[0] == 'aqua_b40',
                                  sender=h_b40_b50.send,
                                  extra_args=all_args[1:])
    if not raw:
        return h_b40_b50.finish(f'invalid img: {raw}')

    await h_b40_b50.send(
        Message([
            MessageSegment("image", {
                "file":
                f"base64://{str(image_to_base64(raw), encoding='utf-8')}"
            })
        ]))


aqua_diff = on_command('diff_aqua', aliases=['aqua_diff'], priority=114514)


@aqua_diff.handle()
async def _(message: Message = CommandArg()):
    username = str(message).strip()
    if not username:
        return await aqua_diff.finish('usage: aqua_diff <id|qq>')
    payload = build_prober_payload(username)

    data_prober, success = await generate50_query(payload)
    if success > 0:
        fail_id = payload['qq'] if 'qq' in payload else payload['username']
        if success == 400:
            return await aqua_diff.finish(
                f"{fail_id}: 未找到此玩家，请确保此玩家的用户名和查分器中的用户名相同。")
        elif success == 403:
            return await aqua_diff.finish(f"{fail_id}: 该用户禁止了其他人获取数据。")

    data_aqua = await aqua_best.GetAquaDiffDataForProber(aqua_diff.send)
    if not data_aqua:
        return await aqua_diff.finish('get aqua data failed')

    img = generate50_diff(data_prober, data_aqua)
    await aqua_diff.send(
        Message([
            MessageSegment("image", {
                "file":
                f"base64://{str(image_to_base64(img), encoding='utf-8')}"
            })
        ]))
