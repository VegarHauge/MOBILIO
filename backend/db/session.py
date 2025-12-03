from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from core.config import settings

DATABASE_URL = settings.DATABASE_URL

# For SQLite, connect_args is needed
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL, 
        connect_args={"check_same_thread": False},
        echo=settings.database_echo  # Log SQL queries in debug mode
    )
else:
    engine = create_engine(
        DATABASE_URL,
        echo=settings.database_echo
    )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)