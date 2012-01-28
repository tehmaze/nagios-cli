import fnmatch
from nagios_cli import nagios
from nagios_cli.ui import Spinner


class Object(dict):
    def __getattr__(self, attr):
        if attr in self:
            return self[attr]
        else:
            raise AttributeError

class Host(Object):
    def __str__(self):
        return self.host_name


class Service(Object):
    def __str__(self):
        return self.service_description


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
        spinner = Spinner(self.cli, 'Loading nagios objects')
        filename = self.config.get('nagios.status.dat')
        for item in self.parser.parse(filename):
            if item.name == 'info':
                self.info = Object(item)

            elif item.name == 'hoststatus':
                host = Host(item)
                host['services'] = {}
                self.hosts[host.host_name] = host

            elif item.name == 'servicestatus':
                host = self.hosts.get(item.get('host_name', None), None)
                name = item.get('service_description', None)
                if host and name:
                    host.services[name] = Service(item)
                    spinner.tick()

        # Finished
        spinner.stop()

