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
        if self.ui.config.get('color.enabled', True):
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
