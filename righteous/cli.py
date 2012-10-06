"""
righteous
Interact with the RightScale Server API.

Usage:
  righteous [options] list
  righteous [options] create <environment> <instance-type>
                             (<template-key>=<template-value>)...
  righteous [options] stop <environment>...
  righteous [options] status <environment>...
  righteous [options] delete <environment>...
  righteous --version

Options:
  -c FILE --config=FILE        Configuration file path, ~/.righteous default
  -v --verbose                 Show debug output.
  -h --help                    Show this screen.
"""
from docopt import docopt
import os
import sys
from pprint import pformat
from datetime import datetime
from StringIO import StringIO

from clint.textui import puts, colored, puts_err
from clint.textui import columns

import righteous
from righteous.util import read_authentication, cache_authentication

import logging
log = logging.getLogger('tty') if sys.stdin.isatty() else logging.getLogger()

AUTH_FILE = os.path.expanduser('~/.righteous')
COL = 30


def error(message):
    puts_err(colored.red(message))
    exit(2)


def print_running_servers(servers, exclude_states=['stopped']):

    def server_owner(server_info):
        owner = [p['value'][5:] for p in server_info['parameters']
            if p['name'] == 'EMAIL']
        return owner[0] if len(owner) else None

    output = StringIO()
    now = datetime.now()
    server_list = []
    for server in servers['servers']:
        server_info = righteous.server_info(server['href'])
        server_settings = righteous.server_settings(server['href'])
        owner = server_owner(server_info)
        running = now - datetime.strptime(server['created_at'],
            '%Y/%m/%d %H:%M:%S +0000')
        if server['state'] not in exclude_states:
            server_list.append(dict(days=running.days,
                instance=server['nickname'],
                size=server_settings['ec2-instance-type'],
                creator=owner))

    puts(columns(
        [(colored.red('Instance')), COL],
        [(colored.green('Size')), COL],
        [(colored.magenta('Creator')), COL],
        [(colored.cyan('Running days')), COL],
    ), stream=output.write)

    for line in sorted(server_list, key=lambda d: d['days']):
        puts(columns(
            [line['instance'], COL],
            [line['size'], COL],
            [line['creator'], COL],
            [str(line['days']), COL],
        ), stream=output.write)

    print output.getvalue()


def initialise(arguments):
    verbose = arguments['--verbose']
    config_file = arguments['--config']

    if verbose:
        logging.basicConfig(level=logging.DEBUG)

    config = read_authentication(config_file or AUTH_FILE)
    if not config:
        error('No configuration found. Either create "%s" or specify a '
              'configuration file with -c FILE' % (AUTH_FILE))

    username, password, account_id = tuple(config.get('auth', key)
        for key in config.options('auth'))

    server_parameters = dict(config.items('server-defaults'))
    righteous.initialise(username, password, account_id, **server_parameters)

    if righteous.login():
        cache_authentication(username, password, account_id,
            config_file or AUTH_FILE)
    else:
        error('Authentication failed')

    return verbose


def list(arguments):
    initialise(arguments)
    servers = righteous.list_servers()
    print_running_servers(servers, exclude_states=[])


def create(arguments):
    initialise(arguments)

    server_template_parameters = {}
    for argument in arguments['<template-key>=<template-value>']:
        param, value = argument.split('=')
        server_template_parameters[param] = value

    success, location = righteous.create_and_start_server(
        arguments['<environment>'][0],
        arguments['<instance-type>'] or 'm1.small',
        server_template_parameters=server_template_parameters)
    if success:
        puts(colored.green('Created and started environment %s @ %s' %
            (arguments['<environment>'][0], location)))
    else:
        error('Error creating environment %s' %
            arguments['<environment>'][0])


def stop(arguments):
    initialise(arguments)

    for environment in arguments['<environment>']:
        answer = raw_input('Confirm decommission of %s [Y/n] ' % environment)
        if answer in ['n', 'no']:
            continue

        server = righteous.find_server(environment)
        success = righteous.stop_server(server['href'])
        if success:
            puts(colored.cyan('Initiated decommission of %s @ %s' %
                (environment, server['href'])))
        else:
            puts_err(colored.magenta('Error stopping server %s @ %s' %
                (environment, server['href'])))


def delete(arguments):
    initialise(arguments)
    for environment in arguments['<environment>']:
        server = righteous.find_server(environment)
        success = righteous.delete_server(server['href'])
        if success:
            puts(colored.green('Successfully deleted %s @ %s' %
                (environment, server['href'])))
        else:
            puts_err(colored.magenta('Error deleting %s @ %s' %
                (environment, server['href'])))


def status(arguments):
    output = StringIO()
    verbose = initialise(arguments)
    environments = arguments['<environment>']

    if environments:
        puts(columns(
            [(colored.green('Nickname')), 15],
            [(colored.green('Instance Type')), 10],
            [(colored.green('Status')), 20],
            [(colored.green('Instance href')), 60],
        ), stream=output.write)

    for environment in environments:
        server = righteous.find_server(environment)
        if server:
            settings = righteous.server_settings(server['href'])
            if verbose:
                server_info = righteous.server_info(server['href'])
                puts('Server Info:\n' + colored.cyan(pformat(server_info)))
                puts('Server Settings:\n' + colored.cyan(pformat(settings)))

            puts(columns(
                [environment, 15],
                [settings['ec2-instance-type'], 10],
                [server['state'] if server else 'Found', 20],
                [server['href'] if server else 'Not', 60],

            ), stream=output.write)
        else:
            puts(colored.red('%s: Not Found' % environment),
                    stream=output.write)

    print output.getvalue()


def main():
    arguments = docopt(__doc__, version=righteous.__version__)
    for command in ['list', 'create', 'stop', 'delete', 'status']:
        if arguments[command]:
            globals()[command](arguments)

if __name__ == '__main__':
    main()
