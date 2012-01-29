import datetime


class Color(object):
    ANSI = dict(
        normal       = '',
        reset        = '\033[m',
        bold         = '\033[1m',
        red          = '\033[31m',
        green        = '\033[32m',
        yellow       = '\033[33m',
        blue         = '\033[34m',
        magenta      = '\033[35m',
        cyan         = '\033[36m',
        bold_red     = '\033[1;31m',
        bold_green   = '\033[1;32m',
        bold_yellow  = '\033[1;33m',
        bold_blue    = '\033[1;34m',
        bold_magenta = '\033[1;35m',
        bold_cyan    = '\033[1;36m',
        bg_red       = '\033[41m',
        bg_green     = '\033[42m',
        bg_yellow    = '\033[43m',
        bg_blue      = '\033[44m',
        bg_magenta   = '\033[45m',
        bg_cyan      = '\033[46m',
    )

    def __init__(self, ui):
        self.ui = ui

    def __call__(self, color, format):
        if self.ui.config.get('ui.color', True):
            return self.color_str(color, format)
        else:
            return format

    def color_str(self, color, format):
        color = self.ui.config.get('color.%s' % (color,), 'normal')
        return ''.join([
            self.ANSI.get(color),
            format,
            self.ANSI.get('reset')
        ])


class Formatted(object):
    def __init__(self, ui):
        self.ui = ui

    def to_bool(self, value, default=0):
        if value is None:
            value = default
        return ['no', 'yes'][int(value)]

    def to_state(self, value, default=-1):
        if value is None:
            value = default
        value = int(value)
        if value == -1:
            return self.ui.color('level.na', 'N/A')
        elif value == 0:
            return self.ui.color('level.ok',
                self.ui.config.get('string.level.ok', 'OK'))
        elif value == 1:
            return self.ui.color('level.warning',
                self.ui.config.get('string.level.warning', 'WARNING'))
        elif value == 2:
            return self.ui.color('level.critical',
                self.ui.config.get('string.level.critical', 'CRITICAL'))
        else:
            return self.ui.color('level.unknown',
                self.ui.config.get('string.level.unknown', 'UNKNOWN'))

    def to_str(self, value, default='N/A', max_length=0):
        if value is None:
            value = default

        if max_length:
            return str(value)[:max_length]
        else:
            return str(value)

    def to_time(self, value, default=-1):
        if value is None:
            value = default
        value = float(value)
        if value < 0:
            return 'N/A'
        elif value == 0:
            return 'never'
        else:
            return str(datetime.datetime.fromtimestamp(value))


class UI(object):
    def __init__(self, config):
        self.config = config
        self.color = Color(self)


class Spinner(object):
    chars = '-\|/'

    def __init__(self, cli, prompt):
        self.cli = cli
        self.cli.send(prompt + '  ')
        self.pos = -1
        self.prompt = prompt
        self.tick()

    def __add__(self, x):
        self.tick()

    def tick(self):
        self.pos += 1
        if self.pos >= len(self.chars):
            self.pos = 0

        self.cli.send('\b%s' % (self.chars[self.pos]))
        self.cli.flush()

    def stop(self):
        self.cli.send('\r\033[K')
        self.cli.flush()
