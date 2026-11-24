"""End-to-End System Health and Integrity Verification Script"""
import sys
import asyncio
from backend.core.database import SessionLocal, Base, engine
from backend.models import Product, Review, ConflictGroup
from backend.ai.preprocessing import preprocessor
from backend.ai.aspect_extractor import aspect_extractor
from backend.ai.context_extractor import context_extractor
from backend.ai.embedding_service import embedding_service
from backend.ai.conflict_engine import conflict_engine
from backend.services.analysis_service import analysis_service
from backend.core.logging import logger


async def run_system_verification():
    logger.info("==================================================")
    logger.info("REVIEW CONFLICT RESOLVER - SYSTEM INTEGRITY CHECK")
    logger.info("==================================================")

    # 1. Database Check
    logger.info("[1/7] Testing Database Connection...")
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    logger.info("✔ Database connected and schema verified.")

    # 2. Text Preprocessor Check
    logger.info("[2/7] Testing Text Sanitization & Segmentation...")
    sample_text = "Battery backup is excellent! Lasts 10 hours. <script>alert(1)</script> https://example.com"
    cleaned = preprocessor.clean_text(sample_text)
    assert "<script>" not in cleaned, "HTML tag was not removed!"
    assert "https://" not in cleaned, "URL was not removed!"
    segments = preprocessor.segment_sentences(sample_text)
    assert len(segments) >= 2, "Sentence segmentation failed!"
    logger.info(f"✔ Preprocessor passed ({len(segments)} segments extracted).")

    # 3. ABSA Aspect-Based Sentiment Check
    logger.info("[3/7] Testing Aspect-Based Sentiment Analysis...")
    sample_review = "The laptop performs excellently with fast speed, but battery backup is disappointing and drains quickly."
    aspects = aspect_extractor.extract_aspects(sample_review)
    assert len(aspects) >= 2, f"Expected at least 2 aspects, got {len(aspects)}"
    aspect_names = {a["aspect_category"] for a in aspects}
    assert "battery" in aspect_names, "Battery aspect was not detected!"
    assert "performance" in aspect_names, "Performance aspect was not detected!"
    
    battery_asp = next(a for a in aspects if a["aspect_category"] == "battery")
    assert battery_asp["sentiment"] == "negative", f"Expected negative battery sentiment, got {battery_asp['sentiment']}"
    perf_asp = next(a for a in aspects if a["aspect_category"] == "performance")
    assert perf_asp["sentiment"] == "positive", f"Expected positive performance sentiment, got {perf_asp['sentiment']}"
    logger.info(f"✔ ABSA passed: correctly split positive performance and negative battery.")

    # 4. Context Extraction Check
    logger.info("[4/7] Testing Context & Workload Extraction...")
    ctx = context_extractor.extract_context(
        "I use this for 4K video editing in Premiere Pro with 32GB RAM on my desk.",
        declared_variant="32GB RAM / RTX 4060"
    )
    assert ctx["primary_use_case"] == "content_creation", f"Expected content_creation, got {ctx['primary_use_case']}"
    assert ctx["usage_intensity"] == "high", f"Expected high intensity, got {ctx['usage_intensity']}"
    assert ctx["certainty"] == "explicit", f"Expected explicit certainty, got {ctx['certainty']}"
    logger.info(f"✔ Context extractor passed ({ctx['primary_use_case']}, {ctx['usage_intensity']} intensity).")

    # 5. Embedding Vector Check
    logger.info("[5/7] Testing Dense Vector Embeddings...")
    vec1 = embedding_service.embed_text("Battery life lasts 10 hours during web browsing.")
    vec2 = embedding_service.embed_text("Battery backup is amazing and holds charge all day.")
    vec3 = embedding_service.embed_text("The keyboard keycaps feel cheap and squeaky.")
    assert len(vec1) == 384, f"Vector dimension must be 384, got {len(vec1)}"
    sim_similar = embedding_service.cosine_similarity(vec1, vec2)
    sim_different = embedding_service.cosine_similarity(vec1, vec3)
    logger.info(f"Cosine Similarity (Battery vs Battery): {sim_similar:.3f}")
    logger.info(f"Cosine Similarity (Battery vs Keyboard): {sim_different:.3f}")
    logger.info("✔ Embedding engine passed.")

    # 6. Conflict Engine Check
    logger.info("[6/7] Testing Conflict Detection on Contradictory Cohorts...")
    mock_reviews = [
        {
            "id": "r1",
            "rating": 5.0,
            "review_text": "Battery backup is fantastic, lasts 10 hours during office meetings.",
            "variant": "FHD+ Display / 16GB RAM",
            "context": {"usage_intensity": "low", "primary_use_case": "office_work"},
            "aspects": [{"id": "a1", "aspect_category": "battery", "sentiment": "positive", "sentiment_score": 0.9, "evidence_snippet": "Battery backup is fantastic"}]
        },
        {
            "id": "r2",
            "rating": 1.0,
            "review_text": "Battery performance is terrible, dies in 2 hours while gaming on 4K OLED.",
            "variant": "4K OLED Display / 32GB RAM",
            "context": {"usage_intensity": "high", "primary_use_case": "gaming"},
            "aspects": [{"id": "a2", "aspect_category": "battery", "sentiment": "negative", "sentiment_score": -0.9, "evidence_snippet": "Battery performance is terrible"}]
        }
    ]
    conflicts = conflict_engine.detect_conflicts("test-prod", mock_reviews)
    assert len(conflicts) == 1, f"Expected 1 conflict detected, got {len(conflicts)}"
    assert conflicts[0]["aspect_category"] == "battery"
    assert conflicts[0]["conflict_score"] > 0.5
    assert conflicts[0]["divergence_analysis"]["has_contextual_divergence"] is True
    logger.info(f"✔ Conflict Engine passed: Score={conflicts[0]['conflict_score']}, Aspect={conflicts[0]['aspect_category']}.")

    # 7. Database Counts Check
    logger.info("[7/7] Checking Seeded Product Counts...")
    p_count = db.query(Product).count()
    r_count = db.query(Review).count()
    c_count = db.query(ConflictGroup).count()
    logger.info(f"Products in DB: {p_count} | Reviews in DB: {r_count} | Detected Conflicts: {c_count}")
    logger.info("✔ All system verification checks completed successfully!")
    db.close()

if __name__ == "__main__":
    asyncio.run(run_system_verification())
