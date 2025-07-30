from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from elevenlabs import save, Voice, VoiceSettings
import os
import time

load_dotenv()

elevenlabs = ElevenLabs(
    api_key=os.getenv("ELEVENLABS_API_KEY"),
)

voice_id = os.getenv("ELEVENLABS_VOICE_ID")


def elevenlabs_tts_to_mp3(text, filename, delay=2):
    audio = elevenlabs.text_to_speech.convert(
        text=text,
        voice_id=voice_id,
        model_id="eleven_multilingual_v2",
        output_format="mp3_44100_128",
    )
    save(audio, filename)
    time.sleep(delay)


# if __name__ == "__main__":
#     elevenlabs_tts_to_mp3(
#         text="Ils étaient souvent en retard le matin.", filename="output/mp3/test.mp3"
#     )
