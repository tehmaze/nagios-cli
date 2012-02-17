class Context(object):
    def __init__(self, stack=None):
        if stack is None:
            self.stack = []
        else:
            self.stack = stack

    def add(self, item):
        '''
        Add an object to the stack.
        '''
        self.stack.append(item)

    def pop(self, item=-1, default=None):
        '''
        Remove the current active (lastly added) object from the stack.
        Returns the removed object (if any).
        '''
        if self.stack:
            return self.stack.pop(item)
        else:
            return default

    def get(self, item=-1):
        '''
        Get the current active (lastly added) object from the stack.
        '''
        return self.stack and self.stack[item]

    def set(self, item):
        '''
        Reset the stack to this single item.
        '''
        self.stack = [item]

    def empty(self):
        self.stack = []


class Section(object):
    # Override in subclass
    def __str__(self):
        '''
        String representation of the context section as displayed in the
        prompt.
        '''
        raise NotImplementedError

