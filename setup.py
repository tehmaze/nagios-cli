#! /usr/bin/env python

from distutils.core import setup, Extension

parser = Extension('nagios_cli/_parser',
    sources = [
        'src/mmapfile.c',
        'src/objects.c',
        'src/status.c',
        'src/parser.c',
    ],
    libraries = [
        'c',
    ],
    include_dirs = [
        'include',
    ],
)

setup(
    name         = 'nagios_cli',
    version      = '0.1',
    description  = 'Nagios command line interface',
    author       = 'Wijnand Modderman-Lenstra',
    author_email = 'maze@pyth0n.org',
    packages     = [
        'nagios_cli',
        'nagios_cli.commands',
        'nagios_cli.filters',
    ],
    scripts      = ['nagios-cli'],
    ext_modules  = [parser],
)
