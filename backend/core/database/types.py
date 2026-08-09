from sqlalchemy import BigInteger, Integer

# SQLite only auto-generates primary keys for columns declared exactly as
# ``INTEGER PRIMARY KEY`` (the rowid alias). A ``BIGINT PRIMARY KEY`` column is
# not a rowid alias, so inserts without an explicit id fail with
# "NOT NULL constraint failed". Rendering INTEGER on SQLite keeps the test
# database usable while PostgreSQL still gets BIGINT/BIGSERIAL.
BigIntPk = BigInteger().with_variant(Integer, "sqlite")

__all__ = ["BigIntPk"]
