def setup_env_with_test_database(env):
    env['DB_HOST'] = 'localhost'
    env['DB_PORT'] = '5432'
    env['SECRET_DB_USER'] = 'test_zlo'
    env['SECRET_DB_PASSWORD'] = 'test_zlo'
    env['DB_NAME'] = 'test_zlo'
