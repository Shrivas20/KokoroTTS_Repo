import sys
import os

os.environ["HF_HOME"] = os.path.abspath(os.getcwd())
import gradio as gr


sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from tts_core import VOICES, generate_speech

# Create the Gradio interface
with gr.Blocks(title="Kokoro TTS", theme="soft") as app:
    gr.Markdown("# 🎤 Kokoro TTS V1.0 - Follow my Youtube Channel -> @HowToIn1Minute")

    with gr.Row():
        with gr.Column():
            text_input = gr.Textbox(
                label="Input Text",
                lines=4,
                placeholder="Enter text to convert... Use newlines to separate parts"
            )
            voice_select = gr.Dropdown(
                label="Select Voice",
                choices=[(f"{lang} - {voice}", voice) for lang in VOICES for voice in VOICES[lang]],
                value="am_puck"
            )
            speed_slider = gr.Slider(
                label="Output Speed",
                minimum=0.5,  # Slowest speed
                maximum=2.0,  # Fastest speed
                value=1.0,    # Default speed
                step=0.1
            )
            generate_btn = gr.Button("Generate Speech", variant="primary")

        with gr.Column():
            progress_bar = gr.Slider(label="Progress", minimum=0, maximum=100, value=0, interactive=False)
            audio_output = gr.Audio(label="Output", autoplay=True)

            gr.Examples(
                examples=[
                    ["Hello world!", "af_bella", 1.0],  # Default speed example
                    ["Hello world!\n\nThis is a multi-part test.", "af_bella", 1.0],
                    ["こんにちは、\n\n元気ですか？", "jf_alpha", 1.0],
                    ["¡Hola amigos!\n\n¿Cómo están?", "ef_dora", 1.0],
                    ["Hello and welcome to my YouTube channel!", "hm_psi", 1.0]
                ],
                inputs=[text_input, voice_select],
                outputs=[progress_bar, audio_output]
            )

    generate_btn.click(
        fn=generate_speech,
        inputs=[text_input, voice_select, speed_slider],
        outputs=[progress_bar, audio_output]
    )

if __name__ == "__main__":
    app.launch(server_name="localhost", server_port=7860, share=False, inbrowser=True, show_error=True)
