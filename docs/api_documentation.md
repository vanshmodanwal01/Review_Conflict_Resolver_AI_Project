# API Documentation: Review Conflict Resolver

## 1. API Architecture Overview

The Review Conflict Resolver API is built with FastAPI and conforms to RESTful best practices. All responses are JSON-encoded and validated via Pydantic v2 schemas.

- **Base URL**: `/api/v1`
- **Interactive Documentation**:
  - Swagger UI: `http://localhost:8000/docs`
  - ReDoc: `http://localhost:8000/redoc`

---

## 2. API Endpoints

### 2.1 Product Discovery
#### `POST /api/v1/products/search`
Searches product catalog across permitted sources by keywords or filters.
- **Request Body**:
  ```json
  {
    "query": "Dell XPS 15",
    "category": "laptops",
    "limit": 10
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "results": [
      {
        "id": "c1f7a28e-5d1b-4f9e-9d8a-3e2c1a4b5c6d",
        "title": "Dell XPS 15 (9530) Intel Core i7 13th Gen",
        "brand": "Dell",
        "category": "laptops",
        "review_count": 254,
        "average_rating": 4.1,
        "available_sources": ["Curated Verified Dataset", "Amazon"]
      }
    ]
  }
  ```

#### `GET /api/v1/products/{product_id}`
Retrieves detailed product metadata, including specifications and known variants.

---

### 2.2 Review Ingestion & Analysis Lifecycle
#### `POST /api/v1/analysis/{product_id}`
Initiates asynchronous or synchronous review collection and conflict analysis.
- **Request Body**:
  ```json
  {
    "force_refresh": false,
    "provider_preference": "all"
  }
  ```
- **Response**: `202 Accepted`
  ```json
  {
    "job_id": "7b8a1c9e-...",
    "status": "processing",
    "message": "Analysis started for Dell XPS 15"
  }
  ```

#### `GET /api/v1/analysis/{job_id}`
Polls or monitors job status.
- **Response**:
  ```json
  {
    "job_id": "7b8a1c9e-...",
    "status": "completed",
    "progress_percent": 100,
    "processed_reviews": 150,
    "detected_conflicts": 3
  }
  ```

---

### 2.3 Conflict Resolution & Deep Dive
#### `GET /api/v1/conflicts/{product_id}`
Returns all detected conflict groups for the specified product.
- **Response**: `200 OK`
  ```json
  {
    "product_id": "c1f7a28e-...",
    "total_conflicts": 3,
    "conflicts": [
      {
        "conflict_id": "f8a2-...",
        "aspect": "battery",
        "conflict_score": 0.88,
        "positive_count": 78,
        "negative_count": 64,
        "status": "resolved_with_explanation",
        "headline": "Significant divergence in battery longevity reported."
      }
    ]
  }
  ```

#### `GET /api/v1/conflicts/details/{conflict_id}`
Retrieves complete forensic breakdown of a single conflict, including contextual divergence, cited review evidence, and AI synthesis.
- **Response**: `200 OK`
  ```json
  {
    "conflict_id": "f8a2-...",
    "aspect": "battery",
    "explanation": {
      "summary": "Customer opinions diverge dramatically based on display type and task intensity.",
      "contributing_factors": [
        "4K OLED display variant drains 40% more power than FHD+ IPS display.",
        "Heavy software compilation and gaming drops battery to ~3.5 hours, whereas office streaming yields 8-10 hours."
      ],
      "supporting_evidence": [
        {
          "review_id": "r101",
          "text": "Battery backup is excellent. It lasts almost 10 hours during my office meetings.",
          "variant": "FHD+ / Core i7",
          "context": "Office Productivity (Low Intensity)"
        }
      ],
      "opposing_evidence": [
        {
          "review_id": "r102",
          "text": "Battery performance is terrible. It barely lasts 3 hours on a single charge.",
          "variant": "4K OLED / RTX 4060",
          "context": "Video Editing / Gaming (High Intensity)"
        }
      ],
      "confidence_level": 0.92,
      "missing_information": "Ambient screen brightness settings were not consistently reported across all reviewers."
    }
  }
  ```

---

### 2.4 Personalized User Consultation
#### `POST /api/v1/insights/personalized`
Receives customer's planned workload and configuration preferences, then returns tailored risk and expectation guidance.
- **Request Body**:
  ```json
  {
    "product_id": "c1f7a28e-...",
    "target_variant": "16GB RAM, 4K OLED",
    "intended_use_case": "video_editing",
    "usage_intensity": "high",
    "priority_aspects": ["battery", "thermals_and_noise"]
  }
  ```
- **Response**: `200 OK`
  ```json
  {
    "advisory_summary": "Expect battery life closer to the lower tier (3 to 4 hours) due to 4K OLED and video rendering workload.",
    "aspect_advisories": [
      {
        "aspect": "battery",
        "predicted_experience": "Below average endurance",
        "relevant_conflict_warning": "High conflict detected: 4K OLED panel combined with high rendering intensity severely accelerates battery drain."
      }
    ]
  }
  ```
