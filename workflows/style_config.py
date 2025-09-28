"""
Subtitle Style Configuration System
Handles style presets and custom style generation
"""

from typing import Dict, Any
from dataclasses import dataclass, asdict
import json

@dataclass
class StyleConfig:
    """Complete style configuration for subtitles"""

    # Font settings
    font_family: str = "Arial"
    font_size_ratio: float = 0.05  # Ratio of video height
    font_weight: str = "bold"

    # Colors (ASS format: &HBBGGRR& where BB=blue, GG=green, RR=red)
    base_color: str = "&Hffffff"     # White
    highlight_color: str = "&H00d7ff"  # Gold
    outline_color: str = "&H000000"   # Black

    # Effects
    highlight_style: str = "color_change"  # color_change, scale_up, glow_pulse, background_highlight
    outline_width: int = 2
    glow_enabled: bool = False
    glow_intensity: str = "none"  # none, soft, strong

    # Layout
    words_per_line: int = 3
    position: str = "bottom"  # top, center, bottom
    alignment: int = 2  # ASS alignment: 1=left, 2=center, 3=right
    margin_ratio: float = 0.08  # Distance from edge as ratio of video height

    # Background
    background_enabled: bool = False
    background_color: str = "&H80000000"  # Semi-transparent black
    background_opacity: int = 80

class StylePresets:
    """Predefined popular style presets"""

    @staticmethod
    def get_preset(preset_name: str) -> StyleConfig:
        """Get a predefined style preset"""
        presets = {
            "instagram_classic": StyleConfig(
                font_family="Arial",
                font_size_ratio=0.05,
                base_color="&Hffffff",      # White
                highlight_color="&H00d7ff",  # Gold
                outline_color="&H000000",    # Black
                highlight_style="color_change",
                outline_width=2,
                words_per_line=3,
                position="bottom",
                margin_ratio=0.08
            ),

            "tiktok_viral": StyleConfig(
                font_family="Arial",
                font_size_ratio=0.055,
                base_color="&Hffffff",       # White
                highlight_color="&Hffff00",  # Cyan
                outline_color="&H000000",    # Black
                highlight_style="glow_pulse",
                outline_width=1,
                glow_enabled=True,
                glow_intensity="strong",
                words_per_line=4,
                position="bottom",
                margin_ratio=0.07
            ),

            "youtube_professional": StyleConfig(
                font_family="Arial",
                font_size_ratio=0.045,
                base_color="&Hffffff",       # White
                highlight_color="&H0000ff",  # Red
                outline_color="&H000000",    # Black
                highlight_style="background_highlight",
                outline_width=2,
                background_enabled=True,
                background_color="&H80000000",  # Semi-transparent black
                background_opacity=70,
                words_per_line=3,
                position="bottom",
                margin_ratio=0.09
            ),

            "minimalist": StyleConfig(
                font_family="Arial",
                font_size_ratio=0.04,
                base_color="&Hffffff",       # White
                highlight_color="&He2904a",  # Soft blue
                outline_color="&H404040",    # Gray
                highlight_style="scale_up",
                outline_width=1,
                words_per_line=3,
                position="center",
                margin_ratio=0.1
            ),

            "gaming": StyleConfig(
                font_family="Arial",
                font_size_ratio=0.06,
                base_color="&Hffffff",       # White
                highlight_color="&H00ff00",  # Green
                outline_color="&H000000",    # Black
                highlight_style="glow_pulse",
                outline_width=3,
                glow_enabled=True,
                glow_intensity="strong",
                words_per_line=2,
                position="bottom",
                margin_ratio=0.06
            )
        }

        return presets.get(preset_name, presets["instagram_classic"])

    @staticmethod
    def list_presets() -> list:
        """Get list of available preset names"""
        return [
            "instagram_classic",
            "tiktok_viral",
            "youtube_professional",
            "minimalist",
            "gaming"
        ]

    @staticmethod
    def get_preset_info() -> Dict[str, Dict[str, str]]:
        """Get preset descriptions for UI"""
        return {
            "instagram_classic": {
                "name": "Instagram Classic",
                "description": "Clean white text with gold highlight",
                "best_for": "Professional content, tutorials"
            },
            "tiktok_viral": {
                "name": "TikTok Viral",
                "description": "Bold text with cyan glow effect",
                "best_for": "Dance videos, trends, young audience"
            },
            "youtube_professional": {
                "name": "YouTube Professional",
                "description": "Red background highlight style",
                "best_for": "Educational content, business videos"
            },
            "minimalist": {
                "name": "Minimalist",
                "description": "Subtle scale effect with soft colors",
                "best_for": "Aesthetic content, quotes"
            },
            "gaming": {
                "name": "Gaming/Streamer",
                "description": "Bold green glow with thick outline",
                "best_for": "Gaming content, reactions"
            }
        }

def convert_hex_to_ass_color(hex_color: str) -> str:
    """Convert hex color (#RRGGBB) to ASS format (&HBBGGRR&)"""
    if hex_color.startswith('#'):
        hex_color = hex_color[1:]

    if len(hex_color) == 6:
        r = hex_color[0:2]
        g = hex_color[2:4]
        b = hex_color[4:6]
        return f"&H{b}{g}{r}"

    return "&Hffffff"  # Default to white

def convert_ass_to_hex_color(ass_color: str) -> str:
    """Convert ASS color (&HBBGGRR&) to hex format (#RRGGBB)"""
    if ass_color.startswith('&H') and len(ass_color) >= 8:
        color_part = ass_color[2:8]
        b = color_part[0:2]
        g = color_part[2:4]
        r = color_part[4:6]
        return f"#{r}{g}{b}".upper()

    return "#FFFFFF"  # Default to white