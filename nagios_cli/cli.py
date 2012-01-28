import os
import re
import readline
import sys
from nagios_cli import command
from nagios_cli.ui import UI
from nagios_cli.objects import Objects

RE_SPACING = re.compile(r'\s+')


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


class CLI(object):
    def __init__(self, config):
        self.config = config
        self.ui = UI(config)
        self.commands = {}
        self.context = Context()
        self.objects = Objects(self, config)
        self.matches = []

        self.setup_prompt()
        self.setup_readline()
        self.setup_commands()

    # Setup

    def setup_prompt(self):
        prompt = self.config.get('ui.prompt_separator', ':').join(
            map(str, self.context.stack)
        )
        self.prompt = self.ui.color('prompt',
            self.config.get('ui.prompt') % (
                self.ui.color('prompt.object',
                    self.config.get('ui.prompt_separator', ':').join(
                        map(str, self.context.stack)
                    )
                )
            )
        ) + ' '

    def setup_readline(self):
        history = self.config.get('cli.history')
        if history:
            # Load history
            history = os.path.expanduser(history)
            try:
                readline.read_history_file(history)
            except IOError:
                pass

            # Save history at exit
            import atexit
            atexit.register(readline.write_history_file, history)

        readline.set_completer(self.complete)
        readline.parse_and_bind('tab: complete')
    
        # We need hyphen in hostnames
        readline.set_completer_delims(readline.get_completer_delims().replace('-', ''))

    def setup_commands(self):
        for item in command.DEFAULT:
            self.command_add(item)

    # I/O

    def flush(self):
        sys.stdout.flush()

    def send(self, text):
        sys.stdout.write(text)

    def sendline(self, text):
        self.send(text + '\n')

    def error(self, text):
        self.sendline(self.ui.color('error', text))

    def warn(self, text):
        self.sendline(self.ui.color('warn', text))

    # Commands

    def command_add(self, obj):
        self.commands[obj.name] = obj
        self.commands[obj.name].cli = self

    def command_run(self, name, args):
        if name not in self.commands:
            matches = []
            for state in xrange(0, len(self.commands)):
                match = self.complete(name, state)
                if match is None:
                    break
                else:
                    matches.append(match)

            # One possible match, complete it
            if len(matches) == 1:
                return self.command_run(matches[0], args)

            return False

        if not self.commands[name].valid_in_context(self.context):
            print 'Not valid in context'
            return False

        try:
            self.commands[name].run(*args)
        except TypeError, e:
            msg = e.message
            if msg.startswith('run()') and (
                'takes exactly' in msg or \
                'takes at least' in msg or \
                'takes at most' in msg):
                self.error('Syntax error')
                return True
            else:
                raise

        return True

    def complete(self, text, state):
        if state == 0:
            line = readline.get_line_buffer()
            part = RE_SPACING.split(line)

            if part and part[0]:
                cmnd = part[0]
                if len(part) == 1:
                    self.matches = [key
                        for key in self.commands.keys()
                        if key.startswith(text) and
                        self.commands[key].valid_in_context(self.context)]
                elif cmnd in self.commands:
                    text = text.replace(cmnd, '').lstrip()
                    self.matches = self.commands[cmnd].complete(text, state)
                else:
                    self.matches = []
            else:
                self.matches = self.commands.keys()

        try:
            return self.matches[state]
        except IndexError:
            pass

    def dispatch(self, line):
        part = RE_SPACING.split(line)
        if not part:
            return

        cmnd, args = part[0], part[1:]
        if not self.command_run(cmnd, args):
            self.error('Invalid command "%s"' % (cmnd,))

    def run(self, banner='Welcome to the nagios command line interface'):
        self.sendline(banner)
        self.running = True
        while self.running:
            try:
                line = raw_input(self.prompt)
            except EOFError:
                line = 'EOF'
            except KeyboardInterrupt:
                line = 'exit'

            stop = self.dispatch(line)
            if stop:
                self.running = False

