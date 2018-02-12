"""Internal helper functions"""

import os.path
import datetime
from configparser import ConfigParser
from subprocess import check_output

import click
from click import MissingParameter

PKG_DIR = os.path.abspath(os.path.dirname(__file__))
TEMPLATES_DIR = os.path.join(PKG_DIR, 'templates')


def _get_username():
    try:
        name = check_output(
            ['git', 'config', '--get', 'user.name']).decode()[:-1]
    except:
        name = ''

    return name


def _get_usermail():
    try:
        email = check_output(
            ['git', 'config', '--get', 'user.email']).decode()[:-1]
    except:
        email = ''

    return email


def _check_riotbase(path):
    """Check the given path is a valid RIOTBASE directory."""
    coc = os.path.join(os.path.expanduser(path), 'CODE_OF_CONDUCT.md')
    if os.path.isfile(coc):
        first_line = open(coc, 'r').readline()[:-1]
        if first_line == 'RIOT-OS Code of Conduct':
            return path
    raise MissingParameter(param_type='RIOT base directory')


def _check_common_params(params):
    if 'year' not in params:
        params['year'] = datetime.datetime.now().year
    if 'author_name' not in params:
        params['author_name'] = _get_username()
    if 'author_email' not in params:
        params['author_email'] = _get_usermail()
    if 'organization' not in params:
        params['organization'] = _get_username()
    if 'riotbase' not in params:
        params['riotbase'] = ''
    params['riotbase'] = _check_riotbase(params['riotbase'])


def _prompt_common_information():
    params = {}
    params['year'] = datetime.datetime.now().year
    params['author_name'] = click.prompt(
        text='Author name', default=_get_username())
    params['author_email'] = click.prompt(
        text='Author email', default=_get_usermail())
    params['organization'] = click.prompt(
        text='Organization', default=_get_username())
    params['riotbase'] = click.prompt(
        text='RIOT base directory', value_proc=_check_riotbase)
    return params


def _read_config(filename, section=None):
    parser = ConfigParser()
    parser.readfp(filename)
    config = dict(parser.items('common'))
    if section is not None:
        config.update(dict(parser.items(section)))
    return config


def _read_board_config(filename):
    return _read_config(filename, section='board')


def _read_driver_config(filename):
    return _read_config(filename, section='driver')
