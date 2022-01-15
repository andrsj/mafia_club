import os

import sqlalchemy as sa
from alembic import context

from dim_mafii.adapters import orm


def get_postgres_url(env):
    return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(**get_postgres_config_test(env))


def get_postgres_config(env):
    return {
        'host': env.get('DB_HOST', 'localhost'),
        'port': env.get('DB_PORT', 5432),
        'user': env.get('SECRET_DB_USER', 'dim_mafii'),
        'password': env.get('SECRET_DB_PASSWORD', 'dim_mafii'),
        'db_name': env.get('DB_NAME', 'dim_mafii'),
    }

def get_postgres_config_test(env):
    return {
        'host': env.get('DB_HOST', 'localhost'),
        'port': env.get('DB_PORT', 5432),
        'user': env.get('SECRET_DB_USER', 'test_zlo'),
        'password': env.get('SECRET_DB_PASSWORD', 'test_zlo'),
        'db_name': env.get('DB_NAME', 'test_zlo'),
    }

def get_current_metadata(env):
    dal = orm.make_sqlalchemy(get_postgres_url(env))
    return dal.configure_mappings()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    postgres_url = get_postgres_url(os.environ)
    engine = sa.create_engine(postgres_url)
    metadata = get_current_metadata(os.environ)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=metadata
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
