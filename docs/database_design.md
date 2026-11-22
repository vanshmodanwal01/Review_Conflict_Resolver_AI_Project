# Database Design: Review Conflict Resolver

## 1. Relational Architecture & Entity-Relationship Model

The Review Conflict Resolver database is designed with third normal form (3NF) principles, balanced with performance-optimized indexing and vector storage via `pgvector`.

```mermaid
erDiagram
    PRODUCTS ||--o{ PRODUCT_VARIANTS : has
    PRODUCTS ||--o{ REVIEWS : receives
    PRODUCTS ||--o{ CONFLICT_GROUPS : generates
    REVIEW_SOURCES ||--o{ REVIEWS : provides
    REVIEWS ||--o{ REVIEW_ASPECTS : contains
    REVIEWS ||--o{ REVIEW_CONTEXTS : identifies
    REVIEWS ||--o| REVIEW_EMBEDDINGS : generates
    CONFLICT_GROUPS ||--o{ CONFLICT_EVIDENCE : references
    REVIEWS ||--o{ CONFLICT_EVIDENCE : cited_in
    CONFLICT_GROUPS ||--o| AI_EXPLANATIONS : explained_by
    PRODUCTS ||--o{ ANALYSIS_JOBS : monitored_by

    PRODUCTS {
        uuid id PK
        string title
        string brand
        string category
        string model_number
        jsonb specifications
        timestamp created_at
        timestamp updated_at
    }

    PRODUCT_VARIANTS {
        uuid id PK
        uuid product_id FK
        string variant_sku
        string cpu
        string ram
        string storage
        string gpu
        string display_spec
        timestamp created_at
    }

    REVIEW_SOURCES {
        uuid id PK
        string name
        string base_url
        boolean is_active
        integer rate_limit_per_min
    }

    REVIEWS {
        uuid id PK
        uuid product_id FK
        uuid source_id FK
        uuid variant_id FK
        string external_id
        float rating
        string title
        text review_text
        string reviewer_name
        timestamp review_date
        string verified_purchase
        jsonb metadata
        timestamp created_at
    }

    REVIEW_ASPECTS {
        uuid id PK
        uuid review_id FK
        string aspect_category
        string sentiment
        float sentiment_score
        text evidence_snippet
        integer char_start
        integer char_end
    }

    REVIEW_CONTEXTS {
        uuid id PK
        uuid review_id FK
        string usage_intensity
        string primary_use_case
        string environment
        string expectation_benchmark
        string user_experience_level
        jsonb extracted_attributes
        string certainty
    }

    REVIEW_EMBEDDINGS {
        uuid id PK
        uuid review_id FK
        vector embedding
        string model_name
        timestamp created_at
    }

    CONFLICT_GROUPS {
        uuid id PK
        uuid product_id FK
        string aspect_category
        float conflict_score
        integer positive_review_count
        integer negative_review_count
        string status
        timestamp detected_at
    }

    CONFLICT_EVIDENCE {
        uuid id PK
        uuid conflict_group_id FK
        uuid review_id FK
        uuid aspect_id FK
        string stance
        float relevance_weight
        text excerpt
    }

    AI_EXPLANATIONS {
        uuid id PK
        uuid conflict_group_id FK
        string provider
        string model_name
        text summary
        text contributing_factors
        text supporting_evidence_summary
        text opposing_evidence_summary
        text missing_information
        float confidence_score
        jsonb contextual_hypotheses
        integer tokens_consumed
        timestamp created_at
    }

    ANALYSIS_JOBS {
        uuid id PK
        uuid product_id FK
        string status
        integer total_reviews
        integer processed_reviews
        string error_message
        timestamp started_at
        timestamp completed_at
    }
```

---

## 2. Table Specifications and DDL

### 2.1 Products & Variants
- `products`: Master record of product entities. Category default is `laptops` with extensible structure for `smartphones`, `headphones`, etc.
- `product_variants`: Normalized hardware and configuration variations (e.g. 16GB RAM vs 32GB RAM, OLED vs IPS screen).

### 2.2 Ingestion & Reviews
- `review_sources`: Catalog of allowed e-commerce sources (Amazon, Flipkart, Curated Dataset) with compliance settings.
- `reviews`: Immutable raw review text and external attributes. Raw reviews are **never mutated** by AI processes.

### 2.3 NLP & Granular Analysis
- `review_aspects`: Granular aspect extractions (`battery`, `thermals`, `display`, `build_quality`, `performance`, `keyboard`, `speakers`, `value_for_money`).
- `review_contexts`: Customer workload profiles, primary task domain (`gaming`, `coding`, `office_work`, `content_creation`, `casual`), environment (`air_conditioned`, `outdoor`, `high_ambient`), and benchmark expectations.
- `review_embeddings`: Dense vector representations (384-d vector) with cosine similarity indexes.

### 2.4 Conflict Resolution & Explanations
- `conflict_groups`: Discovered polarities clustered on the same aspect for the same product.
- `conflict_evidence`: Many-to-many traceable links between detected conflicts and specific review sentences.
- `ai_explanations`: Structured LLM-synthesized resolution reports, strictly grounded in review evidence.
- `analysis_jobs`: Asynchronous execution status and progress tracking for long-running analyses.

---

## 3. Indexing and Optimization Strategy

1. **Foreign Key Indexes**: Every foreign key is explicitly indexed to guarantee fast JOIN operations.
2. **Compound Filter Indexes**: `(product_id, aspect_category)` and `(aspect_category, sentiment)` for instant conflict querying.
3. **pgvector Indexing**:
   ```sql
   CREATE INDEX idx_review_embeddings_cosine
   ON review_embeddings
   USING hnsw (embedding vector_cosine_ops)
   WITH (m = 16, ef_construction = 64);
   ```
4. **Full-Text Search Indexing**: PostgreSQL `tsvector` on `reviews.review_text` and `products.title` for instant keyword lookup.
