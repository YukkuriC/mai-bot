from .inject import inject
from .plugin_loader import load_plugins
from .decorators import *
from .core import handle_message, sort_priority
from .fake_module import *

import sys, asyncio, traceback


async def io_main():
    sort_priority()
    if len(sys.argv) > 1:
        msg = ' '.join(sys.argv[1:])
        await handle_message(msg)
    else:
        while 1:
            print('=' * 30)
            msg = input()
            try:
                await handle_message(msg)
            except:
                print(traceback.print_exc())


def run():
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(io_main())
