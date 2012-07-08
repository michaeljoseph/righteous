from ConfigParser import SafeConfigParser


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
