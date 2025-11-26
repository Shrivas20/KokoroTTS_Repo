import os
os.environ["HF_HOME"] = os.path.abspath(os.getcwd())
import phonemizer
from kokoro import KPipeline
import soundfile as sf

def generate_speech(text, output_file="output.wav", voice="hf_beta.pt", lang_code="a"):
    pipeline = KPipeline(lang_code=lang_code)
    generator = pipeline(
        text,
        voice=voice,
        speed=1,
        split_pattern=r'\n+'
    )
    
    # Process and save the first generated audio
    for i, (gs, ps, audio) in enumerate(generator):
        sf.write(output_file, audio, 24000)
        break  # Only save the first segment

if __name__ == "__main__":
    text = "Audio has been generated and saved as 'output.wav"
    generate_speech(text)
    print(f"Audio has been generated and saved as 'output.wav'")