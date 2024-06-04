from pathlib import Path
from openai import OpenAI
import openai
import pytesseract  # ignore:types
from PIL import Image
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os
load_dotenv()

app = FastAPI()


origins = [
    "http://localhost",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Image-to-text
image = Image.open("/Users/owner/presentation/backend/pres/sample.png")
text = pytesseract.image_to_string(image)

topic = "sustainability"
audience = "beginners"
slideno = "first"
# Initialize the OpenAI client
gptapi_key = os.getenv("GPTAPIKEY")
client = OpenAI(api_key=gptapi_key)
# Define your prompt
prompt = (
    "Please provide an eloquent script for a presentation on"
    + topic
    + "for"
    + audience
    + ". Here is text from an image generated from a slide from that presentation, this is the "
    + slideno
    + "image-text"
)
Trueprompt = prompt + text

# messages dictionary full of prev messages
# messages dictionary full of prev messages
messages = [
    {
        "role": "system",
        "content": """
        You will help me make scripts for various presentations 
        that i can use to give good eloquent presentations. I have
        broken the presentation into several images. I have read the 
        text in those images. I will feed you images one by one and you will 
        generate a script for that specific slide/image. Your response must
        be 10 sentences long max. No more. """,
    },
    {
        "role": "user",
        "content": Trueprompt,
    },
]


# Send the prompt to the GPT-3.5 model
response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=messages,
    temperature=0,
    max_tokens=250,
)

# Print the response
text_response = response.choices[0].message.content


@app.get("/get-house-number")
async def root():
    return text_response

# # Text-to-Image transform to functions
# speech_file_path = Path(__file__).parent / "speech2.mp3"

# with client.audio.speech.with_streaming_response.create(
#     model="tts-1",
#     voice="alloy",
#     input=text_response,
# ) as response:
#     response.stream_to_file(speech_file_path)
