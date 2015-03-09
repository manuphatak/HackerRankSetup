# coding=utf-8
import ConfigParser
import click
import logging
import pkg_resources
import os.path

# Setup
import requests
import hackerranksetup.HackerRankReadme as HRReadme

CONFIG_FILE = pkg_resources.resource_stream(__name__, 'config/config.cfg')
CONTEXT_SETTINGS = dict(help_option_names=['-h', '--help'])

self_dir = os.path.dirname(os.path.realpath(__file__))
logfile = os.path.join(self_dir, 'logs', 'hackerranksetup.log')

logging.basicConfig(filename=logfile, filemode='w', level=logging.INFO)
logging.getLogger('requests').setLevel(logging.WARNING)


# App
@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug', '-D', is_flag=True, default=False,
              help='Turn debug mode on.')
@click.pass_context
def cli(ctx, debug):
    """HackerRank IDE setup utility."""
    ctx.obj = {}
    config = ConfigParser.SafeConfigParser()
    config.readfp(CONFIG_FILE)

    if debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.getLogger('requests').setLevel(logging.INFO)
        logging.getLogger().addHandler(logging.StreamHandler())
        logging.info('Debug On')
        for section in config.sections():
            logging.debug('section:%s', section)
            for option in config.options(section):
                logging.debug('%s:%s', option, config.get(section, option))

    ctx.obj['root'] = os.path.realpath(
        os.path.expanduser(config.get('HackerRank', 'Root')))
    ctx.obj['workspace'] = os.path.realpath(
        os.path.expanduser(config.get('HackerRank', 'Workspace')))
    ctx.obj['assets'] = os.path.realpath(
        os.path.expanduser(config.get('HackerRank', 'Assets')))


@cli.command()
@click.argument('url')
@click.pass_context
def set(ctx, url):
    """Setup new workspace."""

    logging.info('set:%s', url)
    logging.debug('ctx.obj:%s', ctx.obj)

    try:
        hrm = HRReadme.HackerRankReadme(url, root=ctx.obj['root'],
                                        workspace=ctx.obj['workspace'],
                                        assets=ctx.obj['assets'])
        output = hrm.save_source().save_readme()
    except (requests.HTTPError, ValueError), e:
        logging.error("Requests Error:%s", e)
        ctx.fail('Must be valid HackerRank challenge URL')
    else:
        logging.info('Readme created at %s', hrm.workspace)
        logging.debug('Readme Output:\n%s', output)


@cli.command()
@click.pass_obj
def publish(obj):
    """Publish current puzzle."""
    click.echo('Publish!')


if __name__ == '__main__':
    cli()
