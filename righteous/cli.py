import os
import sys
from pprint import pformat
from datetime import datetime
from optparse import OptionParser, TitledHelpFormatter

from clint.textui import puts, colored, puts_err
from clint.textui import columns

from righteous import api
from righteous.util import comma_split, read_authentication, cache_authentication

import logging
log = logging.getLogger('tty') if sys.stdin.isatty() else logging.getLogger()

AUTH_FILE = os.path.expanduser('~/.righteous')
COL = 30

def print_running_servers(servers, exclude_states=['stopped']):
    def server_owner(server_info):
        owner = None
        for p in server_info['parameters']:
            if p['name']=='EMAIL':
                owner = p['value'][5:]
        return owner

    now = datetime.now()
    output = []
    for server in servers['servers']:
        server_info = api.server_info(server['href'])
        server_settings = api.server_settings(server['href'])
        owner = server_owner(server_info)
        running = now - datetime.strptime(server['created_at'], '%Y/%m/%d %H:%M:%S +0000')
        if server['state'] not in exclude_states:
            output.append(dict(days=running.days, instance=server['nickname'], size=server_settings['ec2-instance-type'], creator=owner))

    puts(columns(
        [(colored.red('Instance')), COL],
        [(colored.green('Size')), COL],
        [(colored.magenta('Creator')), COL],
        [(colored.cyan('Running days')), COL],
    ))
    for line in sorted(output, key=lambda d: (d['days'])):
        puts(columns(
            [line['instance'], COL],
            [line['size'], COL],
            [line['creator'], COL],
            [str(line['days']), COL],
        ))


def main():

    parser = OptionParser(formatter=TitledHelpFormatter(width=78))
    parser.add_option('-l', '--list', dest='list_servers', action='store_true', help='List running integration environments')

    parser.add_option('-k', '--kill', dest='kill_env', type='string', help='Stops a comma-separated list of integration environments', action='callback', callback=comma_split)

    parser.add_option('-s', '--status', dest='server_status', type='string', help='Lists the status of a comma-separated list of integration environments', action='callback', callback=comma_split)

    parser.add_option('-r', '--remove', dest='delete_env', type='string', help='Deletes a comma-separated list of integration environments', action='callback', callback=comma_split)

    parser.add_option('-c', '--create', dest='envname', type='string', help='Create an integration environment')
    parser.add_option('-b', '--branches', dest='branches', type='string', help='Branches to build')
    parser.add_option('-e', '--email', dest='email', type='string')
    parser.add_option('-i', '--instance-type', dest='instance_type', type='string', help='Specify the instance size (small/large)')

    parser.add_option('-u', '--username', dest='username', type='string')
    parser.add_option('-p', '--password', dest='password', type='string')
    parser.add_option('-d', '--debug', dest='debug', action='store_true')
    parser.add_option('-a', '--account-id', dest='account_id', type='string', help='The account_id of your RightScale account')

    (options, args) = parser.parse_args()

    if options.debug:
        logging.basicConfig(level=logging.DEBUG)

    config = read_authentication(AUTH_FILE)

    if (options.username and options.password and options.account_id):
        username, password, account_id = options.username, options.password, options.account_id
    else:
        username, password, account_id = tuple(config.get('auth', key) for key in config.options('auth'))

    server_parameters = dict(config.items('server-defaults'))
    api.init(username, password, account_id, **server_parameters)

    if username:
        if api.login():
            cache_authentication(username, password, account_id, AUTH_FILE)
        else:
            puts_err(colored.red('Authentication failed'))
            exit(2)
    else:
        puts_err(colored.red('Missing authentication information'))
        # TODO: more helpful instructions
        parser.print_help()
        exit(2)

    if options.list_servers:
        servers = api.list_servers()
        print_running_servers(servers, exclude_states=[])

    elif options.envname and options.email:
        server_template_parameters = dict(envname=options.envname, email=options.email, mode='unattended', branches=options.branches if options.branches else 'none')
        success, location = api.create_and_start_server(options.envname, options.instance_type or 'm1.small', server_template_parameters=server_template_parameters)
        if success:
            puts(colored.green('Created and started environment %s @ %s' % (options.envname, location)))
        else:
            puts(colored.red('Error creating environment %s' % options.envname))

    elif options.kill_env:
        for env in options.kill_env:
            answer = raw_input('Confirm decommission of %s [Y/n] ' % env)
            if answer in ['n', 'no']:
                continue
            server = api.find_server(env)
            success = api.stop_server(server['href'])
            if success:
                puts(colored.cyan('Initiated decommission of %s @ %s' % (env, server['href'])))
            else:
                puts_err(colored.magenta('Error stopping server %s @ %s' % (env, server['href'])))

    elif options.server_status:

        puts(columns(
            [(colored.green('Nickname')), 15],
            [(colored.green('Instance Type')), 10],
            [(colored.green('Status')), 20],
            [(colored.green('Instance href')), 60],
        ))

        for env in options.server_status:
            server = api.find_server(env)
            settings = api.server_settings(server['href'])
            if server and options.debug:
                server_info = api.server_info(server['href'])
                puts(colored.cyan(pformat(server_info)))
                puts(colored.cyan(pformat(settings)))

            puts(columns(
                [env, 15],
                [settings['ec2-instance-type'], 10],
                [server['state'] if server else 'Found', 20],
                [server['href'] if server else 'Not', 60],

            ))

    elif options.delete_env:
        for env in options.delete_env:
            server = api.find_server(env)
            success = api.delete_server(server['href'])
            if success:
                puts(colored.green('Successfully deleted %s @ %s' % (env, server['href'])))
            else:
                puts_err(colored.magenta('Error deleting %s @ %s' % (env, server['href'])))
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
