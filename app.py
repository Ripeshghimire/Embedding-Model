from fastapi import FastAPI,UploadFile, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
import google.generativeai as genai
from fastapi.responses import HTMLResponse,JSONResponse
from pypdf import PdfReader
import google.generativeai as genai
import uvicorn 
from io import BytesIO
import json 
# from embedding import embed_and_chunk_text 
import pandas as pd
from cleantext import cleanpdf_text
from retrieval import embed_text,encode_question,get_similar_text
import warnings
import chromadb
warnings.filterwarnings("ignore")
# from datamanager import set_global_df,get_global_df
genai.configure(api_key=os.environ["API_KEY"])
app = FastAPI()
chroma_client = chromadb.Client()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")
global_df = pd.DataFrame()
origins = ["http://127.0.0.1:8000"]
collection = chroma_client.create_collection(name="my_collection")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get('/',response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(request=request,name= 'index.html')

@app.post('/pdf')
async def extract_text(pdfFile:UploadFile):
    '''
    takes input as a upload file extracts the text cleans it and returns cleaned text from the pdf file  
    '''
    contents = await pdfFile.read()
    file_like_object = BytesIO(contents) # BytesIO creates file like object 
    pages = PdfReader(file_like_object).pages
    text = " "
    for page in range(0,len(pages)):
        text += pages[page].extract_text() #extracts the whole pdf text one page at a time 
    clean_text = cleanpdf_text(text)
    text_chunks_df = embed_text(clean_text)
    text_chunks_df['embedding'] = text_chunks_df['embedding'].apply(lambda x: x.tolist())
    data_dict = text_chunks_df.to_dict(orient='records')
    # Serialize the dictionary to JSON
    json_data = json.dumps(data_dict)
    parsed_data = json.loads(json_data)
    data = [i['embeddding'] for i in parsed_data]
    collection.add(data)
    return json_data


@app.post('/similaritychecker')
async def checksimilarity(request:Request):
    '''
        takes input finds the most similar text and gives the output of the code     
    '''
    question = await request.json()
    encoded_question = encode_question(question)
    similarity_text = get_similar_text(encoded_question)
    return similarity_text

if __name__ == '__main__':
    uvicorn.run(app,port=8000)