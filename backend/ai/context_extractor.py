"""Context and Customer Usage Extractor"""
import re
from typing import Dict, Any, Optional
from backend.core.logging import logger


class ContextExtractor:
    """
    Extracts customer usage intensity, primary use case, hardware variant clues,
    and environmental factors. Distinguishes explicitly stated facts from inferences.
    """
    
    # Task domains
    USE_CASES = {
        "gaming": ["game", "games", "gaming", "cyberpunk", "fps", "steam", "rtx", "gpu"],
        "content_creation": ["premiere", "photoshop", "davinci", "video editing", "render", "rendering", "timeline", "color grading", "4k export"],
        "software_development": ["docker", "coding", "code", "compile", "python", "xcode", "vs code", "developer", "programming", "builds"],
        "office_work": ["zoom", "teams", "slack", "excel", "sheets", "documents", "typing", "office", "meetings", "emails"],
        "college_study": ["college", "student", "lectures", "school", "notes", "dorm", "studying"],
        "casual": ["netflix", "youtube", "streaming", "safari", "browsing", "movies"]
    }

    # Intensity mappings
    HIGH_INTENSITY = [
        "gaming", "game", "games", "render", "rendering", "compile", "docker", "ml",
        "4k export", "4k", "premiere", "davinci", "timeline", "video editing",
        "heavy", "intense", "extreme", "benchmark", "stress"
    ]
    LOW_INTENSITY = ["browsing", "typing", "notes", "zoom", "slack", "streaming", "netflix", "unplugged", "lightweight", "casual"]

    # Environment cues
    ENVIRONMENT_CUES = {
        "travel": ["flight", "plane", "travel", "train", "commute", "backpack", "airport"],
        "lap": ["lap", "couch", "bed"],
        "desk": ["desk", "monitor", "dock", "cooling pad", "workstation"],
        "hot_climate": ["hot room", "summer", "warm room", "ambient"]
    }

    # Variant extraction regex
    RAM_PATTERN = re.compile(r'\b(8|16|32|64)\s*gb\b', re.IGNORECASE)
    DISPLAY_PATTERN = re.compile(r'\b(oled|ips|4k|fhd\+?|3\.5k|qhd|wqhd|120hz|144hz|165hz|240hz)\b', re.IGNORECASE)
    GPU_PATTERN = re.compile(r'\b(rtx\s*\d{4}|iris\s*xe|radeon|integrated)\b', re.IGNORECASE)

    def extract_context(self, review_text: str, declared_variant: Optional[str] = None) -> Dict[str, Any]:
        text_lower = review_text.lower()
        extracted_attributes = {}
        certainty = "unknown"

        # 1. Hardware Variant Cues
        detected_rams = self.RAM_PATTERN.findall(text_lower)
        if detected_rams:
            extracted_attributes["mentioned_ram"] = f"{detected_rams[0].upper()}GB"
            certainty = "explicit"
            
        detected_displays = self.DISPLAY_PATTERN.findall(text_lower)
        if detected_displays:
            extracted_attributes["mentioned_display"] = detected_displays[0].upper()
            certainty = "explicit"

        detected_gpus = self.GPU_PATTERN.findall(text_lower)
        if detected_gpus:
            extracted_attributes["mentioned_gpu"] = detected_gpus[0].upper()
            certainty = "explicit"

        if declared_variant:
            extracted_attributes["declared_variant"] = declared_variant
            certainty = "explicit"

        # 2. Primary Use Case
        primary_use_case = "general"
        for uc, keywords in self.USE_CASES.items():
            if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in keywords):
                primary_use_case = uc
                if certainty != "explicit":
                    certainty = "inferred"
                break

        # 3. Workload Intensity
        usage_intensity = "unknown"
        if any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in self.HIGH_INTENSITY):
            usage_intensity = "high"
            certainty = "explicit" if certainty == "explicit" else "inferred"
        elif any(re.search(r'\b' + re.escape(kw) + r'\b', text_lower) for kw in self.LOW_INTENSITY):
            usage_intensity = "low"
            certainty = "explicit" if certainty == "explicit" else "inferred"
        else:
            usage_intensity = "medium"

        # 4. Environmental Conditions
        environment = "unknown"
        for env_name, env_cues in self.ENVIRONMENT_CUES.items():
            if any(re.search(r'\b' + re.escape(c) + r'\b', text_lower) for c in env_cues):
                environment = env_name
                break

        # 5. Expectation / Benchmark Comparison
        expectation_benchmark = None
        if "macbook" in text_lower:
            expectation_benchmark = "Compared against Apple MacBook benchmark"
        elif "old laptop" in text_lower or "previous laptop" in text_lower or "upgraded from" in text_lower:
            expectation_benchmark = "Upgrading from older-generation hardware"

        return {
            "usage_intensity": usage_intensity,
            "primary_use_case": primary_use_case,
            "environment": environment,
            "expectation_benchmark": expectation_benchmark,
            "certainty": certainty,
            "extracted_attributes": extracted_attributes
        }

context_extractor = ContextExtractor()
