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
import shutil
import logging
from io import BytesIO
import aiofiles

load_dotenv()
gptapi_key = os.getenv("GPTAPIKEY")
client = OpenAI(api_key=gptapi_key)

logging.basicConfig(filename='server.log', level=logging.INFO)
app = FastAPI()

origins = ["http://localhost", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def process_image_and_generate_response(image_path, topic, audience, slideno):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    logging.info(text)
    prompt = (
        f"Please provide an eloquent description for {audience}. "
        f"Here is text from an image."
    )
    logging.info(prompt)
    messages = [
        {
            "role": "system",
            "content": """
            I will give you text corresponding to an image. You will
            attempt to use that text to describe that image to the best of your
            abilities.""",
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
        max_tokens=250,
    )
    logging.info(response)
    return response.choices[0].message.content

@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):  
    try:
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)

        async with aiofiles.open(file_path, 'wb') as buffer:
            while content := await file.read(1024):
                await buffer.write(content)

        topic = "learning core concepts"
        audience = "beginners"
        slideno = "first"

        text_response = await process_image_and_generate_response(file_path, topic, audience, slideno)
        logging.info(text_response)
        
        response_file_path = os.path.join(upload_folder, "response.txt")
        async with aiofiles.open(response_file_path, "w") as response_file:
            await response_file.write(text_response)

        return {"message": "File processed", "file_path": response_file_path}
   
    except Exception as e:
        logging.error(f"Error processing file: {e}")
        return {"error": str(e)}

@app.get("/fetchResponse")
async def fetch_response():
    try:
        response_file_path = Path("uploads/response.txt")
        if not response_file_path.exists():
            return {"error": "Response file not found"}
        
        async with aiofiles.open(response_file_path, "r") as file:
            text_response = await file.read()

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