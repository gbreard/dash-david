import os

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

# En local usa SQLite. En Koyeb, la variable DATABASE_URL apunta al Postgres gratis.
# Koyeb provee DATABASE_URL automáticamente al vincular el servicio con la DB.
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///data.db")

# PostgreSQL en Koyeb puede venir con "postgres://" en vez de "postgresql://"
# SQLAlchemy 2.x necesita "postgresql://"
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    pass
