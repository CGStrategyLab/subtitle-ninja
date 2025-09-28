import os
import json
import subprocess
import tempfile
from pathlib import Path
from typing import Tuple, Dict, Callable, Optional

import whisper
import ffmpeg
from PIL import Image, ImageDraw, ImageFont

from .style_config import StyleConfig, StylePresets
from .ass_renderer import ASSRenderer


class VideoProcessor:
    def __init__(self, job_id: str):
        self.job_id = job_id
        self.output_dir = Path("downloads")
        self.output_dir.mkdir(exist_ok=True)

    def process(self, input_path: str, style_preset: str = "instagram_classic", progress_callback: Optional[Callable] = None) -> str:
        """Process video with subtitles using specified style preset"""
        input_path = Path(input_path)

        if progress_callback:
            progress_callback(15, "Analyzing video properties...")

        # Get video properties
        width, height, fps, duration = self.get_video_properties(input_path)
        aspect_ratio = width / height

        if progress_callback:
            progress_callback(25, "Extracting audio for transcription...")

        # Extract audio for Whisper
        audio_path = self.extract_audio(input_path)

        if progress_callback:
            progress_callback(40, "Transcribing audio with Whisper...")

        # Transcribe with Whisper
        segments = self.transcribe_audio(audio_path)

        if progress_callback:
            progress_callback(60, "Generating subtitle overlays...")

        if progress_callback:
            progress_callback(80, f"Rendering final video with {style_preset} style...")

        # Get style configuration
        style = StylePresets.get_preset(style_preset)

        # Render final video with styled ASS subtitles
        output_path = self.render_video_with_subtitles(
            input_path, width, height, segments, style, style_preset
        )

        # Cleanup temporary files
        if os.path.exists(audio_path):
            os.unlink(audio_path)

        if progress_callback:
            progress_callback(100, "Video processing completed!")

        return str(output_path)

    def get_video_properties(self, input_path: Path) -> Tuple[int, int, float, float]:
        """Get video width, height, fps, and duration"""
        probe = ffmpeg.probe(str(input_path))
        video_stream = next(stream for stream in probe['streams'] if stream['codec_type'] == 'video')

        width = int(video_stream['width'])
        height = int(video_stream['height'])
        fps = eval(video_stream['r_frame_rate'])  # Convert fraction to float
        duration = float(video_stream['duration'])

        return width, height, fps, duration

    def extract_audio(self, input_path: Path) -> str:
        """Extract audio from video for Whisper processing"""
        audio_path = f"/tmp/audio_{self.job_id}.wav"

        (
            ffmpeg
            .input(str(input_path))
            .output(audio_path, acodec='pcm_s16le', ac=1, ar='16000')
            .overwrite_output()
            .run(quiet=True)
        )

        return audio_path

    def transcribe_audio(self, audio_path: str) -> list:
        """Transcribe audio using Whisper and create word groups"""
        model = whisper.load_model("base")
        result = model.transcribe(audio_path, word_timestamps=True)

        # First, extract individual words with timestamps
        individual_words = []
        for segment in result["segments"]:
            if "words" in segment:
                for word in segment["words"]:
                    individual_words.append({
                        "start": word["start"],
                        "end": word["end"],
                        "text": word["word"].strip()
                    })
            else:
                # Fallback if word-level timestamps not available
                individual_words.append({
                    "start": segment["start"],
                    "end": segment["end"],
                    "text": segment["text"].strip()
                })

        # Create grouped segments with sliding window
        return self.create_word_groups(individual_words)

    def create_word_groups(self, words: list, words_per_group: int = 3) -> list:
        """Create non-overlapping groups of words with highlight timing"""
        if not words:
            return []

        grouped_segments = []

        for i in range(len(words)):
            # Create a group starting from current word
            group_words = []
            group_start = words[i]["start"]

            # Calculate end time: either when next word starts, or when current word group ends
            if i + 1 < len(words):
                group_end = words[i + 1]["start"]  # End when next word starts (no overlap)
            else:
                group_end = words[i]["end"]  # Last word uses its natural end time

            # Add current word and next words (up to words_per_group total)
            for j in range(words_per_group):
                if i + j < len(words):
                    word = words[i + j]
                    group_words.append(word["text"])

            grouped_segments.append({
                "start": group_start,
                "end": group_end,
                "words": group_words,
                "current_word_index": 0,  # First word is highlighted
                "current_word": group_words[0] if group_words else "",
                "display_text": " ".join(group_words)
            })

        return grouped_segments

    def get_subtitle_config(self, width: int, height: int, aspect_ratio: float) -> Dict:
        """Get subtitle configuration based on aspect ratio"""
        if aspect_ratio < 0.75:  # Vertical (9:16 or similar)
            return {
                "fontsize": max(int(height * 0.06), 24),
                "y": height - int(height * 0.25),  # Bottom quarter
                "box_color": "black@0.7",
                "font_color": "white",
                "outline_color": "black",
                "outline_width": 2,
                "alignment": "center",
                "max_width": int(width * 0.9)
            }
        elif aspect_ratio > 1.5:  # Horizontal (16:9 or similar)
            return {
                "fontsize": max(int(height * 0.08), 28),
                "y": height - int(height * 0.15),  # Bottom 15%
                "box_color": "black@0.7",
                "font_color": "white",
                "outline_color": "black",
                "outline_width": 2,
                "alignment": "center",
                "max_width": int(width * 0.8)
            }
        else:  # Square (1:1 or close)
            return {
                "fontsize": max(int(height * 0.07), 26),
                "y": height - int(height * 0.2),  # Bottom 20%
                "box_color": "black@0.7",
                "font_color": "white",
                "outline_color": "black",
                "outline_width": 2,
                "alignment": "center",
                "max_width": int(width * 0.85)
            }

    def create_subtitle_filter(self, segments: list, config: Dict, fps: float) -> str:
        """Create FFmpeg drawtext filter for subtitles with Instagram-style highlighting"""
        if not segments:
            return ""

        filters = []

        for i, segment in enumerate(segments):
            start_frame = int(segment["start"] * fps)
            end_frame = int(segment["end"] * fps)
            text = segment["text"].replace("'", "'\\''")  # Escape single quotes

            # Create animated highlighting effect
            filter_str = (
                f"drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf:"
                f"text='{text}':"
                f"fontcolor={config['font_color']}:"
                f"fontsize={config['fontsize']}:"
                f"x=(w-text_w)/2:"
                f"y={config['y']}:"
                f"shadowcolor={config['outline_color']}:"
                f"shadowx={config['outline_width']}:"
                f"shadowy={config['outline_width']}:"
                f"box=1:"
                f"boxcolor={config['box_color']}:"
                f"boxborderw=10:"
                f"enable='between(n,{start_frame},{end_frame})'"
            )

            filters.append(filter_str)

        return ",".join(filters)

    def render_video_with_subtitles(self, input_path: Path, width: int, height: int, segments: list, style: StyleConfig, style_name: str = "default") -> Path:
        """Render final video with styled ASS subtitle overlays"""
        output_filename = f"{self.job_id}_{style_name}_with_subtitles.mp4"
        output_path = self.output_dir / output_filename

        # Create ASS file with selected style
        renderer = ASSRenderer(self.job_id)
        ass_path = renderer.render_subtitles(segments, width, height, style)

        # Debug: Print style info for troubleshooting
        print(f"DEBUG: Using style {style_name}")
        print(f"DEBUG: Highlight style: {style.highlight_style}")
        print(f"DEBUG: Colors - base: {style.base_color}, highlight: {style.highlight_color}")
        print(f"DEBUG: ASS file path: {ass_path}")

        # Build FFmpeg command with ASS subtitle burning
        try:
            cmd = [
                'ffmpeg', '-y',
                '-i', str(input_path),
                '-vf', f"ass={ass_path}",
                '-c:a', 'copy',
                '-c:v', 'libx264',
                '-preset', 'fast',
                str(output_path)
            ]

            result = subprocess.run(cmd, capture_output=True, text=True, check=True)

        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg failed: {e.stderr}")

        # Clean up temporary ASS file
        if os.path.exists(ass_path):
            os.unlink(ass_path)

        return output_path

    def create_srt_file_from_segments(self, segments: list) -> str:
        """Create SRT subtitle file from grouped segments"""
        srt_path = f"/tmp/subtitles_{self.job_id}.srt"

        if not segments:
            # Fallback if no segments
            srt_content = "1\n00:00:00,000 --> 00:00:05,000\nNo speech detected\n\n"
        else:
            srt_lines = []
            for i, segment in enumerate(segments, 1):
                start_time = self.seconds_to_srt_time(segment["start"])
                end_time = self.seconds_to_srt_time(segment["end"])

                # Use display_text from grouped segments
                text = segment.get("display_text", "").strip()
                if not text and "words" in segment:
                    # Fallback: join words if display_text not available
                    text = " ".join(segment["words"]).strip()
                elif not text and "text" in segment:
                    # Fallback: use text field if available (for backward compatibility)
                    text = segment["text"].strip()

                if text:  # Only add non-empty text
                    srt_lines.append(f"{i}")
                    srt_lines.append(f"{start_time} --> {end_time}")
                    srt_lines.append(text)
                    srt_lines.append("")  # Empty line between subtitles

            srt_content = "\n".join(srt_lines)

        with open(srt_path, 'w', encoding='utf-8') as f:
            f.write(srt_content)

        return srt_path

    def create_ass_file_from_segments(self, segments: list, width: int, height: int) -> str:
        """Create ASS subtitle file with word highlighting (Instagram Classic style)"""
        ass_path = f"/tmp/subtitles_{self.job_id}.ass"

        if not segments:
            # Fallback if no segments
            ass_content = self.generate_empty_ass_file()
        else:
            ass_content = self.generate_ass_content(segments, width, height)

        with open(ass_path, 'w', encoding='utf-8') as f:
            f.write(ass_content)

        return ass_path

    def generate_ass_content(self, segments: list, width: int, height: int) -> str:
        """Generate ASS content with Instagram Classic styling"""

        # Calculate font size based on video dimensions
        base_font_size = max(int(height * 0.05), 20)

        # Calculate bottom margin (smaller value = closer to bottom)
        bottom_margin = max(int(height * 0.08), 30)  # About 8% from bottom, minimum 30px

        # ASS file header with styles
        header = f"""[Script Info]
Title: Subtitle Ninja - Instagram Classic
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,{base_font_size},&Hffffff,&Hffffff,&H000000,&H80000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,{bottom_margin},1
Style: Highlight,Arial,{base_font_size},&H00d7ff,&H00d7ff,&H000000,&H80000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,{bottom_margin},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

        # Generate dialogue events
        dialogue_lines = []
        for i, segment in enumerate(segments):
            start_time = self.seconds_to_ass_time(segment["start"])
            end_time = self.seconds_to_ass_time(segment["end"])

            # Create highlighted text with timing
            highlighted_text = self.create_highlighted_ass_text(segment)

            dialogue_line = f"Dialogue: 0,{start_time},{end_time},Default,,0,0,0,,{highlighted_text}"
            dialogue_lines.append(dialogue_line)

        return header + "\n".join(dialogue_lines)

    def create_highlighted_ass_text(self, segment: dict) -> str:
        """Create ASS text with first word highlighted in yellow"""
        words = segment.get("words", [])
        if not words:
            return segment.get("display_text", "")

        # First word highlighted in yellow, rest in white
        highlighted_parts = []

        for i, word in enumerate(words):
            if i == 0:  # First word - highlighted
                highlighted_parts.append(f"{{\\c&H00d7ff&}}{word}{{\\c&Hffffff&}}")
            else:  # Other words - normal white
                highlighted_parts.append(word)

        return " ".join(highlighted_parts)

    def generate_empty_ass_file(self) -> str:
        """Generate empty ASS file for fallback"""
        return """[Script Info]
