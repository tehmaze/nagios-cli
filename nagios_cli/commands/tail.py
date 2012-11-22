import time
from nagios_cli.commands.base import Command
from nagios_cli.objects import Host, Service
from nagios_cli.fields import FIELDS
from nagios_cli.ui import Fancy
from nagios_cli.util import tail
from nagios_cli.filters import Parser


class Log(object):
    ignored = (
        'Warning',
        'CURRENT HOST STATE',
        'CURRENT SERVICE STATE',
        'EXTERNAL COMMAND',
        'LOG ROTATION',
        'LOG VERSION',
        'HOST NOTIFICATION',
        'SERVICE DOWNTIME ALERT',
        'SERVICE EVENT HANDLER',
        'SERVICE NOTIFICATION',
        'PASSIVE HOST CHECK',
        'PASSIVE SERVICE CHECK',
    )
    current_states = ['OK', 'WARNING', 'CRITICAL', 'UNKNOWN']
    state_types = ['SOFT', 'HARD']

    def parse(self, line):
        if line.startswith('[') and ': ' in line:
            timestamp, rest = line[1:].split('] ', 1)
            kind, rest = rest.split(': ', 1)
            # [1327916763] HOST DOWNTIME ALERT: mc01ccmdb-02;STARTED; Host has entered a period of scheduled downtime
            if kind == 'HOST DOWNTIME ALERT':
                part = rest.split(';')
                return Host(dict(
                    host_name = part[0],
                    plugin_output = part[2].strip(),
                ))

            # [1327878075] SERVICE ALERT: mc01monitorsrdb-02;BOOK HTTPD death;CRITICAL;HARD;3;CRITICAL: Failed to run query
            # [1327916763] SERVICE DOWNTIME ALERT: mc01ccmdb-02;SSH;STARTED; Service has entered a period of scheduled downtime
            elif kind == 'SERVICE ALERT':
                part = rest.split(';')
                return Service(dict(
                    last_check          = \
                        FIELDS['last_check'](timestamp),
                    host_name           = \
                        FIELDS['host_name'](part[0]),
                    service_description = \
                        FIELDS['service_description'](part[1]),
                    current_state       = \
                        FIELDS['current_state'](Log.current_states.index(part[2])),
                    state_type          = \
                        FIELDS['state_type'](Log.state_types.index(part[3])),
                    plugin_output       = \
                        FIELDS['plugin_output'](part[5]),
                ))

            # Ignore
            elif kind in Log.ignored:
                pass
            else:
                print 'Unable to parse kind %r' % (kind,)

    def parse_file(self, filename):
        for line in file(filename):
            obj = self.parse(line)
            if obj:
                yield obj


class Tail(Command):
    def run(self, *filters):
        '''
        Follow events as they are recorded to the logs.
        '''
        filters = ' '.join(filters)
        self.today = ''

        # Tail log
        log = Log()
        filename = self.cli.config.get('nagios.log_file')
        self.cli.sendline('following %s' % (filename,))

        try:
            for line in tail(filename):
                #print line
                obj = log.parse(line)
                if isinstance(obj, Service):
                    if not self.filter(filters,
                        host=obj.host_name,
                        service=obj.service_description,
                        output=obj.plugin_output):
                        continue
                    self.show_service(obj)
                elif isinstance(obj, Host):
                    if not self.filter(filters,
                        host=obj.host_name,
                        service='',
                        output=obj.plugin_output):
                        continue
                    self.show_host(obj)
        except KeyboardInterrupt:
            pass
        except SyntaxError, e:
            self.cli.sendline('Syntax error: %s' % (str(e),))

    def filter(self, filters, **scope):
        if not filters:
            return True
        else:
            return Parser.parse(filters, **scope)

    def show_date(self, date):
        self.today = date
        self.cli.sendline('--- day changed to %s ---' % (date,))

    def show_service(self, service):
        date, clock = service.last_check.split(' ')
        if date != self.today:
            self.show_date(date)

        # Fancy formatter
        fancy = Fancy(self.cli.ui)
        output = ' '.join(service.plugin_output.splitlines()).strip()
        self.cli.sendline('%s %s > %s:' % (
            clock,
            service.host_name,
            service.service_description))
        self.cli.sendline('    %s, %s' % (
            fancy.state(service.current_state),
            output))

DEFAULT = (
    Tail('tail'),
)

