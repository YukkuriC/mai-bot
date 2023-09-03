class Symbol:

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f'<{self.name}>'

    def __call__(self):
        return self

    def __eq__(self, other):
        return other and hasattr(other, 'name') and self.name == other.name


CommandArg = Symbol('CommandArg')
EventMessage = Symbol('EventMessage')
