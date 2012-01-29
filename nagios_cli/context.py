class Context(object):
    def __init__(self, stack=[]):
        self.stack = stack

    def add(self, item):
        self.stack.append(item)

    def pop(self, item=-1, default=None):
        if self.stack:
            return self.stack.pop(item)
        else:
            return default

    def get(self, item=-1):
        return self.stack and self.stack[item]

    def set(self, item):
        self.stack = [item]


class Section(object):
    # Override in subclass
    def __str__(self):
        '''
        String representation of the context section as displayed in the
        prompt.
        '''
        raise NotImplementedError

