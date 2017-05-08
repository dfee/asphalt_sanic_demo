from typing import Optional

import click
from ruamel import yaml

from asphalt.core.runner import run_application, policies
from asphalt.core.utils import merge_config


@click.command(
    help='Read one or more configuration files and start the application.',
)
@click.argument(
    'service',
    required=True,
    type=str,
)
@click.argument(
    'configfile',
    type=click.File(),
    nargs=-1,
    required=True,
)
@click.option(
    '--unsafe',
    is_flag=True,
    default=False,
    help='use unsafe mode when loading YAML (enables markup extensions)',
)
@click.option(
    '-l',
    '--loop',
    type=click.Choice(policies.names),
    help='alternate event loop policy',
)
def road(configfile, service: str, unsafe: bool, loop: Optional[str]):
    # Read the configuration from the supplied YAML files
    config = {}
    for path in configfile:
        config_data = yaml.load(path) if unsafe else yaml.safe_load(path)
        assert isinstance(config_data, dict), \
            'the document root element must be a dictionary'
        config = merge_config(config, config_data)

    # Override the event loop policy if specified
    if loop:
        config['event_loop_policy'] = loop

    kwargs = {
        k: v for k, v in config.items()
        if k in ['logging', 'event_loop_policy', 'max_threads', 'start_timeout']
    }
    # Start the application
    run_application(component=config[service], **kwargs)
