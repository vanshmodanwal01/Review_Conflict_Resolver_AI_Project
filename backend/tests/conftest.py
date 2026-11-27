"""Pytest Fixtures and Test Setup"""
import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

# Use a concrete SQLite file for testing to ensure all connections share state
TEST_DB_FILE = os.path.abspath(os.path.join(os.path.dirname(__file__), "test_app.db"))
TEST_DATABASE_URL = f"sqlite:///{TEST_DB_FILE}"

os.environ["ENVIRONMENT"] = "test"
os.environ["DATABASE_URL"] = TEST_DATABASE_URL

from backend.core.config import settings
settings.ENVIRONMENT = "test"
settings.DATABASE_URL = TEST_DATABASE_URL

# Disable heavy local transformers in tests
import backend.ai.embedding_service as emb_mod
emb_mod._st_model = False

from backend.core.database import Base, get_db
from backend.models import Product, ProductVariant, Review, ReviewSource, ConflictGroup, ConflictEvidence
from backend.main import app

test_engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Initializes schema and seeds baseline test fixtures."""
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)
    
    db = TestingSessionLocal()
    
    # 1. Source
    source = ReviewSource(name="Curated Dataset", base_url="https://curated.internal")
    db.add(source)
    db.flush()

    # 2. Product
    product = Product(
        title="Dell XPS 15 9530 (OLED)",
        brand="Dell",
        category="laptops",
        model_number="XPS-9530-OLED",
        specifications={"category": "laptops", "processor": "Intel Core i7-13700H"},
        average_rating=4.2,
        total_reviews=2
    )
    db.add(product)
    db.flush()

    # 3. Reviews
    r1 = Review(
        product_id=product.id,
        source_id=source.id,
        rating=5.0,
        title="Phenomenal battery",
        review_text="Battery lasts 10 hours easily during office work and light browsing.",
        verified_purchase=True
    )
    r2 = Review(
        product_id=product.id,
        source_id=source.id,
        rating=2.0,
        title="Terrible battery life",
        review_text="Battery barely lasts 3 hours under heavy 4K video editing and gaming.",
        verified_purchase=True
    )
    db.add_all([r1, r2])
    db.flush()

    # 4. Conflict Group
    conflict = ConflictGroup(
        product_id=product.id,
        aspect_category="battery",
        conflict_score=0.85,
        status="detected",
        positive_review_count=1,
        negative_review_count=1,
        headline="Customers report conflicting battery life between 3 and 10 hours."
    )
    db.add(conflict)
    db.flush()

    # 5. Evidence
    ev1 = ConflictEvidence(
        conflict_group_id=conflict.id,
        review_id=r1.id,
        stance="positive",
        excerpt="Battery lasts 10 hours easily during office work.",
        relevance_weight=0.9,
        usage_context="office_work"
    )
    ev2 = ConflictEvidence(
        conflict_group_id=conflict.id,
        review_id=r2.id,
        stance="negative",
        excerpt="Battery barely lasts 3 hours under heavy 4K video editing.",
        relevance_weight=0.95,
        usage_context="content_creation"
    )
    db.add_all([ev1, ev2])
    db.commit()
    db.close()

    yield

    Base.metadata.drop_all(bind=test_engine)
    if os.path.exists(TEST_DB_FILE):
        try:
            os.remove(TEST_DB_FILE)
        except Exception:
            pass


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c
