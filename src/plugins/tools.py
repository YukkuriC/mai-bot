from nonebot import on_command
from nonebot.params import CommandArg
from nonebot.typing import T_State
from nonebot.adapters.onebot.v11 import Message, Event, Bot, MessageSegment
import os, sys

TARGET_DIR = os.path.abspath(os.path.join(__file__, '../../../tools'))


def get_tools():
    res = []
    for file in os.listdir(TARGET_DIR):
        name, ext = os.path.splitext(file)
        if ext.lower() == '.py':
            res.append(name)
    return res


tools_handler = on_command('run_tool')


@tools_handler.handle()
async def _(bot: Bot, event: Event, state: T_State, message=CommandArg()):
    tool_name = str(message).strip()
    all_tools = get_tools()
    tool_valid = tool_name in all_tools
    if (not tool_valid) and message and message not in ('list', 'help'):
        await tools_handler.send(f'invalid tool: {tool_name}')
    if not tool_valid:
        tools_lister = '\n'.join(all_tools)
        return await tools_handler.finish(f'''usage:
tools [list|help]: 列出可用命令
可用命令：
{tools_lister}
''')

    try:
        os.chdir(TARGET_DIR)
        os.system(f'python {tool_name}.py')
    except:
        pass
    try:
        exit()
    except:
        pass
