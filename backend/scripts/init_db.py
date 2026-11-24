"""Database Initialization Script"""
import sys
from backend.core.database import engine, Base
from backend.models import *
from backend.core.logging import logger


def init_database():
    logger.info("Initializing database schema...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables verified and created successfully.")

if __name__ == "__main__":
    init_database()
