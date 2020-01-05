class Config:
    DEBUG = True


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
