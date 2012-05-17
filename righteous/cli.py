from righteous import api
from datetime import datetime
#import sys
from optparse import OptionParser, TitledHelpFormatter
from ConfigParser import SafeConfigParser
#import argparse
import os
from pprint import pprint
from clint.textui import puts, colored
from clint.textui import columns

AUTH_FILE = os.path.expanduser('~/.righteous')

# TODO: move
def server_owner(server_info):
    owner = None
    for p in server_info['parameters']:
        if p['name']=='EMAIL':
            owner = p['value'][5:]
    return owner

def print_running_servers(servers, exclude_states=['stopped']):
    now = datetime.now()
    output = []
    col = 30
    for server in servers['servers']:
        server_info = api.server_info(server['href'])
        server_settings = api.server_settings(server['href'])
        owner = server_owner(server_info)
        running = now - datetime.strptime(server['created_at'], '%Y/%m/%d %H:%M:%S +0000')
        if server['state'] not in exclude_states:
            output.append(dict(days=running.days, instance=server['nickname'], size=server_settings['ec2-instance-type'], creator=owner))

    puts(columns(
        [(colored.red('Instance')), col],
        [(colored.green('Size')), col],
        [(colored.magenta('Creator')), col],
        [(colored.cyan('Running days')), col],
    ))
    for line in sorted(output, key=lambda d: (d['days'])):
        puts(columns(
            [line['instance'], col],
            [line['size'], col],
            [line['creator'], col],
            [str(line['days']), col],
        ))

#def delete_stopped_servers(servers):
    #now = datetime.now()
    #for server in servers['servers']:
        ##owner = server_owner(server)
        #running = now - datetime.strptime(server['created_at'], '%Y/%m/%d %H:%M:%S +0000')
        #if server['state']=='stopped':
            #puts(colored.red('Deleting stopped server %s %s running for %s days' % (server['nickname'], server['href'], running)))
            #api.delete_server(server['href'])

#def stop_stranded_servers(servers):
    #for server in servers['servers']:
        ##server_info = api.server_info(server['href'])
        #if server['state']=='stranded':
            #api.stop_server(server['href'])

# move
# http://stackoverflow.com/questions/392041/python-optparse-list
def comma_split(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def read_authentication():
    config = SafeConfigParser()
    if config.read(AUTH_FILE):
        return config
    return None

def cache_authentication(username, password, account_id):
    config = SafeConfigParser()
    if not config.read(AUTH_FILE):
        config.add_section('auth')
    config.set('auth', 'username', username)
    config.set('auth', 'password', password)
    config.set('auth', 'account_id', account_id)
    with open(AUTH_FILE, 'wb') as config_file:
        config.write(config_file)

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

    config = read_authentication()

    if (options.username and options.password and options.account_id):
        username, password, account_id = options.username, options.password, options.account_id
    else:
        username, password, account_id = tuple(config.get('auth', key) for key in config.options('auth'))

    server_parameters = dict(config.items('server-defaults'))
    api.init(username, password, account_id, **server_parameters)

    if username:
        if api.login():
            cache_authentication(username, password, account_id)
        else:
            # TODO: clint colorise
            print 'Authentication failed'
            exit(2)
    else:
        # TODO: clint colorise
        print 'Missing authentication information'
        # TODO: more helpful instructions
        parser.print_help()
        exit(2)

    if options.list_servers: # todo: check config for deployment_id, look for it in options
        servers = api.list_servers()
        print_running_servers(servers, exclude_states=[])

    elif options.envname and options.email:
        # TODO: move inside api?
        # TODO: configuration for instance type / region and alternate server
        # templates (rightscale limitation: ....)

        #if options.instance_type and options.instance_type in ['small','large']:
            #defaults['instance_type'] = 'm1.%s' % options.instance_type
            #defaults['server_template_href'] = server_template_map[defaults['instance_type']]

        server_template_parameters = dict(envname=options.envname, email=options.email, mode='unattended', branches=options.branches if options.branches else 'none')

        response, content = api.create_and_start_server(options.envname, server_template_parameters)
        if response['status']=='201':
            print 'Created and started environment %s @ %s' % (options.envname, response['location'])
        else:
            print response, content

    elif options.kill_env:
        for env in options.kill_env:
            # TODO: clint colorise
            answer = raw_input('Confirm decommission of %s ([enter/y]/[n|no])' % env)
            if answer in ['n', 'no']:
                continue
            server = api.find_server(env)
            success = api.stop_server(server['href'])
            if success:
                print 'Initiated decommission of %s @ %s' % (env, server['href'])
            else:
                print 'Error stopping server %s @ %s' % (env, server['href'])

    elif options.server_status:
        for env in options.server_status:
            server = api.find_server(env)
            settings = api.server_settings(server['href'])
            if server and options.debug:
                server_info = api.server_info(server['href'])
                pprint(server_info)
                pprint(settings)
            print '%s (%s): %s' % (env, settings['ec2-instance-type'], '%s %s' % (server['href'], server['state']) if server else 'Not Found')

    elif options.delete_env:
        for env in options.delete_env:
            server = api.find_server(env)
            success = api.delete_server(server['href'])
            if success:
                print 'Successfully deleted %s @ %s' % (env, server['href'])
            else:
                print 'Error deleting %s @ %s' % (env, server['href'])
    else:
        parser.print_help()

if __name__ == '__main__':
    main()
