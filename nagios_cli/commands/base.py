class Command(object):
    is_global = True

    def __init__(self, name):
        self.name = name
        self.cli = None
        # For completion
        self.matches = []

    def valid_in_context(self, context):
        return True

    def complete(self, text, state):
        '''
        Return the next possible completion for 'text'.                       
                                                                                 
        This is called successively with state == 0, 1, 2, ... until it          
        returns None.  The completion should begin with 'text'. 
        '''
        return None

    def run(self, *args):
        return False
