__version__ = '0.3.0'
__author__ = 'Michael Joseph'

from .api import (
    init, login,
    list_servers, find_server, server_info, server_settings,
    create_and_start_server, create_server, set_server_parameters,
    start_server, stop_server, delete_server, list_server_templates,
    server_template_info, create_server_template, delete_server_template
)

hush_pyflakes = (init, login, list_servers, find_server, server_info,
    server_settings, create_and_start_server, create_server,
    set_server_parameters, start_server, stop_server, delete_server,
    list_server_templates, server_template_info, create_server_template,
    delete_server_template
)
