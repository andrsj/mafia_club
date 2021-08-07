class Config:
    DEBUG = True


def get_postgres_url(env):
    return "postgresql://{user}:{password}@{host}:{port}/{db_name}".format(**get_postgres_config(env))


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
