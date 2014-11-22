import time
import sys


class Command(object):
    def __init__(self, config):
        self.config = config
        self.filename = config.get('nagios.command_file')
        try:
            self.pipe = open(self.filename, 'a')
        except (IOError, OSError), e:
            self.pipe = None

    def __call__(self, *args):
        if self.pipe is None:
            return

        self.pipe.write('[%d] %s\n' % (time.time(),
            ';'.join(map(str, args))))
        self.pipe.flush()

    def _read_only(self):
        return not(bool(self.pipe))

    read_only = property(_read_only)


class Section(dict):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Parser(object):
    def __init__(self, define=True, limit=()):
        self.section = None
        self.define = define
        self.limit = limit

    def end_section(self):
        if self.section:
            section = self.section
            self.section = None
            return section

    def new_section(self, name):
        if not self.limit or name in self.limit:
            self.section = Section(name)

    def parse(self, filename, limit=None):
        if limit is not None:
            self.limit = limit

        retry = 10
        handle = None
        while handle is None:
            try:
                handle = open(filename, 'rb')
            except:
                retry -= 1
                if retry:
                    print '%s is not available, retry %d' % (filename, retry)
                    time.sleep(0.5)
                else:
                    print '%s is not available' % (filename,)
                    sys.exit(0)

        for line in handle:
            line = line.strip()

            if not line:
                continue

            elif self.section is None:
                if self.define:
                    if line[:6] == 'define' and line[-1] == '{':
                        self.new_section(line[7:-1].strip())
                elif line[-1] == '{':
                    self.new_section(line[:-1].strip())

            elif line == '}':
                yield self.end_section()

            elif line[0] == '#':
                continue

            else:
                if self.define:
                    try:
                        space = line.index(' ')
                        self.section[line[:space]] = line[space + 1:]
                    except ValueError:
                        pass
                elif '=' in line:
                    try:
                        equal = line.index('=')
                        self.section[line[:equal]] = line[equal + 1:]
                    except ValueError:
                        pass
