"""
Advanced ASS Subtitle Renderer
Generates ASS subtitles from style configurations
"""

from typing import List, Dict
from .style_config import StyleConfig

class ASSRenderer:
    """Renders ASS subtitles with advanced styling options"""

    def __init__(self, job_id: str):
        self.job_id = job_id

    def render_subtitles(self, segments: List[Dict], width: int, height: int, style: StyleConfig) -> str:
        """Generate ASS subtitle file with custom styling"""
        ass_path = f"/tmp/subtitles_{self.job_id}.ass"

        if not segments:
            ass_content = self._generate_empty_ass_file(style, width, height)
        else:
            ass_content = self._generate_ass_content(segments, width, height, style)

        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)

        return ass_path

    def _generate_ass_content(self, segments: List[Dict], width: int, height: int, style: StyleConfig) -> str:
        """Generate complete ASS file content"""

        # Calculate responsive font size
        font_size = max(int(height * style.font_size_ratio), 16)

        # Calculate margins
        margin_bottom = max(int(height * style.margin_ratio), 20)
        margin_side = 20

        # Generate header with styles
        header = self._generate_header(font_size, margin_side, margin_bottom, style)

        # Generate dialogue events
        dialogue_lines = []
        for segment in segments:
            start_time = self._seconds_to_ass_time(segment["start"])
            end_time = self._seconds_to_ass_time(segment["end"])

            # Create styled text based on highlight type
            styled_text = self._create_styled_text(segment, style)

            dialogue_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{styled_text}"
            dialogue_lines.append(dialogue_line)

        return header + "\n".join(dialogue_lines)

    def _generate_header(self, font_size: int, margin_side: int, margin_bottom: int, style: StyleConfig) -> str:
        """Generate ASS file header with style definitions"""

        return f"""[Script Info]
Title: Subtitle Ninja - {style.font_family}
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style.font_family},{font_size},{style.base_color},{style.base_color},{style.outline_color},{style.background_color if style.background_enabled else '&H80000000'},1,0,0,0,100,100,0,0,1,{style.outline_width},0,{style.alignment},{margin_side},{margin_side},{margin_bottom},1
Style: Highlight,{style.font_family},{font_size},{style.highlight_color},{style.highlight_color},{style.outline_color},{style.background_color if style.background_enabled else '&H80000000'},1,0,0,0,{self._get_highlight_scale(style)},{self._get_highlight_scale(style)},0,0,1,{style.outline_width},0,{style.alignment},{margin_side},{margin_side},{margin_bottom},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

    def _create_styled_text(self, segment: Dict, style: StyleConfig) -> str:
        """Create styled text with highlighting based on style configuration"""
        words = segment.get("words", [])
        if not words:
            return segment.get("display_text", "")

        styled_parts = []

        for i, word in enumerate(words):
            if i == 0:  # First word - apply highlighting
                if style.highlight_style == "color_change":
                    styled_parts.append(f"{{\\c{style.highlight_color}&}}{word}{{\\c{style.base_color}&}}")

                elif style.highlight_style == "scale_up":
                    scale = self._get_highlight_scale(style)
                    styled_parts.append(f"{{\\fscx{scale}\\fscy{scale}\\c{style.highlight_color}&}}{word}{{\\fscx100\\fscy100\\c{style.base_color}&}}")

                elif style.highlight_style == "glow_pulse":
                    if style.glow_enabled:
                        # Gaming style: Green text with black outline AND green shadow glow
                        shadow_size = 3 if style.glow_intensity == "strong" else 2
                        styled_parts.append(f"{{\\c{style.highlight_color}&\\3c{style.outline_color}&\\4c{style.highlight_color}&\\bord{style.outline_width}\\shad{shadow_size}}}{word}{{\\c{style.base_color}&\\3c{style.outline_color}&\\4c&H00000000&\\bord2\\shad0}}")
                    else:
                        styled_parts.append(f"{{\\c{style.highlight_color}&}}{word}{{\\c{style.base_color}&}}")

                elif style.highlight_style == "background_highlight":
                    # YouTube style: Simulate background with thick colored border
                    styled_parts.append(f"{{\\c{style.base_color}&\\3c{style.highlight_color}&\\bord6}}{word}{{\\3c{style.outline_color}&\\bord2}}")

                else:  # Default fallback
                    styled_parts.append(f"{{\\c{style.highlight_color}&}}{word}{{\\c{style.base_color}&}}")

            else:  # Other words - normal style
                styled_parts.append(word)

        return " ".join(styled_parts)

    def _get_highlight_scale(self, style: StyleConfig) -> int:
        """Get scale percentage for highlight effects"""
        if style.highlight_style == "scale_up":
            return 120  # 20% larger
        return 100  # Normal size

    def _generate_empty_ass_file(self, style: StyleConfig, width: int, height: int) -> str:
        """Generate empty ASS file for fallback"""
        font_size = max(int(height * style.font_size_ratio), 16)
        margin_bottom = max(int(height * style.margin_ratio), 20)

        return f"""[Script Info]
Title: Subtitle Ninja
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,{style.font_family},{font_size},{style.base_color},{style.base_color},{style.outline_color},&H80000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,{margin_bottom},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,No speech detected
"""

    def _seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"