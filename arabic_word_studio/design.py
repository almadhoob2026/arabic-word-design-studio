"""Deterministic document presets, each with its own layout system."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Preset:
    name: str
    label: str
    heading_font: str
    body_font: str
    primary: str
    accent: str
    muted: str
    pale: str
    body_size: float
    h1_size: float
    title_size: float
    margin_cm: float
    orientation: str = "portrait"
    cover: bool = False

@dataclass(frozen=True)
class LayoutRules:
    """Shared physical-layout defaults for all four genres (v1.1)."""
    table_padding_horizontal_twips: int = 155
    table_padding_vertical_twips: int = 85
    table_line_spacing: float = 1.14
    bullet_right_indent_cm: float = 0.55
    bullet_hanging_cm: float = 0.38
    table_spacer_pt: float = 5

LAYOUT = LayoutRules()


PRESETS = {
    "executive_report": Preset("executive_report", "Executive Report", "Noto Kufi Arabic", "Noto Sans Arabic", "172A40", "087E80", "5F7182", "E8F3F1", 10.5, 15, 27, 2.2, cover=True),
    "official_decision": Preset("official_decision", "Official Decision", "Amiri", "Amiri", "252932", "967A53", "656768", "F3F0EA", 12.5, 17, 24, 2.5),
    "strategic_plan": Preset("strategic_plan", "Strategic Plan", "Noto Kufi Arabic", "Noto Sans Arabic", "205B53", "C46D3E", "65716C", "EEF4EF", 10, 15, 23, 1.85, orientation="landscape"),
    "impact_report": Preset("impact_report", "Impact Report", "Noto Kufi Arabic", "Noto Sans Arabic", "653A50", "AF7551", "7C6672", "F6F0F2", 10.5, 15, 25, 2.1, cover=True),
}


def get_preset(name: str) -> Preset:
    if name not in PRESETS:
        raise ValueError(f"Unknown document type {name!r}. Choose: {', '.join(PRESETS)}")
    return PRESETS[name]
