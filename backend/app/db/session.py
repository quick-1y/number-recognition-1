from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.engine.url import make_url
from sqlalchemy.orm import sessionmaker

from app.core.config import get_settings

settings = get_settings()
url = make_url(settings.database_url)
connect_args: dict = {}

project_root = Path(__file__).resolve().parents[2]

if url.get_backend_name() == "sqlite":
    if url.database:
        db_path = Path(url.database)
        if not db_path.is_absolute():
            db_path = (project_root / db_path).resolve()
        db_path.parent.mkdir(parents=True, exist_ok=True)
        url = url.set(database=str(db_path))
    connect_args["check_same_thread"] = False

engine = create_engine(url, pool_pre_ping=True, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
