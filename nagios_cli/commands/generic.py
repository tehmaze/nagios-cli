import textwrap
from nagios_cli.commands.base import Command


LICENSE = '''
Copyright (C) 2012, Wijnand Modderman-Lenstra, https://maze.io/

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''


class About(Command):
    def run(self):
        '''
        Shows information about the program.
        '''
        self.cli.sendline('nagios-cli, a nagios command line interface')
        self.cli.sendline('Copyright (C) 2012 Wijnand Modderman-Lenstra, https://maze.io/')
        self.cli.sendline('')
        self.cli.sendline('This program is FREE SOFTWARE, see the "license" command for details.')


class License(Command):
    def run(self):
        '''
        Shows the program license.
        '''
        for line in LICENSE.strip().splitlines():
            self.cli.sendline(line)


class Exit(Command):
    def run(self):
        '''
        Go back to the shell.
        '''

        self.cli.sendline('')
        self.cli.running = False


class EOF(Command):
    def run(self):
        '''
        Go up a section, or go back to the shell if in main section.
        '''

        self.cli.sendline('')
        if self.cli.context.pop():
            self.cli.setup_prompt()
        else:
            self.cli.dispatch('exit')


class Help(Command):
    def get_commands(self):
        # Get all globally and locally available commands
        globally = []
        locally = []
        for command, obj in self.cli.commands.iteritems():
            if obj.is_global:
                globally.append(command)
            elif obj.valid_in_context(self.cli.context):
                locally.append(command)

        # Sort items
        globally.sort()
        locally.sort()

        return (globally, locally)

    def run(self, command=''):
        '''
        Show help on the given command, or show available commands.
        
        Usage: help

            Show available commands.

        Usage: help <command>
            
            Show help about <command>.
        '''

        globally, locally = self.get_commands()
        commands = globally + locally

        # Display available commands
        if command:
            if command in commands:
                docs = self.cli.commands[command].run.__doc__
                text = textwrap.dedent(docs).strip()
                for line in text.splitlines():
                    self.cli.sendline(line)
                self.cli.sendline('')
            else:
                self.cli.error('Command "%s" not available' % (command,))

        else:
            self.cli.sendline('Global commands:')
            maxlen = max(map(len, globally + locally))
            maxcnt = int(float(80 / (maxlen + 2)) + 0.5)
            y = 0
            while True:
                sliced = globally[y * maxcnt:(y + 1) * maxcnt]
                if not sliced:
                    break

                for item in sliced:
                    self.cli.send(item.ljust(maxlen + 2, ' '))
                self.cli.sendline('')
                y += 1
            
            if not locally:
                return

            self.cli.sendline('')
            self.cli.sendline('Local commands:')
            y = 0
            while True:
                sliced = locally[y * maxcnt:(y + 1) * maxcnt]
                if not sliced:
                    break
                
                for item in sliced:
                    self.cli.send(item.ljust(maxlen + 2, ' '))
                self.cli.sendline('')
                y += 1
    
    def complete(self, text, state):
        if state == 0:
            globally, locally = self.get_commands()
            commands = globally + locally
            commands.sort()

            self.matches = [command
                for command in commands
                if command.startswith(text)]

        return self.matches


# Default commands
DEFAULT = (
    About('about'),
    License('license'),
    EOF('EOF'),
    EOF('..'),
    Exit('exit'),
    Exit('quit'),
    Help('help'),
)
