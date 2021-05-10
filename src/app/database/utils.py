import sqlalchemy
from contextlib import contextmanager
from . import _base, _engines, _sessions
# The models module need to be import before create_all
from .models import *


__all__ = [
    'session_scope',
    'init_database',
    'describe_table'
]


@contextmanager
def session_scope(db='default'):
    session = _sessions.get(db)()
    try:
        yield session
        session.commit()
    except:
        session.rollback()
        raise
    finally:
        session.close()


def init_database(db='default', drop_all=False):
    engine = _engines.get(db)
    if drop_all:
        _base.metadata.drop_all(engine)
    _base.metadata.create_all(engine)


def describe_table(table, db='default'):
    engine = _engines.get(db)
    assert engine.has_table(table), "Table not exists"
    inspect = sqlalchemy.inspect(engine)
    return {
        'columns': inspect.get_columns(table),
        'check_constraints': inspect.get_check_constraints(table),
        'foreign_keys': inspect.get_foreign_keys(table),
        'indexes': inspect.get_indexes(table),
        'pk_constraint': inspect.get_pk_constraint(table),
        'primary_keys': inspect.get_primary_keys(table),
        'table_comment': inspect.get_table_comment(table),
    }
