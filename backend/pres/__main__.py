from pathlib import Path
import openai
from openai import OpenAI
import pytesseract  # ignore:types
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
text_response = ""

origins = ["http://localhost", "http://localhost:5173"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Function to process image and generate response
def process_image_and_generate_response(image_path, topic, audience, slideno):
    image = Image.open(image_path)
    text = pytesseract.image_to_string(image)
    logging.info(text)
    prompt = (
        f"Please provide an eloquent script for a presentation on {topic} for {audience}. "
        f"Here is text from an image generated from a slide from that presentation, this is the {slideno} image-text: {text}"
    )
    logging.info(prompt)
    messages = [
        {
            "role": "system",
            "content": """
            You will help me make scripts for various presentations 
            that I can use to give good eloquent presentations. I have
            broken the presentation into several images. I have read the 
            text in those images. I will feed you images one by one and you will 
            generate a script for that specific slide/image. Your response must
            be 10 sentences long max. No more. """,
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

# Text-to-Image transform to functions


@app.post("/upload")
async def upload_image(file: UploadFile = File(...)):  
    global text_response
    try:
        upload_folder = "uploads"
        os.makedirs(upload_folder, exist_ok=True)
        file_path = os.path.join(upload_folder, file.filename)
        

        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    

        topic = "learning core concepts"
        audience = "beginners"
        slideno = "first"

        text_response = process_image_and_generate_response(file_path, topic, audience, slideno)
        logging.info(text_response)
        logging.info("skibbidi")
        
        response_file_path = os.path.join(upload_folder, "response.txt")
        with open(response_file_path, "w") as response_file:
            response_file.write(text_response)

        return {"message": "File processed", "file_path": response_file_path}
   
    except Exception as e:
        return {"error": str(e)}

# @app.get("/download_response")
# async def download_response():
#     file_path = "uploads/response.txt"
#     if os.path.exists(file_path):
#         logging.info(FileResponse(file_path, media_type='application/octet-stream', filename="response.txt"))
#         return FileResponse(file_path, media_type='application/octet-stream', filename="response.txt")
        
#     else:
#         logging.info("well")
#         return {"error": "File not found"}
        

@app.get("/fetchResponse")
async def root():

    speech_file_path = Path(__file__).parent / "speech2.mp3"
    with client.audio.speech.with_streaming_response.create(
        model="tts-1",
        voice="alloy",
        input=text_response,
    ) as response:
        response.stream_to_file(speech_file_path)
    return FileResponse(path=speech_file_path, media_type="audio/mpeg")

