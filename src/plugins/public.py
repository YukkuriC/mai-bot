from nonebot import on_command
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, Event, Bot
from src.libraries.image import *
from src.inject_cmdbot.core import HELP_MAP

help = on_command('help')


@help.handle()
async def _(bot: Bot, event: Event, state: T_State, message: Message):
    msgs = []
    for file, lst in HELP_MAP.items():
        msgs.append(file + ':')
        for c in lst:
            msgs.append(f'- {c}')

    await help.send(Message('\n'.join(msgs)))
