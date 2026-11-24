"""API Dependencies"""
from typing import Generator
from fastapi import Depends
from sqlalchemy.orm import Session
from backend.core.database import get_db

DbSession = Depends(get_db)
