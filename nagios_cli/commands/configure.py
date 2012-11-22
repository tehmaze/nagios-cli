from nagios_cli.commands.base import Command
from nagios_cli.context import Section


class Configure(Command, Section):
    def __str__(self):
        return '(configure)'

    def run(self):
        '''
        Configure program.
        '''

        self.cli.context.set(self)
        self.cli.setup_prompt()


class Set(Command):
    is_global = False

    def valid_in_context(self, context):
        obj = context.get()
        return isinstance(obj, Configure)

    def run(self, key=None, value=None):
        '''
        Set or get current configuration keys.

        Usage: set

            Show current configuration.

        Usage: set <key or section>

            Show current configuration in section.

        Usage: set <key> <value>

            Update the value of <key> to <value>.
        '''

        if not value:
            # All lookup
            if not key:
                for item in sorted(self.cli.config):
                    self.run(item)

            # Item lookup
            elif '.' in key:
                if key in self.cli.config:
                    self.cli.sendline('%s = %s' % (key, self.cli.config.get(key)))
                else:
                    self.cli.error('Unknown configuration item "%s"' % (key,))

            # Section lookup
            else:
                if self.cli.config.has_section(key):
                    for item in self.cli.config.get_section(key):
                        self.run(item)
                else:
                    self.cli.error('Unknown configuration section "%s"' % (key,))

        else:
            self.cli.sendline('Not implemented')

    def complete(self, text, state):
        if state == 0:
            if '.' in text:
                section = text.split('.')[0]
                self.matches = [key
                    for key in self.cli.config.get_section(section)
                    if key.startswith(text)]
            else:
                self.matches = [section + '.'
                    for section in self.cli.config.get_sections()
                    if section.startswith(text)]

            self.matches.sort()

        return self.matches


# Default commands
DEFAULT = (
    # Configure context
    Configure('configure'),
    # Available in configure context
    Set('set'),
)

