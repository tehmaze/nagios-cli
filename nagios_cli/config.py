# -*- coding: utf8; -*-

import ConfigParser
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

DEFAULT_CONFIG = u'''
[cli]
history                 = ~/.nagios_cli_history

[ui]
color                   = 1
prompt                  = nagios %s>
prompt_separator        = " → "

[nagios]
log                     = /var/log/nagios
command_file            = %(log)s/rw/nagios.cmd
log_file                = %(log)s/nagios.log
object_cache_file       = %(log)s/objects.cache
status_file             = %(log)s/status.dat

[object]
host.status             =
    host_name
    current_state
    plugin_output
    is_flapping
    last_check
    last_time_down
    last_state_change
    check_period
    notification_period
    current_attempt
    max_attempts
service.status          =
    host_name
    service_description
    current_state
    is_flapping
    plugin_output
    last_time_down
    last_state_change
    last_check
    next_check
    check_interval
    check_latency
    check_period
    notification_period
    current_attempt
    max_attempts

[string]
level.ok                = ↑ OK
level.warning           = ! WARNING
level.critical          = ↓ CRITICAL
level.unknown           = ↕ UNKNOWN

[color]
error                   = bold_red

prompt                  = normal
prompt.object           = bold

host.host_name          = bold
host.plugin_output      = bold
service.plugin_output   = bold

level.ok                = bold_green
level.warning           = bold_yellow
level.critical          = bold_red
level.unknown           = bold_magenta
'''

class Config(dict):
    def __init__(self, options):
        self.options = options

    def has_section(self, section):
        return bool(self.get_section(section))

    def get_list(self, key, default=[]):
        value = self.get(key, None)
        if not value:
            return default
        else:
            return filter(None, value.splitlines())

    def get_section(self, section):
        keys = []
        name = '.'.join([section, ''])
        for key in self:
            if key.startswith(name):
                keys.append(key)
        return keys

    def get_sections(self):
        sections = set()
        for key in self:
            sections.add(key.split('.')[0])
        return tuple(sections)

    def load(self, filename):
        fp = open(filename, 'rb')
        self.load_file(fp)
        fp.close()

    def load_default(self):
        self.load_str(DEFAULT_CONFIG.encode('utf-8'))

    def load_str(self, config):
        fp = StringIO(config)
        self.load_file(fp)
        fp.close()

    def load_file(self, fp):
        parser = ConfigParser.ConfigParser()
        parser.readfp(fp)
        for section in parser.sections():
            for option, value in parser.items(section):
                # Support quoted strings
                if isinstance(value, basestring):
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                self['.'.join([section, option])] = value

    def as_ini(self):
        curr = None
        ini = []
        for key, value in sorted(self.iteritems()):
            section, option = key.split('.', 1)
            if section != curr:
                if ini:
                    ini.append('')

                ini.append('[%s]' % (section,))
                curr = section

            if type(value) in [int, long, float]:
                ini.append('%s = %s' % (option, value))
            elif isinstance(value, basestring):
                # Quoted string
                if value.startswith(' ') or value.endswith(' '):
                    value = '"%s"' % (value,)
                ini.append('%s = %s' % (option, value))
            elif type(value) is bool:
                ini.append('%s = %s' % (option, int(value)))

        return '\n'.join(ini)



