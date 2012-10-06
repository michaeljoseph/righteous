# coding: utf-8

"""
righteous.config


Settings object, lifted from https://github.com/kennethreitz/requests
"""


class Settings(object):
    _singleton = {}

    # attributes with defaults
    __attrs__ = []

    def __init__(self, **kwargs):
        super(Settings, self).__init__()

        self.__dict__ = self._singleton

    def __call__(self, *args, **kwargs):
        # new instance of class to call
        r = self.__class__()

        # cache previous settings for __exit__
        r.__cache = self.__dict__.copy()
        map(self.__cache.setdefault, self.__attrs__)

        # set new settings
        self.__dict__.update(*args, **kwargs)

        return r

    def __enter__(self):
        pass

    def __exit__(self, *args):

        # restore cached copy
        self.__dict__.update(self.__cache.copy())
        del self.__cache

    def __getattribute__(self, key):
        if key in object.__getattribute__(self, '__attrs__'):
            try:
                return object.__getattribute__(self, key)
            except AttributeError:
                return None
        return object.__getattribute__(self, key)


settings = Settings()
settings.debug = False
settings.cookies = None
settings.username = None
settings.password = None
settings.account_id = None
settings.requests_config = {}

account_url = 'https://my.rightscale.com/api/acct/'
