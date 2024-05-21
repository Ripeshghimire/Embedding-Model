from fastapi import FastAPI, UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from fastapi.responses import JSONResponse
from pypdf import PdfReader
import uvicorn
from io import BytesIO
import json
import pandas as pd
from cleantext import cleanpdf_text
from retrieval import embed_text, encode_question
import warnings
import chromadb

warnings.filterwarnings("ignore")

genai.configure(api_key=os.environ["API_KEY"])

app = FastAPI()
chroma_client = chromadb.Client()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = ["http://127.0.0.1:8000"]
collection = chroma_client.create_collection(name="vector_collection")

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
    Takes input as an uploaded file, extracts the text, cleans it, and returns cleaned text from the PDF file
    """
    contents = await pdfFile.read()
    file_like_object = BytesIO(contents)
    pages = PdfReader(file_like_object).pages
    text = ""
    for page in pages:
        text += page.extract_text()
    clean_text = cleanpdf_text(text)
    text_chunks_df = embed_text(clean_text)
    text_chunks_df['embedding'] = text_chunks_df['embedding'].apply(lambda x: x.tolist())
    data_dict = text_chunks_df.to_dict(orient='records')
    json_data = json.dumps(data_dict)
    parsed_data = json.loads(json_data)
    embeddings = [item['embedding'] for item in parsed_data]
    documents = [item['text'] for item in parsed_data]
    collection.add(documents=documents, embeddings=embeddings)
    return JSONResponse(content=json_data)

@app.post('/similaritychecker')
async def check_similarity(request: Request):
    """
    Takes input, finds the most similar text, and gives the output
    """
    request_data = await request.json()
    question = request_data.get('question')
    encoded_question = encode_question(question)
    result = collection.query(query_embeddings=encoded_question, n_results=1)
    return JSONResponse(content=result)

if __name__ == '__main__':
    uvicorn.run(app, port=8000)
