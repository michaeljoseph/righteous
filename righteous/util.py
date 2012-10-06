from ConfigParser import SafeConfigParser


def read_authentication(auth_file):
    """
    Load and return a `ConfigParser` instance of the supplied file

    :param auth_file: String containing the path to the file
    :return: `None` if the file was not found / could not be parsed or
             a `ConfigParser` instance
    """
    config = SafeConfigParser()
    if config.read(auth_file):
        return config
    return None


def cache_authentication(username, password, account_id, auth_file):
    """
    Stores authentication information in the auth_file

    :param username: String of a Rightscale username
    :param password: String of the user's password
    :param account_id: String of the Rightscale account_id
    :param auth_file: String containing the path to the file
    """
    config = SafeConfigParser()
    if not config.read(auth_file):
        config.add_section('auth')
    config.set('auth', 'username', username)
    config.set('auth', 'password', password)
    config.set('auth', 'account_id', account_id)
    with open(auth_file, 'wb') as config_file:
        config.write(config_file)
