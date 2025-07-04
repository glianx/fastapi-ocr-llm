from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pdf2image import convert_from_bytes
from pytesseract import image_to_string
from ai_sdk.core.types import UserMessage
from ai_sdk import generate_text
from ai_sdk.openai import openai
from dotenv import load_dotenv
load_dotenv()

app = FastAPI()

@app.get("/")
def index():
    return FileResponse("static/main.html")

@app.post("/upload")
async def upload_pdf(file: UploadFile = File(...)):
    pages_text = []
    pdf_bytes = await file.read()
    images = convert_from_bytes(pdf_bytes)

    for i, image in enumerate(images):
        print(f'processing page {i + 1} of {len(images)}')
        page_text = image_to_string(image)
        pages_text.append(page_text)
    
    message = \
        "Summarize this text: \n" \
        + "<<< start of text >>>\n" \
        + "\n".join(pages_text) \
        + "\n<<< end of text >>>"

    print(message)
    messages=[ UserMessage(role="user", content=message) ]
    response = generate_text(
        model=openai("gpt-4o"),
        messages=messages
    )
    return response.text