Title: Subtitle Ninja
ScriptType: v4.00+

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,Arial,24,&Hffffff,&Hffffff,&H000000,&H80000000,1,0,0,0,100,100,0,0,1,2,0,2,20,20,50,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
Dialogue: 0,0:00:00.00,0:00:05.00,Default,,0,0,0,,No speech detected
"""

    def seconds_to_ass_time(self, seconds: float) -> str:
        """Convert seconds to ASS time format (H:MM:SS.cc)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        centisecs = int((seconds % 1) * 100)
        return f"{hours}:{minutes:02d}:{secs:02d}.{centisecs:02d}"

    def seconds_to_srt_time(self, seconds: float) -> str:
        """Convert seconds to SRT time format (HH:MM:SS,mmm)"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millisecs = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millisecs:03d}"

    def parse_drawtext_filter(self, filter_string: str) -> dict:
        """Parse drawtext filter string into parameters"""
        # For now, return a simplified version
        # In a full implementation, you'd parse the complex filter string
        return {
            'fontfile': '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
            'fontcolor': 'white',
            'fontsize': 40,
            'x': '(w-text_w)/2',
            'y': 'h-h/4',
            'shadowcolor': 'black',
            'shadowx': 2,
            'shadowy': 2,
            'box': 1,
            'boxcolor': 'black@0.7',
            'boxborderw': 10
        }