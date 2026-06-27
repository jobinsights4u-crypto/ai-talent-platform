"""
taxonomy/domains.py
-------------------
Canonical AI domain definitions and keyword-to-domain mapping.
Used for enrichment and display-level normalisation.
"""

from __future__ import annotations

# Primary domains in display order
DOMAIN_ORDER = [
    "GenAI",
    "Machine Learning",
    "Data Science",
    "NLP",
    "Computer Vision",
    "MLOps",
    "Robotics",
    "AI Ethics",
    "BI / Analytics",
    "Other",
]

DOMAIN_DESCRIPTIONS: dict[str, str] = {
    "GenAI":            "Generative AI, LLMs, prompt engineering, foundation models",
    "Machine Learning": "Classical ML, deep learning, model training & evaluation",
    "Data Science":     "Statistical analysis, experimentation, data pipelines",
    "NLP":              "Natural language processing, text analytics, conversational AI",
    "Computer Vision":  "Image / video recognition, object detection, visual AI",
    "MLOps":            "Model deployment, monitoring, CI/CD for ML, platform engineering",
    "Robotics":         "Robot autonomy, motion planning, sensor fusion",
    "AI Ethics":        "Responsible AI, bias mitigation, fairness, governance",
    "BI / Analytics":   "Business intelligence, dashboards, reporting, data visualisation",
    "Other":            "AI-adjacent roles not fitting a primary domain",
}

# Keyword → canonical domain mapping for role-classification logic
KEYWORD_DOMAIN_MAP: dict[str, str] = {
    "generative": "GenAI",
    "llm": "GenAI",
    "gpt": "GenAI",
    "prompt": "GenAI",
    "foundation model": "GenAI",
    "machine learning": "Machine Learning",
    "deep learning": "Machine Learning",
    "neural network": "Machine Learning",
    "data science": "Data Science",
    "data scientist": "Data Science",
    "statistics": "Data Science",
    "nlp": "NLP",
    "natural language": "NLP",
    "text mining": "NLP",
    "sentiment": "NLP",
    "computer vision": "Computer Vision",
    "image recognition": "Computer Vision",
    "object detection": "Computer Vision",
    "mlops": "MLOps",
    "model deployment": "MLOps",
    "kubeflow": "MLOps",
    "robot": "Robotics",
    "autonomous": "Robotics",
    "responsible ai": "AI Ethics",
    "bias": "AI Ethics",
    "fairness": "AI Ethics",
    "bi ": "BI / Analytics",
    "business intelligence": "BI / Analytics",
    "tableau": "BI / Analytics",
    "power bi": "BI / Analytics",
}
