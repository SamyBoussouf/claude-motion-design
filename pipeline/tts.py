"""
TTS module — dual backend: ElevenLabs (primary) or edge-tts + Whisper (fallback).

ElevenLabs returns native word-level timestamps.
edge-tts requires faster-whisper to extract word timestamps post-generation.

generate_voiceover() tries ElevenLabs first, falls back to edge-tts automatically.
"""

import os
import json
import asyncio
import subprocess
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY")

# ElevenLabs — Adam voice (deep, calm narrator)
EL_VOICE_ID = "pNInz6obpgDQGcFmaJgB"
EL_MODEL_ID = "eleven_multilingual_v2"
EL_VOICE_SETTINGS = {
    "stability": 0.55,
    "similarity_boost": 0.80,
    "style": 0.20,
    "use_speaker_boost": True,
}

# edge-tts — GuyNeural: deep, measured American narrator
EDGE_VOICE = "en-US-GuyNeural"
EDGE_RATE = "-8%"    # slightly slower than default for dramatic pacing
EDGE_PITCH = "-3Hz"  # slightly deeper


def generate_voiceover(script: str, output_path: str) -> dict:
    """
    Generate voiceover. Tries ElevenLabs first, falls back to edge-tts + Whisper.
    Returns:
        audio_path       : str
        duration         : float (seconds)
        word_timestamps  : list[{word, start, end}]
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if ELEVENLABS_API_KEY:
        try:
            return _generate_elevenlabs(script, output_path)
        except Exception as e:
            print(f"  tts: ElevenLabs failed ({e.__class__.__name__}), falling back to edge-tts")

    return _generate_edge_tts(script, output_path)


# ── ElevenLabs backend ────────────────────────────────────────────────────────

def _generate_elevenlabs(script: str, output_path: Path) -> dict:
    from elevenlabs.client import ElevenLabs
    from elevenlabs import VoiceSettings

    client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
    print(f"  tts [ElevenLabs]: generating ({len(script)} chars)...")

    response = client.text_to_speech.convert_with_timestamps(
        voice_id=EL_VOICE_ID,
        text=script,
        model_id=EL_MODEL_ID,
        voice_settings=VoiceSettings(
            stability=EL_VOICE_SETTINGS["stability"],
            similarity_boost=EL_VOICE_SETTINGS["similarity_boost"],
            style=EL_VOICE_SETTINGS["style"],
            use_speaker_boost=EL_VOICE_SETTINGS["use_speaker_boost"],
        ),
    )

    with open(output_path, "wb") as f:
        f.write(response.audio)

    word_timestamps = _parse_el_alignment(response.alignment)
    duration = word_timestamps[-1]["end"] if word_timestamps else 0.0
    _save_timestamps(output_path, duration, word_timestamps)

    print(f"  tts [ElevenLabs]: {duration:.2f}s, {len(word_timestamps)} words -> {output_path}")
    return {"audio_path": str(output_path), "duration": duration, "word_timestamps": word_timestamps}


def _parse_el_alignment(alignment) -> list:
    if alignment is None:
        return []
    chars = alignment.characters
    starts = alignment.character_start_times_seconds
    ends = alignment.character_end_times_seconds
    words, current, word_start = [], "", None
    for char, s, e in zip(chars, starts, ends):
        if char in (" ", "\n"):
            if current.strip():
                words.append({"word": current.strip(), "start": round(word_start, 3), "end": round(e, 3)})
            current, word_start = "", None
        else:
            if word_start is None:
                word_start = s
            current += char
    if current.strip() and word_start is not None:
        words.append({"word": current.strip(), "start": round(word_start, 3), "end": round(ends[-1], 3)})
    return words


# ── edge-tts + Whisper backend ────────────────────────────────────────────────

def _generate_edge_tts(script: str, output_path: Path) -> dict:
    print(f"  tts [edge-tts]: generating ({len(script)} chars) with {EDGE_VOICE}...")

    # edge-tts outputs MP3
    mp3_path = output_path.with_suffix(".mp3") if output_path.suffix != ".mp3" else output_path

    asyncio.run(_edge_synthesize(script, mp3_path))

    # Convert to WAV for Whisper (Whisper handles MP3 too but WAV is cleaner)
    wav_path = output_path.with_suffix(".wav")
    subprocess.run([
        "ffmpeg", "-y", "-i", str(mp3_path),
        "-ar", "16000", "-ac", "1", str(wav_path)
    ], capture_output=True, check=True)

    # Get duration
    result = subprocess.run(
        ["ffprobe", "-v", "quiet", "-show_entries", "format=duration",
         "-of", "csv=p=0", str(mp3_path)],
        capture_output=True, text=True
    )
    duration = float(result.stdout.strip())

    print(f"  tts [edge-tts]: {duration:.2f}s audio generated, running Whisper for timestamps...")

    # Whisper word-level alignment
    word_timestamps = _whisper_timestamps(wav_path)

    # Cleanup WAV (keep MP3 as final audio)
    wav_path.unlink(missing_ok=True)

    # Ensure output_path points to the MP3
    if output_path != mp3_path:
        mp3_path.rename(output_path)

    _save_timestamps(output_path, duration, word_timestamps)
    print(f"  tts [edge-tts]: {len(word_timestamps)} words timestamped -> {output_path}")
    return {"audio_path": str(output_path), "duration": duration, "word_timestamps": word_timestamps}


async def _edge_synthesize(script: str, output_path: Path) -> None:
    import edge_tts
    communicate = edge_tts.Communicate(
        text=script,
        voice=EDGE_VOICE,
        rate=EDGE_RATE,
        pitch=EDGE_PITCH,
    )
    await communicate.save(str(output_path))


def _whisper_timestamps(wav_path: Path) -> list:
    from faster_whisper import WhisperModel
    model = WhisperModel("base", device="cpu", compute_type="int8")
    segments, _ = model.transcribe(
        str(wav_path),
        word_timestamps=True,
        language="en",
        vad_filter=True,
    )
    words = []
    for segment in segments:
        if segment.words:
            for w in segment.words:
                clean = w.word.strip().strip(".,!?;:")
                if clean:
                    words.append({
                        "word": clean,
                        "start": round(w.start, 3),
                        "end": round(w.end, 3),
                    })
    return words


# ── Shared helpers ────────────────────────────────────────────────────────────

def _save_timestamps(audio_path: Path, duration: float, words: list) -> None:
    ts_path = audio_path.with_suffix(".json")
    with open(ts_path, "w") as f:
        json.dump({"duration": duration, "words": words}, f, indent=2)


def load_timestamps(json_path: str) -> dict:
    with open(json_path) as f:
        return json.load(f)
