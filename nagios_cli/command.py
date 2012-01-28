import readline
from nagios_cli import objects

class Command(object):
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


class Version(Command):
    def run(self):
        self.cli.sendline('nagios-cli version 0.1')
        self.cli.sendline('nagios version %s' % (self.cli.objects.info.version,))

class About(Command):
    def run(self):
        self.cli.sendline('nagios-cli command line interface for nagios')
        self.cli.sendline('(c) 2012 Wijnand Modderman-Lenstra, https://maze.io/')


class Exit(Command):
    def run(self):
        self.cli.sendline('Bye')
        self.cli.running = False


class EOF(Command):
    def run(self):
        self.cli.sendline('')
        if self.cli.context.pop():
            self.cli.setup_prompt()
        else:
            self.cli.dispatch('exit')


class Host(Command):
    def run(self, hostname=None):
        '''
        [<hostname>]
        '''
        if not hostname:
            self.cli.sendline('%d hosts available' % (len(self.cli.objects.hosts),))
            self.cli.sendline('')
            self.cli.sendline('To switch objects, use: host <hostname>')
            return

        if hostname in self.cli.objects.hosts:
            self.cli.context.set(self.cli.objects.hosts[hostname])
            self.cli.setup_prompt()
        else:
            self.cli.error('Host "%s" not found' % (hostname,))

    def complete(self, text, state):
        print 'Host.complete', state, text
        if state == 0:
            part = text.split()
            print 'part', part
            if not part:
                self.matches = self.cli.objects.hosts.keys()
            elif len(part) == 1:
                self.matches = [hostname
                    for hostname in self.cli.objects.hosts
                    if hostname.startswith(part[0])]
            else:
                self.matches = []

            self.matches.sort()

        print self.matches
        return self.matches


class Service(Command):
    def valid_in_context(self, context):
        obj = context.get()
        return isinstance(obj, objects.Host)

    def run(self, service=None):
        '''
        [<service>]

        Shows information about services, if you specify an argument you
        will switch the active object to the given service.
        '''

        host = self.cli.context.get()
        if not service:
            self.cli.sendline('%s services for this host' % (len(host.services),))
            for service in sorted(host.services):
                self.cli.sendline(' - "%s" (%s)' % (service, host.services[service].plugin_output))

        elif service in host.services:
            self.cli.context.add(host.services[service])
            self.cli.setup_prompt()

        else:
            self.cli.error('Service "%s" not found' % (service,))

    def complete(self, text, state):
        print 'Service.complete', state, text
        if state == 0:
            part = text.split()
            host = self.cli.context.get()
            print 'part', part
            if not part:
                self.matches = host.services.keys()
            elif len(part) == 1:
                self.matches = [service
                    for service in host.services
                    if service.startswith(part[0])]
            else:
                self.matches = []

            self.matches.sort()

        print self.matches
        return self.matches
        

class Info(Command):
    def valid_in_context(self, context):
        obj = context.get()
        return isinstance(obj, objects.Object)

    def run(self):
        obj = self.cli.context.get()
        if isinstance(obj, objects.Host):
            self.cli.sendline('Host')
        elif isinstance(obj, objects.Service):
            self.cli.sendline('Service')

# Default commands
DEFAULT = (
    # Global commands
    About('about'),
    Version('version'),
    EOF('EOF'),
    Exit('exit'),
    Exit('quit'),
    Host('host'),   
        # Host context
        Service('service'),
        # Host/Service context
        Info('info'),
        Info('show'),
)
