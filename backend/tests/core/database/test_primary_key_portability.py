import pytest
from sqlalchemy.dialects import postgresql, sqlite

from app.models import Task, User

MODELS = [User, Task]


@pytest.mark.parametrize("model", MODELS)
def test_primary_key_is_sqlite_rowid_alias(model):
    """SQLite autoincrements only INTEGER PRIMARY KEY columns."""
    compiled = model.__table__.c.id.type.compile(dialect=sqlite.dialect())
    assert compiled == "INTEGER"


@pytest.mark.parametrize("model", MODELS)
def test_primary_key_stays_bigint_on_postgres(model):
    compiled = model.__table__.c.id.type.compile(dialect=postgresql.dialect())
    assert compiled == "BIGINT"


def test_task_author_foreign_key_matches_user_pk_on_both_dialects():
    for dialect in (sqlite.dialect(), postgresql.dialect()):
        assert Task.__table__.c.task_author_id.type.compile(
            dialect=dialect
        ) == User.__table__.c.id.type.compile(dialect=dialect)
