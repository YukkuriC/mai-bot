class MessageSegment:

    def __init__(self, type, data) -> None:
        self.type = type
        self.data = data

    def __repr__(self):
        return f'<{self.type},{self.data}>'


class Message:

    def __init__(self, msgs: list[MessageSegment]) -> None:
        self.data = msgs

    def __repr__(self):
        return repr(self.data)


Event = Bot = None
