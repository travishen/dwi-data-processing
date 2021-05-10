from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from .. import settings

_base = declarative_base()
_engines = dict()
_sessions = dict()


def get_connection_string(engine, user, password, host, port, name, **options):
    conn = None
    if engine == 'postgresql':
        conn = f"postgresql://{user}:{password}@{host}:{port}/{name}"
    if options:
        conn += '?'
        for key, value in options.items():
            conn += f'{key}={value}'
    if not conn:
        raise NotImplementedError('Engine type not supported.')
    return conn


for db, settings in settings.DATABASES.items():
    extra_config = dict()
    connection_string = get_connection_string(
        engine=settings['ENGINE'],
        host=settings['HOST'],
        name=settings['NAME'],
        port=settings['PORT'],
        user=settings['USER'],
        password=settings['PASSWORD'],
        **settings['OPTIONS']
    )
    engine = create_engine(connection_string, **extra_config)
    session = scoped_session(sessionmaker())
    session.configure(bind=engine)
    _engines[db] = engine
    _sessions[db] = session
