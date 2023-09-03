import inspect

from .params import CommandArg, EventMessage


class CommandMatcher:

    def __init__(self, matcher, kwargs):
        self.matcher = matcher
        self.running = False
        self.commands = []
        self.messages = []
        self.priority = kwargs.get('priority', 0)
        self.block = kwargs.get('block', True)

        self.appended = False

    def handle(self):

        def receiver(func):
            sig = inspect.signature(func)
            func.kwSet = set(sig.parameters)
            arg_msg = sig.parameters.get('message')
            if arg_msg and arg_msg.default is not inspect.Parameter.empty:
                func.msgType = arg_msg.default
            else:
                func.msgType = EventMessage
            self.commands.append(func)
            return func

        if not self.appended:
            self.appended = True
            RULESETS.append(self)

        return receiver

    async def send(self, msg):
        if not self.running:
            return
        self.messages.append(msg)

    async def finish(self, finalMsg=None):
        if finalMsg:
            await self.send(finalMsg)
        self.running = False

    async def process(self, **kw):
        self.running = True
        self.messages = []
        for cmd in self.commands:
            msg = kw['message']
            print(
                type(cmd.msgType),
                type(CommandArg),
                type(cmd.msgType) == type(CommandArg),
                cmd.msgType == CommandArg,
            )
            if cmd.msgType == CommandArg:
                msg = msg.split(' ', 1)[1]
                kw['message'] = msg

            kw_part = {k: v for k, v in kw.items() if k in cmd.kwSet}
            await cmd(**kw_part)

    def dump(self, into: list):
        into.extend(self.messages)
        return self.messages


RULESETS: list[CommandMatcher] = []
DUMMY_EVENT = None
DUMMY_BOT = None
DUMMY_STATE = {}


def sort_priority():
    RULESETS.sort(key=lambda x: -x.priority)


async def handle_message(msg: str):
    replies = []
    for rule in RULESETS:
        if rule.matcher(msg):
            await rule.process(event=DUMMY_EVENT,
                               message=msg,
                               bot=DUMMY_BOT,
                               state=DUMMY_STATE)
            messages = rule.dump(replies)

            if rule.block:
                break

    print(replies)