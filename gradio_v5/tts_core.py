import os
import subprocess
import tempfile
from pathlib import Path
import soundfile as sf
import shutil
from kokoro import KPipeline

# Set environment variable for HF_HOME
os.environ["HF_HOME"] = os.path.abspath(os.getcwd())

# Organized voice list by language
VOICES = {
    "🇺🇸 American English": [
        "af_bella", "af_nova", "af_alloy", "af_aoede",
        "af_jessica", "af_kore", "af_nicole", "af_river",
        "af_sarah", "af_sky", "am_adam", "am_echo",
        "am_eric", "am_fenrir", "am_liam", "am_michael",
        "am_onyx", "am_puck", "am_santa"
    ],
    "🇬🇧 British English": [
        "bf_alice", "bf_emma", "bf_isabella", "bf_lily",
        "bm_daniel", "bm_fable", "bm_george", "bm_lewis"
    ],
    "🇯🇵 Japanese": [
        "jf_alpha", "jf_gongitsune", "jf_nezumi", "jf_tebukuro",
        "jm_kumo"
    ],
    "🇨🇳 Mandarin Chinese": [
        "zf_xiaobei", "zf_xiaoni", "zf_xiaoxiao", "zf_xiaoyi",
        "zm_yunjian", "zm_yunxi", "zm_yunxia", "zm_yunyang"
    ],
    "🇪🇸 Spanish": ["ef_dora", "em_alex", "em_santa"],
    "🇫🇷 French": ["ff_siwis"],
    "🇮🇳 Hindi": ["hf_alpha", "hf_beta", "hm_omega", "hm_psi"],
    "🇮🇹 Italian": ["if_sara", "im_nicola"],
    "🇧🇷 Portuguese": ["pf_dora", "pm_alex", "pm_santa"]
}

LANG_CODE_MAP = {
    'af_': 'a', 'am_': 'a',  # American English
    'bf_': 'b', 'bm_': 'b',  # British English
    'jf_': 'j', 'jm_': 'j',  # Japanese
    'zf_': 'z', 'zm_': 'z',  # Chinese
    'ef_': 'e', 'em_': 'e',  # Spanish
    'ff_': 'f',              # French
    'hf_': 'h', 'hm_': 'h',  # Hindi
    'if_': 'i', 'im_': 'i',  # Italian
    'pf_': 'p', 'pm_': 'p'   # Portuguese
}

def get_lang_code(voice):
    """Get the language code from the voice name."""
    for prefix, code in LANG_CODE_MAP.items():
        if voice.startswith(prefix):
            return code
    return 'a'

def combine_audio_files(file_list, output_path):
    """Combine multiple WAV files using FFmpeg."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        for audio_file in file_list:
            f.write(f"file '{audio_file}'\n")
        file_list_path = f.name

    try:
        subprocess.run([
            'ffmpeg', '-f', 'concat', '-safe', '0',
            '-i', file_list_path,
            '-c', 'copy',
            output_path
        ], check=True, capture_output=True)
    finally:
        os.unlink(file_list_path)

import tempfile
import shutil
import soundfile as sf
from pathlib import Path

def generate_speech(text, voice, speed):
    """Generate speech with real-time progress updates."""
    if not text.strip():
        yield 0, None  # No input, reset progress
        return

    lang_code = get_lang_code(voice)
    pipeline = KPipeline(lang_code=lang_code)

    # Determine if input contains multiple lines
    text_parts = text.split("\n")
    total_parts = len(text_parts)

    if total_parts == 1:
        # Single-line case: process directly
        yield 10, None  # Initial progress update
        audio = next(pipeline(text, voice=voice, speed=speed), (None, None, None))[2]
        if audio is None or len(audio) == 0:
            yield 100, None  # Finish with no output
            return

        output_path = "output.wav"
        sf.write(output_path, audio, 24000)
        yield 100, output_path  # Progress done
        return

    # Multi-line case: process in chunks and merge
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)
        audio_parts = []

        generator = pipeline(text, voice=voice, speed=speed, split_pattern=r'\n+')

        for i, (gs, ps, audio) in enumerate(generator):
            if audio is None or len(audio) == 0:
                continue  # Skip empty outputs
            
            part_path = temp_dir_path / f'part_{i}.wav'
            sf.write(str(part_path), audio, 24000)
            audio_parts.append(str(part_path))

            # Update progress
            progress_percent = int(((i + 1) / total_parts) * 90)  # Max progress: 90%
            yield progress_percent, None

        if not audio_parts:
            yield 100, None  # No valid audio generated
            return

        # If only one part, return it directly
        if len(audio_parts) == 1:
            final_output = "output.wav"
            shutil.copy2(audio_parts[0], final_output)
            yield 100, final_output
            return

        # Combine multiple parts
        output_path = str(temp_dir_path / 'output.wav')
        combine_audio_files(audio_parts, output_path)

        # Copy the final output to a permanent location
        final_output = "output.wav"
        shutil.copy2(output_path, final_output)

        yield 100, final_output  # Progress complete
