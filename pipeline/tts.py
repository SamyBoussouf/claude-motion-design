"""
ElevenLabs TTS module.
Generates voiceover audio and returns word-level timestamps.
"""

import os
import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# Voice calibrated for calm, measured psychology narrator (matches psychovius style)
# "Adam" — deep, thoughtful, slight gravitas
VOICE_ID = "pNInz6obpgDQGcFmaJgB"  # Adam

# Generation settings
MODEL_ID = "eleven_multilingual_v2"
VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.80,
    "style": 0.20,
    "use_speaker_boost": True
}


def generate_voiceover(script: str, output_path: str) -> dict:
    """
    Generate voiceover from script text.
    Returns dict with:
        - audio_path: path to saved MP3
        - duration: total audio duration in seconds
        - word_timestamps: list of {word, start, end} dicts
    """
    if not ELEVENLABS_API_KEY:
        raise RuntimeError("ELEVENLABS_API_KEY not set in .env")

    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    print(f"  tts: generating audio ({len(script)} chars)...")

    # Request with timestamps via with_timestamps endpoint
    response = client.text_to_speech.convert_with_timestamps(
        voice_id=VOICE_ID,
        text=script,
        model_id=MODEL_ID,
        voice_settings=VoiceSettings(
            stability=VOICE_SETTINGS["stability"],
            similarity_boost=VOICE_SETTINGS["similarity_boost"],
            style=VOICE_SETTINGS["style"],
            use_speaker_boost=VOICE_SETTINGS["use_speaker_boost"]
        )
    )

    # Write audio bytes
    with open(output_path, "wb") as f:
        f.write(response.audio)

    # Parse alignment data into word timestamps
    word_timestamps = _parse_alignment(response.alignment)

    # Compute duration from last word end time
    duration = word_timestamps[-1]["end"] if word_timestamps else 0.0

    # Save timestamps as JSON alongside audio
    ts_path = output_path.with_suffix(".json")
    with open(ts_path, "w") as f:
        json.dump({"duration": duration, "words": word_timestamps}, f, indent=2)

    print(f"  tts: saved audio -> {output_path}")
    print(f"  tts: duration = {duration:.2f}s, words = {len(word_timestamps)}")

    return {
        "audio_path": str(output_path),
        "duration": duration,
        "word_timestamps": word_timestamps
    }


def _parse_alignment(alignment) -> list[dict]:
    """
    Convert ElevenLabs character-level alignment to word-level timestamps.
    alignment has: characters, character_start_times_seconds, character_end_times_seconds
    """
    if alignment is None:
        return []

    chars = alignment.characters
    starts = alignment.character_start_times_seconds
    ends = alignment.character_end_times_seconds

    words = []
    current_word = ""
    word_start = None

    for char, start, end in zip(chars, starts, ends):
        if char == " " or char == "\n":
            if current_word.strip():
                words.append({
                    "word": current_word.strip(),
                    "start": round(word_start, 3),
                    "end": round(end, 3)
                })
            current_word = ""
            word_start = None
        else:
            if word_start is None:
                word_start = start
            current_word += char

    # Last word
    if current_word.strip() and word_start is not None:
        words.append({
            "word": current_word.strip(),
            "start": round(word_start, 3),
            "end": round(ends[-1], 3)
        })

    return words


def load_timestamps(json_path: str) -> dict:
    """Load previously generated timestamps from JSON."""
    with open(json_path) as f:
        return json.load(f)
