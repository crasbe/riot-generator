"""RIOT pkg generator module."""

import os

import click
from click import MissingParameter

from .common import render_source, render_file
from .common import prompt_common_information, check_common_params
from .utils import read_config, parse_list_option


def _read_pkg_config(filename):
    """Read the pkg specific configuration file."""
    params = read_config(filename, section='pkg')
    if 'name' not in params or not params['name']:
        raise MissingParameter(param_type='package name')
    if 'displayed_name' not in params or not params['displayed_name']:
        raise MissingParameter(param_type='package displayed name')
    if 'url' not in params or not params['url']:
        raise MissingParameter(param_type='package source url')
    if 'hash' not in params or not params['hash']:
        raise MissingParameter(param_type='package version hash')
    if 'license' not in params or not params['license']:
        raise MissingParameter(param_type='package license')
    if 'description' not in params:
        params['description'] = ''
    for param in ['modules', 'packages', 'features']:
        if param not in params:
            params[param] = ''
        else:
            params[param] = parse_list_option(params[param])
    return params


def _prompt_pkg_params():
    """Request pkg specific variables."""
    params = {}
    params['name'] = click.prompt(text='Package name (no space)')
    params['displayed_name'] = click.prompt(
        text='Package displayed name (for doxygen documentation)')
    params['url'] = click.prompt(text='Package source url')
    params['hash'] = click.prompt(text='Package version hash')
    params['license'] = click.prompt(text='Package license')
    params['description'] = click.prompt(text='Package short description')
    params['modules'] = click.prompt(
        text='Required modules (comma separated)', default='',
        value_proc=parse_list_option)
    params['packages'] = click.prompt(
        text='Required packages (comma separated)', default='',
        value_proc=parse_list_option)
    params['features'] = click.prompt(
        text='Required board features (comma separated)', default='',
        value_proc=parse_list_option)

    params.update(prompt_common_information())
    return params


def _check_pkg_params(params):
    test_name = params['name'].replace(' ', '_')
    params['name'] = test_name


def generate_pkg(config=None):
    # Start wizard if config is not set
    if config is None:
        params = _prompt_pkg_params()
    else:
        params = _read_pkg_config(config)
    _check_pkg_params(params)
    check_common_params(params)

    pkgs_dir = os.path.join(os.path.expanduser(params['riotbase']), 'pkg')
    pkg_dir = os.path.join(pkgs_dir, params['name'])

    riotbase = os.path.abspath(os.path.expanduser(params['riotbase']))
    if os.path.abspath(os.path.curdir) == riotbase:
        output_dir = os.path.join('pkg', params['name'])
    else:
        output_dir = os.path.expanduser(pkg_dir)

    if not os.path.exists(pkg_dir):
        os.makedirs(pkg_dir)
    elif not click.prompt('\'{name}\' pkg directory already exists, '
                          'overwrite (y/N)?'.format(**params),
                          default=False, show_default=False):
        click.echo('Abort')
        return

    context = {'pkg': params}
    render_source(
        context, 'pkg',
        ['doc.txt', 'Makefile', 'Makefile.dep', 'Makefile.include'],
        output_dir
    )

    template_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), 'templates', 'pkg'
    )
    makefile_pkg_out = os.path.join(output_dir,
                                    '{}.mk'.format(params['name']))
    render_file(context, template_dir, 'pkg.mk.j2', makefile_pkg_out)

    click.echo(click.style('Package \'{name}\' generated in '
                           '{output_dir} with success!'
                           .format(name=params['name'], output_dir=output_dir),
                           bold=True))
