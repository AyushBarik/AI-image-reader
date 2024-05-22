from pathlib import Path
from openai import OpenAI

client = OpenAI(api_key="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")

speech_file_path = Path(__file__).parent / "speech.mp3"

with client.audio.speech.with_streaming_response.create(
    model="tts-1",
    voice="alloy",
    input="""My name is Ayush""",
) as response:
    response.stream_to_file(speech_file_path)
