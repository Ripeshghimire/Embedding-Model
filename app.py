from fastapi import FastAPI, UploadFile, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from pypdf import PdfReader
import uvicorn
from io import BytesIO
import json
import pandas as pd
from cleantext import cleanpdf_text
from retrieval import chunk_text,embed_text,encode_question
import warnings
import chromadb
import logging
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")
df = pd.DataFrame(columns=['chunk_text','embeddings'])
genai.configure(api_key=os.environ["API_KEY"])

app = FastAPI()
chroma_client = chromadb.Client()
collection = chroma_client.get_collection('vector_collection')
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["http://127.0.0.1:8000"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/', response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse(request=request, name='index.html')

@app.post('/pdf')
async def extract_text(pdfFile: UploadFile):
    """
    Takes input as an uploaded file, extracts the text, cleans it, and returns cleaned text from the PDF file.
    """
    try:
        contents = await pdfFile.read()
        file_like_object = BytesIO(contents)
        pages = PdfReader(file_like_object).pages
        text = ""
        for page in pages:
            text += page.extract_text()
        chunked_text = chunk_text(cleanpdf_text(text))
        embedded_text = embed_text(chunked_text)
        return embedded_text
    except Exception as e :
        logging.error(f"Error Processing pdf {e}")
        raise HTTPException(status_code=500, detail="Failed to process Pdf")
    

async def similar_text(request:Request):
    question = await request.json()
    question = question['question']
    encode_query = encode_question(question)
    logging.INFO(encode_query)
    text = collection.query(
        query_embeddings=encode_query,
        n_results=1
    )
    logging.INFO(text)
    return text['data']
if __name__ == "__main__":
    uvicorn.run(app,port=8000)