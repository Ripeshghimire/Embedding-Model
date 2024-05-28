from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, UploadFile, Request, HTTPException
import os
import google.generativeai as genai
from pypdf import PdfReader
import uvicorn
from io import BytesIO
from dotenv import load_dotenv
import pandas as pd
from cleantext import cleanpdf_text
from retrieval import chunk_text, embed_text, encode_question,llmresponse
import warnings
import chromadb
import logging
from langchain_community.vectorstores import chroma
load_dotenv()
logging.basicConfig(level=logging.INFO)
warnings.filterwarnings("ignore")
df = pd.DataFrame(columns=['chunk_text', 'embeddings'])
genai.configure(api_key=os.environ["API_KEY"])

app = FastAPI()
chroma_client = chromadb.Client()
collection = chroma_client.create_collection('vector_database')
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
    return templates.TemplateResponse("index.html", {"request": request})

@app.post('/pdf')
async def extract_text(pdfFile: UploadFile):
    """
    Takes input as an uploaded file, extracts the text, cleans it, and returns cleaned text from the PDF file.
    """
    try:
        contents = await pdfFile.read()
        file_like_object = BytesIO(contents)
        reader = PdfReader(file_like_object)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        cleaned_text = cleanpdf_text(text)
        chunked_text = chunk_text(cleaned_text)
        embedded_text,ids = embed_text(chunked_text)

        collection.add(
            documents= chunked_text,
            embeddings=embedded_text,
            ids= ids
     )
        return JSONResponse(content={"embeddings": embedded_text})
    except Exception as e:
        logging.error(f"Error Processing PDF: {e}")
        raise HTTPException(status_code=500, detail="Failed to process PDF")

@app.post('/query')
async def similar_text(request: Request):
    """
    Takes a query from the user, encodes it, and retrieves the most similar text from the database.
    """
    try:
        body = await request.json()
        question = body['question']
        encode_query = encode_question(question)
        logging.info(f"Encoded query: {encode_query}")
        results = collection.query(
            query_embeddings=[encode_query.tolist()],
            n_results=1         
        )
        logging.info(f"Query results: {results}")
        response = results['documents'][0][0] if results['documents'] else "No documents found"
        logging.info(response)
        response_text = llmresponse(response).text
        logging.info(response_text)
        return JSONResponse(content={"results": response_text})
    except Exception as e:
        logging.error(f"Error querying text: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve similar text")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")