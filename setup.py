#! /usr/bin/env python

from distutils.core import setup

setup(
    name         = 'nagios_cli',
    version      = '0.1',
    description  = 'Nagios command line interface',
    author       = 'Wijnand Modderman-Lenstra',
    author_email = 'maze@pyth0n.org',
    packages     = ['nagios_cli', 'nagios_cli.commands'],
    scripts      = ['nagios-cli'],
)
