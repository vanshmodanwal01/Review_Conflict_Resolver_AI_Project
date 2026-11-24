"""System Prompts for Forensic Conflict Explanation and Context Extraction"""

EXPLANATION_SYSTEM_PROMPT = """You are a Senior Product Intelligence Investigator and Forensic Review Analyst.
Your goal is to investigate customer disagreements on specific product aspects.

MANDATORY INVESTIGATION RULES:
1. NEVER INVENT OR SPECULATE ON EXPLANATIONS. Every claim must be grounded in the provided review evidence and context.
2. If the provided reviews or context do not contain sufficient evidence to explain why experiences differ, YOU MUST EXPLICITLY STATE:
   "The available review evidence is insufficient to explain this disagreement with high confidence."
3. Distinguish clearly between CORRELATION and CAUSATION. Do not claim causation when the data only reveals correlation.
4. Highlight hardware variants (e.g., 4K OLED vs FHD screen, 8GB vs 16GB RAM) and usage intensity differences (e.g., gaming vs web browsing) whenever present in the evidence.
5. Identify any missing information that would be necessary to resolve the conflict conclusively.

OUTPUT FORMAT:
You MUST respond with a valid, clean JSON object matching this schema:
{
  "summary": "Clear, objective 2-3 sentence overview of the disagreement and why it occurs.",
  "contributing_factors": [
    "Specific factor 1 (e.g. High display resolution drains battery 35% faster)",
    "Specific factor 2 (e.g. Intensive 4K video rendering vs lightweight office typing)"
  ],
  "supporting_evidence_summary": "Summary of satisfied customer experiences.",
  "opposing_evidence_summary": "Summary of dissatisfied customer experiences.",
  "missing_information": "Crucial details not mentioned in reviews (e.g. ambient temperature or battery health settings).",
  "confidence_score": 0.85
}
"""

def build_explanation_user_prompt(
    product_title: str,
    aspect_category: str,
    positive_evidence: list,
    negative_evidence: list,
    divergence_notes: list
) -> str:
    prompt = f"Product: {product_title}\n"
    prompt += f"Conflicting Aspect: {aspect_category.upper()}\n\n"
    
    prompt += "CONTEXTUAL DIVERGENCE DETECTED IN DATA:\n"
    if divergence_notes:
        for note in divergence_notes:
            prompt += f"- {note.get('finding')}\n"
    else:
        prompt += "- No distinct variant or usage intensity split detected in metadata.\n"
    
    prompt += "\nPOSITIVE REVIEW EXCERPTS:\n"
    for idx, item in enumerate(positive_evidence, 1):
        prompt += f"[{idx}] Excerpt: \"{item.get('excerpt')}\"\n"
        prompt += f"    Variant: {item.get('variant_context')}\n"
        prompt += f"    Context: {item.get('usage_context')}\n"

    prompt += "\nNEGATIVE REVIEW EXCERPTS:\n"
    for idx, item in enumerate(negative_evidence, 1):
        prompt += f"[{idx}] Excerpt: \"{item.get('excerpt')}\"\n"
        prompt += f"    Variant: {item.get('variant_context')}\n"
        prompt += f"    Context: {item.get('usage_context')}\n"

    prompt += "\nInvestigate the above evidence and generate the forensic JSON report."
    return prompt
