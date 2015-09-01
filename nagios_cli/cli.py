import os
import re
try:
    import readline
except ImportError:
    import warnings
    warnings.warn('No readline available')
    readline = None
import sys
from nagios_cli import command, nagios
from nagios_cli.context import Context
from nagios_cli.ui import UI
from nagios_cli.objects import Objects

RE_SPACING   = re.compile(r'\s+')
RE_RUN_GIVEN = re.compile(r'^run\(\) takes.* \((?P<given>\d+) given\)')


class CLI(object):
    def __init__(self, config):
        self.config = config
        # CLI user interface
        self.ui = UI(config)
        # CLI commands
        self.commands = {}
        # CLI context
        self.context = Context()
        # Readline matches
        self.matches = []
        # Nagios objects
        self.objects = Objects(self, config)
        # Nagios command pipe
        self.command = nagios.Command(config)

        self.setup_prompt()
        if readline:
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

    def send(self, text, error=False):
        if error:
            sys.stderr.write(text)
        else:
            sys.stdout.write(text)

    def sendline(self, text, error=False):
        self.send(text + '\n', error=error)

    def error(self, text):
        self.sendline(self.ui.color('error', text), error=True)

    def warn(self, text):
        self.sendline(self.ui.color('warn', text), error=True)

    def ask_bool(self, question, min_length=None, default=None):
        if min_length:
            question = question.ljust(min_length, ' ')

        answer = None
        prompt = question + ' [yn]: ' 
        if default is not None:
            if default is True or default in 'yY':
                prompt = question + ' [Yn]: '
                default = True
            
            elif default is False or default in 'nN':
                prompt = question + ' [yN]: '
                default = False

            else:
                default = None

        while answer is None:
            answer = raw_input(prompt)
            if answer:
                if answer in 'yY':
                    answer = True
                elif answer in 'nN':
                    answer = False
                else:
                    self.error('Invalid response')
                    answer = None
            else:
                answer = default

        return answer 

    def ask_str(self, question, min_length=None):
        if min_length:
            question = question.ljust(min_length, ' ')

        answer = None
        prompt = question + ': '
        while answer is None:
            answer = raw_input(prompt)
            if not answer:
                answer = None
        
        return answer

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
            info = RE_RUN_GIVEN.search(e.message)
            if info:
                # Function arguments count (minus self)
                args = self.commands[name].run.func_code.co_argcount - 1
                try:
                    least = args - len(self.commands[name].run.func_defaults)
                except TypeError:
                    least = 0
                # Given arguments count (minus self)
                given = int(info.groupdict()['given']) - 1
                if args == least:
                    error = 'exactly'
                    count = args
                elif given < least:
                    error = 'at least'
                    count = least
                elif given > args:
                    error = 'at most'
                    count = args
                else:
                    print 'huh?', args, least, given
                    return

                plural = ''
                if count != 1:
                    plural = 's'
                self.error('Syntax error: %s takes %s %d argument%s (%d given)' % \
                    (name, error, count, plural, given))
                return True
            else:
                print dir(e)
                print e.message
                print e.args
                raise

        return True

    def complete(self, text, state):
        if state == 0:
            if readline:
                line = readline.get_line_buffer()
            else:
                line = text
            part = RE_SPACING.split(line)

            if part and part[0]:
                cmnd = part[0]
                if len(part) == 1:
                    self.matches = [key
                        for key in self.commands.keys()
                        if key.startswith(text) and (
                            self.commands[key].is_global or \
                            self.commands[key].valid_in_context(self.context))]
                elif cmnd in self.commands:
                    text = text.replace(cmnd, '').lstrip()
                    self.matches = self.commands[cmnd].complete(text, state)
                else:
                    self.matches = []
            else:
                self.matches = [key
                    for key in self.commands.keys()
                    if self.commands[key].is_global or \
                        self.commands[key].valid_in_context(self.context)]

        try:
            return self.matches[state]
        except IndexError:
            pass

    def dispatch(self, line):
        if not line:
            self.sendline('')
            return False

        part = RE_SPACING.split(line)
        if not part:
            self.sendline('')
            return False

        cmnd, args = part[0], part[1:]
        if not self.command_run(cmnd, args):
            self.error('Invalid command "%s"' % (cmnd,))
            return True # stop
        else:
            return False

    def run(self, banner='Welcome to the nagios command line interface'):
        if not self.config.options.quiet:
            self.sendline(banner)
        self.running = True
        while self.running:
            try:
                line = raw_input(self.prompt)
            except EOFError:
                line = 'EOF'
            except KeyboardInterrupt:
                line = ''

            self.dispatch(line)

