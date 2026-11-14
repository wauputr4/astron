"""Optional natal and predictive longitude aspects, with a uniform minor orb."""

ANGLES = {"semi-sextile": 30, "semi-square": 45, "quintile": 72,
          "sesquiquadrate": 135, "quincunx": 150}
ALIASES = {"semisextile": "semi-sextile", "semisquare": "semi-square",
           "sesquisquare": "sesquiquadrate", "inconjunct": "quincunx"}
ORB = 2


def requested(payload):
    value = payload.get("minor_aspects", False)
    if isinstance(value, bool):
        return list(ANGLES) if value else []
    if not isinstance(value, list) or not all(isinstance(name, str) for name in value):
        raise ValueError("minor_aspects must be a boolean or a list of aspect names")
    names = list(dict.fromkeys(ALIASES.get(name.lower(), name.lower()) for name in value))
    if any(name not in ANGLES for name in names):
        raise ValueError("Unknown minor aspect. Choose from " + ", ".join(ANGLES))
    return names


def options(names, operation):
    if not names:
        return {}
    from kerykeion.settings.config_constants import (
        DEFAULT_ACTIVE_ASPECTS, DEFAULT_NATAL_POINT_ORB_ADJUSTMENTS, PREDICTIVE_ACTIVE_ASPECTS,
    )
    natal = operation in ("natal", "svg")
    major = DEFAULT_ACTIVE_ASPECTS if natal else PREDICTIVE_ACTIVE_ASPECTS
    if operation == "progression":
        return {"aspects": [a["name"] for a in major] + names}
    result = {"active_aspects": major + [{"name": name, "orb": ORB} for name in names]}
    if natal:
        result["point_orb_adjustments"] = {
            point: {a["name"]: adjustment for a in major}
            for point, adjustment in DEFAULT_NATAL_POINT_ORB_ADJUSTMENTS.items()
        }
    return result
