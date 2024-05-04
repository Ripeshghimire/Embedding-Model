import markdown
from fastapi import HTTPException
from fastapi import FastAPI, File, UploadFile, Depends, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
import os
import google.generativeai as genai
from fastapi.responses import HTMLResponse,StreamingResponse,JSONResponse
from pypdf import PdfReader
import google.generativeai as genai
import uvicorn 
import re 
import requests
from io import BytesIO
from langchain_text_splitters import CharacterTextSplitter
from tqdm import tqdm
genai.configure(api_key=os.environ["API_KEY"])
app = FastAPI()
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

#clean pdf function 
def cleanpdf_text(text_pdf: str):
    '''cleans pdf text removing unnecessay symbols signs takes text of pdf as input and returns cleaned text as outpu '''
    text = re.sub('[^a-zA-Z.\s]', '', text_pdf)  
    text = text.lower()
    text = ' '.join(text.split())  
    return text

@app.get('/',response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(request=request,name= 'index.html')

@app.post('/pdf')
async def extract_text(pdfFile:UploadFile):
    '''extracts pdffile from the server and extracts the text of the pdffile 
    '''
    contents = await pdfFile.read()
    file_like_object = BytesIO(contents) # BytesIO creates file like object 
    reader = PdfReader(file_like_object)
    pages = reader.pages
    text = ""
    for page in range(1,len(pages)):
        text  += pages[page].extract_text() #extracts the whole pdf text one page at a time 
    return {"text":(cleanpdf_text(text))}

@app.post('/embedding')
async def embed_and_chunk_text(request:Request):
    '''Takes a input of the text that is given by the pdf after cleaning and embeds the given token'''
    data = await request.json()
    extracted_text = data['text']
    text_splitter = CharacterTextSplitter(
        separator=".",
        chunk_size=1500,
        chunk_overlap = 500,
        length_function=len,
        is_separator_regex=False,
    )
    text = text_splitter.create_documents([extracted_text])
    texts = [i.page_content for i in text]
    embds = []
    for text in tqdm(texts):
     try:
        a = genai.embed_content(
        model="models/embedding-001",
        content= text,
        task_type="retrieval_document",
        title="Embedding of pdf document")
        embds.append(a)
     except Exception as e:
        print(e)
        return {"embedded_text":embds}
if __name__ == '__main__':
    uvicorn.run(app,port=8000)
