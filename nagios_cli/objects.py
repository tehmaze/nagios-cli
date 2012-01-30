import fnmatch
from nagios_cli import nagios
from nagios_cli.context import Section
from nagios_cli.ui import Spinner
from nagios_cli.fields import FIELDS


class Object(Section, dict):
    @classmethod
    def convert(cls, data={}, strict=False, limit=()):
        obj = cls()
        for key, value in data.iteritems():
            if limit and key not in limit:
                continue
            elif key in FIELDS:
                obj[key] = FIELDS[key](value)
            elif strict:
                raise TypeError, 'Field type "%s" unknown' % (key,)
        return obj

    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError

class Host(Object):
    def __str__(self):
        return '(host) %s' % (self.host_name,)


class Service(Object):
    def __str__(self):
        return str(self.service_description)


class Objects(object):
    def __init__(self, cli, config):
        self.cli = cli
        self.config = config
        self.info = None
        self.hosts = {}

        self.parser = nagios.Parser(define=False)
        self.parse_status()

    def filter(self, pattern):
        return fnmatch.filter(self.hosts.keys(), pattern)

    def parse_status(self):
        if not self.config.options.quiet:
            spinner = Spinner(self.cli, 'Loading nagios objects')
        filename = self.config.get('nagios.status_file')

        limit = dict(
            info = (),
            hoststatus = self.config.get_list('object.host.status'),
            servicestatus = self.config.get_list('object.service.status'),
        )
        limit['hoststatus'].extend(['host_name', 'current_status'])
        limit['servicestatus'].extend(['host_name', 'current_status', 'service_description'])

        for item in self.parser.parse(filename, limit=limit.keys()):
            if item.name == 'info':
                self.info = Object.convert(item)

            elif item.name == 'hoststatus':
                host = Host.convert(item, limit=limit['hoststatus'])
                host['services'] = {}
                self.hosts[str(host.host_name)] = host

            elif item.name == 'servicestatus':
                host = self.hosts.get(item.get('host_name', None), None)
                name = item.get('service_description', None)
                if host and name:
                    # XXX We do this because Python's readline has limitations,
                    # XXX as it's not able to handle quotation. Therefor we
                    # XXX need to make sure we have no services with spaces :(
                    name = name.replace(' ', '-')
                    host.services[name] = Service.convert(item, limit=limit['servicestatus'])
                    if not self.config.options.quiet:
                        spinner.tick()

        # Finished
        if not self.config.options.quiet:
            spinner.stop()

