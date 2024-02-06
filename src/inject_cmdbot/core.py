import inspect, os, tempfile

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
            if cmd.msgType == CommandArg:
                msg = msg.split(' ', 1)
                kw['message'] = msg[1] if len(msg) > 1 else ''

            kw_part = {k: v for k, v in kw.items() if k in cmd.kwSet}
            await cmd(**kw_part)

    def dump(self, into: list):
        into.extend(self.messages)
        return self.messages


RULESETS: list[CommandMatcher] = []
DUMMY_EVENT = None
DUMMY_BOT = None
DUMMY_STATE = {}

HTML_TEMPLATE = '''<html>
<head><meta charset="utf-8"><title>{1}</title></head>
<body><pre>{0}</pre></body></html>'''


def sort_priority():
    RULESETS.sort(key=lambda x: -x.priority)


async def handle_message(input_msg: str):
    from nonebot.adapters.onebot.v11 import Message, MessageSegment
    replies: list[Message] = []
    for rule in RULESETS:
        if rule.matcher(input_msg):
            await rule.process(event=DUMMY_EVENT,
                               message=input_msg,
                               bot=DUMMY_BOT,
                               state=DUMMY_STATE)
            rule.dump(replies)

            if rule.block:
                break

    # merge messages
    hasImg = False
    filtered_msgs = []

    # first iter
    for msg in replies:
        if isinstance(msg, str):
            filtered_msgs.append(msg)
            filtered_msgs.append('\n')
            continue
        for seg in msg:
            if isinstance(seg, MessageSegment):
                if seg.type == 'text':
                    seg = seg.data['text']
                else:
                    if seg.type == 'image':
                        hasImg = True
                    else:
                        print('unsupported type:', seg.type)
                    seg = f'\n{seg}\n'
            filtered_msgs.append(seg)
        filtered_msgs.append('\n')
    else:
        if filtered_msgs:
            filtered_msgs.pop()

    msg_body = ''.join(filtered_msgs)

    # image html
    if hasImg:
        tmp_path = os.path.join(tempfile.gettempdir(), 'tmp.html')
        with open(tmp_path, 'w', encoding='utf-8') as f:
            print(HTML_TEMPLATE.format(msg_body, input_msg), file=f)
        os.system(f"start {tmp_path}")

    # pure text
    else:
        print(msg_body)
