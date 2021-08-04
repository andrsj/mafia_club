import os
import logging
import sys

from alembic.config import Config
import alembic.command

logger = logging.getLogger()
logger.setLevel(logging.INFO)


def dump_env_vars(env):
    logging.info('Environment variables (non-password)')

    for key, value in env.items():
        if key.startswith('SECRET'):
            continue
        logging.info(f'{key}: {value}')


def lambda_handler(event, context):
    logging.info('Running alembic migration for ZLO DB...')

    dump_env_vars(os.environ)

    try:
        config = Config('alembic.ini')
        config.attributes['configure_logger'] = False

        alembic.command.upgrade(config, 'head')
        result = 'success'
    except Exception:
        logging.exception(f'Error during alembic migration')
        sys.exit(1)

    return result


if __name__ == '__main__':
    lambda_handler(None, None)
