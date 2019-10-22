import os

import sqlalchemy as sa
from alembic import context


def get_postgres_url(env):
    return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(**get_postgres_config(env))


def get_postgres_config(env):
    return {
        'host': env.get('DB_HOST', 'localhost'),
        'port': env.get('DB_PORT', 5432),
        'user': env.get('SECRET_DB_USER', 'zlo'),
        'password': env.get('SECRET_DB_PASSWORD', 'zlo'),
        'db_name': env.get('DB_NAME', 'zlo'),
    }


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    postgres_url = get_postgres_url(os.environ)
    engine = sa.create_engine(postgres_url)
    metadata = sa.MetaData(engine)

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=metadata
        )

        with context.begin_transaction():
            context.run_migrations()


run_migrations_online()
