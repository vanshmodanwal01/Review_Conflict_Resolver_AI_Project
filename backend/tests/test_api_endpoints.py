"""Tests for FastAPI Endpoints"""


def test_health_endpoint(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Review Conflict Resolver" in data["app"]


def test_product_search_and_listing(client):
    # Search
    response = client.post("/api/v1/products/search", json={"query": "Dell XPS", "limit": 5})
    assert response.status_code == 200
    results = response.json()
    assert len(results) >= 1
    prod_id = results[0]["id"]

    # Get Single Product
    get_res = client.get(f"/api/v1/products/{prod_id}")
    assert get_res.status_code == 200
    assert get_res.json()["id"] == prod_id


def test_review_retrieval_and_conflicts(client):
    # Search product
    search_res = client.post("/api/v1/products/search", json={"query": "Dell XPS", "limit": 1})
    prod_id = search_res.json()[0]["id"]

    # Fetch reviews
    rev_res = client.get(f"/api/v1/reviews/{prod_id}")
    assert rev_res.status_code == 200
    reviews = rev_res.json()
    assert len(reviews) >= 1

    # Fetch conflicts
    conflict_res = client.get(f"/api/v1/conflicts/{prod_id}")
    assert conflict_res.status_code == 200


def test_personalized_insight_advisory(client):
    search_res = client.post("/api/v1/products/search", json={"query": "Dell XPS", "limit": 1})
    prod_id = search_res.json()[0]["id"]

    payload = {
        "product_id": prod_id,
        "target_variant": "32GB RAM / 3.5K OLED",
        "intended_use_case": "content_creation",
        "usage_intensity": "high",
        "priority_aspects": ["battery", "thermals_and_noise"]
    }
    insight_res = client.post("/api/v1/insights/personalized", json=payload)
    assert insight_res.status_code == 200
    data = insight_res.json()
    assert "advisory_summary" in data
    assert len(data["aspect_advisories"]) >= 1
