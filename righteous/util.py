from ConfigParser import SafeConfigParser

# http://stackoverflow.com/questions/392041/python-optparse-list
def comma_split(option, opt, value, parser):
    setattr(parser.values, option.dest, value.split(','))

def read_authentication(auth_file):
    config = SafeConfigParser()
    if config.read(auth_file):
        return config
    return None

def cache_authentication(username, password, account_id, auth_file):
    config = SafeConfigParser()
    if not config.read(auth_file):
        config.add_section('auth')
    config.set('auth', 'username', username)
    config.set('auth', 'password', password)
    config.set('auth', 'account_id', account_id)
    with open(auth_file, 'wb') as config_file:
        config.write(config_file)
