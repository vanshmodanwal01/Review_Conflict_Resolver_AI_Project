# Review Conflict Resolver

> **AI-Powered Product Intelligence Platform for Investigating Customer Experience Disagreements.**

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111+-009688.svg?style=flat&logo=fastapi)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg?style=flat&logo=react)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5+-3178C6.svg?style=flat&logo=typescript)](https://www.typescriptlang.org)
[![Tailwind CSS](https://img.shields.io/badge/Tailwind-3+-38B2AC.svg?style=flat&logo=tailwind-css)](https://tailwindcss.com)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-16+pgvector-336791.svg?style=flat&logo=postgresql)](https://github.com/pgvector/pgvector)
[![Gemini](https://img.shields.io/badge/LLM-Google%20Gemini%20API-4285F4.svg?style=flat&logo=google)](https://ai.google.dev)

---

## Why Review Conflict Resolver?

Traditional e-commerce platforms average customer reviews into a single score (e.g. 4.1 / 5 stars) or offer shallow positive/negative sentiment summaries. When customers leave sharply contradictory reviews—such as:
- *"Battery backup is excellent, lasts almost 10 hours!"* (5 stars)
- *"Battery performance is terrible, barely lasts 3 hours!"* (1 star)

traditional tools label this as simple "mixed feedback". **Review Conflict Resolver investigates why.**

By analyzing product hardware variants (RAM, CPU, 4K OLED vs FHD displays), customer usage profiles (gaming vs office typing), environmental factors, and baseline expectations, the system resolves contradictions with verifiable, traceable review evidence—and never invents explanations when facts are insufficient.

---

## System Architecture

```
[ User Browser / Client ]
            │
            ▼
[ React 19 + TypeScript + Tailwind Dashboard ]
            │  REST / JSON
            ▼
[ FastAPI Modern Asynchronous Backend ]
            │
    ┌───────┴───────────────────────────────┐
    ▼                                       ▼
[ Data Acquisition Layer ]           [ AI / NLP Pipeline ]
  • Provider Manager (Amazon,          • Text Preprocessor & Deduplication
    Flipkart, Verified Dataset)        • Aspect-Based Sentiment Analysis (ABSA)
  • Rate Limiting & Compliance         • Context & Workload Extractor
                                       • Sentence Transformers Embeddings
                                       • Vector-Assisted Conflict Detection
                                       • Grounded LLM Explanation (Gemini/OpenAI)
    │                                       │
    └───────────────────┬───────────────────┘
                        ▼
       [ PostgreSQL 16 + pgvector Storage ]
         (With SQLite Local Dev Fallback)
```

---

## Core Capabilities

1. **Aspect-Based Sentiment Analysis (ABSA)**: Evaluates distinct product dimensions (`battery`, `thermals_and_noise`, `display`, `performance`, `build_quality`, `keyboard`, `speakers`, `value_for_money`) independently instead of broad overall ratings.
2. **Context & Usage Profiling**: Discerns the customer's specific workload (software engineering, AAA gaming, lightweight office work, media streaming) and exact hardware configuration.
3. **Automated Conflict Detection**: Automatically identifies aspect polarity clashes and scores the magnitude of customer disagreement.
4. **Evidence-Grounded Explanations**: Uses Google Gemini (with OpenAI fallback) under strict zero-hallucination prompts to synthesize clear explanations backed by cited review excerpts.
5. **Personalized Usage Advisor**: Enables buyers to input their exact use-case and hardware preferences to receive customized warnings and expectation forecasts.

---

## Documentation Links

- [System Architecture Specification](file:///c:/Review_Conflict_Resolver_AI_Project/docs/architecture.md)
- [Database Schema & ER Design](file:///c:/Review_Conflict_Resolver_AI_Project/docs/database_design.md)
- [AI Processing Pipeline Details](file:///c:/Review_Conflict_Resolver_AI_Project/docs/ai_pipeline.md)
- [REST API Documentation](file:///c:/Review_Conflict_Resolver_AI_Project/docs/api_documentation.md)
- [Setup & Installation Guide](file:///c:/Review_Conflict_Resolver_AI_Project/docs/setup_guide.md)
- [Development Log & Milestones](file:///c:/Review_Conflict_Resolver_AI_Project/docs/development_log.md)

---

## License

Proprietary — Built for Review Conflict Resolver AI Project.
