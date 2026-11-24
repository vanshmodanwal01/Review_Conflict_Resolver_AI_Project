"""Seed Database with Authentic Laptop Conflict Datasets"""
import asyncio
from backend.core.database import SessionLocal, engine, Base
from backend.models import Product, ProductVariant, Review, ReviewSource
from backend.collectors.curated_dataset import SAMPLE_LAPTOP_REVIEWS, CuratedDatasetCollector
from backend.services.review_service import ReviewService
from backend.services.analysis_service import analysis_service
from backend.core.logging import logger


async def seed_laptop_data():
    print("Initializing database schema...", flush=True)
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    collector = CuratedDatasetCollector()
    source = ReviewService.get_or_create_source(db, collector.source_name, collector.base_url)

    print(f"Seeding {len(SAMPLE_LAPTOP_REVIEWS)} reference laptop conflict profiles...", flush=True)
    seeded_product_ids = []

    for item in SAMPLE_LAPTOP_REVIEWS:
        # Check if product already exists
        existing = db.query(Product).filter(Product.model_number == item["external_product_id"]).first()
        if existing:
            logger.info(f"Product '{item['product_name']}' already exists.")
            seeded_product_ids.append(existing.id)
            continue

        product = Product(
            title=item["product_name"],
            brand=item["brand"],
            category=item["specs"].get("category", "laptops"),
            model_number=item["external_product_id"],
            specifications=item["specs"],
            average_rating=round(sum(r["rating"] for r in item["reviews"]) / len(item["reviews"]), 2),
            total_reviews=len(item["reviews"])
        )
        db.add(product)
        db.flush()

        # Add variants
        variant_cache = {}
        for var_name in item["specs"].get("variants", []):
            pv = ProductVariant(
                product_id=product.id,
                raw_variant_string=var_name
            )
            db.add(pv)
            db.flush()
            variant_cache[var_name] = pv.id

        # Add reviews
        for r in item["reviews"]:
            rev = Review(
                product_id=product.id,
                source_id=source.id,
                rating=r["rating"],
                title=f"Review for {item['product_name']}",
                review_text=r["review_text"],
                reviewer_name=r.get("reviewer_name"),
                verified_purchase=r.get("verified_purchase", True)
            )
            # Link variant if matches
            if r.get("variant") in variant_cache:
                rev.variant_id = variant_cache[r.get("variant")]
            db.add(rev)

        db.commit()
        seeded_product_ids.append(product.id)
        logger.info(f"Seeded '{product.title}' with {len(item['reviews'])} authentic reviews.")

    # Run initial analysis on all seeded products
    logger.info("Running baseline AI analysis and conflict detection on seeded products...")
    for pid in seeded_product_ids:
        try:
            await analysis_service.process_product_analysis(db, pid, force_refresh=True)
        except Exception as e:
            logger.error(f"Error during baseline analysis for product {pid}: {e}")

    db.close()
    logger.info("Seeding and conflict analysis complete.")

if __name__ == "__main__":
    asyncio.run(seed_laptop_data())
