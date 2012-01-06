# coding: utf-8

"""
righteous.config


Settings object, lifted from https://github.com/kennethreitz/requests
"""

from requests.config import Settings

class RighteousSettings(Settings):
    pass


settings = RighteousSettings()
settings.debug = False
settings.cookies = None
settings.username = None
settings.password = None
settings.account_id = None
