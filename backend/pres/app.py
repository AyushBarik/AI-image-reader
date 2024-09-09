from pathlib import Path
import openai
from openai import OpenAI
import pytesseract
from PIL import Image
from fastapi import FastAPI, File, UploadFile, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from dotenv import load_dotenv
import os
import logging
import aiofiles

# Load API key from .env file
load_dotenv()
gptapi_key = os.getenv("GPTAPIKEY")
client = OpenAI(api_key=gptapi_key)

# Set up logging
logging.basicConfig(filename='server.log', level=logging.INFO)
app = FastAPI()

# CORS configuration
origins = ["http://localhost", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Process image and generate text response via GPT
async def process_image_and_generate_response(image_path, topic, audience):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    logging.info(f"Extracted text: {text}")

    if not text.strip():
        logging.error("No text found in the image.")
        return "No text could be extracted from the image."

    prompt = (
        f"""Please provide a description for a {audience} audience who is blind. Be descriptive Pretend you are an assistant helping blind individuals. Your
            job is to provide context about the image as needed and the meaning behind the text. Select what you deem as the most important points of information. """
        f"Here is text from an image. Make a description of it: '{text}'. Keep it brief, explicitly mention any contact info or addresses "
    )
    logging.info(f"Prompt sent to GPT: {prompt}")

    messages = [
        {
            "role": "system",
            "content": """
            I will give you text corresponding to an image. You will
            attempt to use that text to describe that image to the best of your
            abilities. Pretend you are an assistant helping blind individuals. Your
            job is to provide context about the image as needed and the meaning
            behind the text.""",
        },
        {
            "role": "user",
            "content": prompt,
        },
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0,
        max_tokens=600,
    )
    logging.info(f"GPT response: {response}")

    return response.choices[0].message.content if response.choices else "No response from GPT."

# Image upload and process endpoint
@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    try:
        # Save uploaded image to 'uploads' folder
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)

        async with aiofiles.open(file_path, 'wb') as buffer:
            while content := await file.read(1024):
                await buffer.write(content)

        topic = "summarization"
        audience = "beginner"

        text_response = await process_image_and_generate_response(file_path, topic, audience)
        logging.info(f"Text response: {text_response}")

        # Save text response to a file
        response_file_path = os.path.join(upload_folder, "response.txt")
        async with aiofiles.open(response_file_path, "w") as response_file:
            await response_file.write(text_response)

        return {"message": "File processed", "file_path": response_file_path}

    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return {"error": str(e)}

# Fetch the generated speech audio
@app.get("/fetchResponse")
async def fetch_response():
    try:
        # Check if the response.txt file exists
        response_file_path = Path("uploads/response.txt")
        if not response_file_path.exists():
            return {"error": "Response file not found"}

        # Read the text from the response file
        async with aiofiles.open(response_file_path, "r") as file:
            text_response = await file.read()

        if not text_response.strip():
            logging.error("Error: The text response is empty. Cannot generate audio.")
            return {"error": "The text response is empty. Cannot generate audio."}

        # Generate speech from text response
        speech_file_path = Path("uploads/speech.mp3")
        with client.audio.speech.with_streaming_response.create(
            model="tts-1",
            voice="alloy",
            input=text_response,
        ) as response:
            response.stream_to_file(speech_file_path)

        return FileResponse(path=speech_file_path, media_type="audio/mpeg")

    except Exception as e:
        logging.error(f"Error fetching response: {e}")
        return {"error": str(e)}
