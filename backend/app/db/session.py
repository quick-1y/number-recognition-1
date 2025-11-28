from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()
url = make_url(settings.database_url)
connect_args: dict = {}

if url.get_backend_name() == "sqlite":
    if url.database:
        Path(url.database).parent.mkdir(parents=True, exist_ok=True)
    connect_args["check_same_thread"] = False

engine = create_engine(settings.database_url, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
