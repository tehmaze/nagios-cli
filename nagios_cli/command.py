from nagios_cli.commands import configure, generic, objects

# Default commands, load all DEFAULTs from the loaded modules
DEFAULT = reduce(lambda a, b: a+b, map(lambda module: module.DEFAULT,
        (generic, configure, objects)))
