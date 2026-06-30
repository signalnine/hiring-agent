"""
Role evaluation profiles.

Each profile defines how a resume is scored for a given seniority/role
archetype: which evaluation prompt templates to use, and how the four fixed
scoring slots (production, technical_skills, self_projects, open_source) are
weighted, labelled, and ordered in the output.

Select a profile with the ROLE_PROFILE environment variable
(e.g. ROLE_PROFILE=manager). Defaults to "principal".
"""

import os

# Each category entry: (json_field, display_label, max_points).
# The four json_field names are fixed by the Pydantic schema; their *meaning*
# is repurposed per profile and documented in that profile's prompt templates.
PROFILES = {
    "principal": {
        "label": "Senior Staff / Principal Engineer",
        "criteria_template": "resume_evaluation_criteria.jinja",
        "system_template": "resume_evaluation_system_message.jinja",
        "categories": [
            ("production", "🏢 Scope & Production Impact:    ", 40),
            ("technical_skills", "💻 Technical Depth & Breadth:    ", 25),
            ("self_projects", "🚀 Engineering Projects/Systems: ", 20),
            ("open_source", "🌐 Open Source & Tech Influence: ", 15),
        ],
    },
    "manager": {
        "label": "Engineering Manager / Director",
        "criteria_template": "resume_evaluation_criteria_manager.jinja",
        "system_template": "resume_evaluation_system_message_manager.jinja",
        "categories": [
            ("production", "🧭 Leadership Scope & Org Impact:  ", 45),
            ("technical_skills", "💻 Technical Judgment & Breadth:   ", 25),
            ("self_projects", "🚀 Initiative & Delivery:          ", 15),
            ("open_source", "🌐 Technical Influence & Community:", 15),
        ],
    },
}

DEFAULT_PROFILE = "principal"


def get_active_profile() -> dict:
    """Return the profile selected by ROLE_PROFILE (default: principal)."""
    name = os.getenv("ROLE_PROFILE", DEFAULT_PROFILE).strip().lower()
    return PROFILES.get(name, PROFILES[DEFAULT_PROFILE])


def category_maxes(profile: dict = None) -> dict:
    """Map of json_field -> max points for the active (or given) profile."""
    profile = profile or get_active_profile()
    return {field: maximum for field, _label, maximum in profile["categories"]}
