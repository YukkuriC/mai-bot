import re
from .core import CommandMatcher


def on_command(base: str, **kw):
    templates = [base]
    aliases = kw.get('aliases')
    if aliases:
        templates.extend(aliases)

    def match(msg: str):
        for prefix in templates:
            if msg.startswith(prefix):
                return True
        return False

    return CommandMatcher(match, kw)


def on_regex(pattern: str, **kw):

    def match(msg: str):
        return re.match(pattern, msg)

    return CommandMatcher(match, kw)


__all__ = [i for i in locals().keys() if i.startswith('on_')]
