class MessageSegment:

    def __init__(self, type, data) -> None:
        self.type = type
        self.data = data

    def __repr__(self):
        if self.type == 'image':
            url = self.data['file']
            if url.startswith('base64://'):
                url = 'data:image/png;base64,' + url[9:]
            return f'<img src="{url}">'

        return f'<{self.type},{self.data}>'


class Message(list):

    def __repr__(self):
        return ''.join(map(str, self))


Event = Bot = None
