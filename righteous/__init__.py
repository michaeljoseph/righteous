__version__ = '0.2.1'
__author__ = 'Michael Joseph'

from .api import (
    init, login,
    list_servers, find_server, server_info, server_settings,
    create_and_start_server, create_server, set_server_parameters,
    start_server, stop_server, delete_server,
)

hush_pyflakes = (init, login, list_servers, find_server, server_info,
    server_settings, create_and_start_server, create_server,
    set_server_parameters, start_server, stop_server, delete_server
)
