class Section(dict):
    def __init__(self, name):
        self.name = name

    def __str__(self):
        return self.name


class Parser(object):
    def __init__(self, define=True):
        self.section = None
        self.define = define

    def parse(self, filename):
        handle = open(filename, 'rb')
        for line in handle:
            line = line.strip()
            part = line.split()
            #print part

            if not part:
                continue
            
            elif self.section is None:
                if self.define:
                    if part[0] == 'define' and part[-1] == '{':
                        self.section = Section(part[1])
                elif part[-1] == '{':
                    self.section = Section(part[0])

            elif line == '}':
                yield self.section
                self.section = None

            elif line.startswith('#'):
                continue

            else:
                if self.define:
                    self.section[part[0]] = ' '.join(part[1:])
                elif '=' in line:
                    part = line.split('=', 1)
                    self.section[part[0]] = part[1]
