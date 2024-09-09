Want to run it? 
- install the libaries, go into backend/pres and run "pip install -r requirements.txt" (without quotations)
- create a ".env" file in backend/pres, type in GPTAPIKEY="(copy paste you OpenAI API key)" 
- brew install tesseract (middleware)
- run "uvicorn app:app --reload" (runs backend; starts asgi server) (make sure you're in backend/pres)

(Yay backend is running now! Time for frontend)
- brew install node (mac only)
- npm install vite (mac only)