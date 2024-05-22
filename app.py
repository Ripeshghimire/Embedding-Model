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
import numpy as np 
import re 
import requests
from io import BytesIO
from langchain_text_splitters import CharacterTextSplitter
from tqdm import tqdm
from embedding import embed_and_chunk_text
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
# from datamanager import set_global_df,get_global_df
genai.configure(api_key=os.environ["API_KEY"])
app = FastAPI()
templates = Jinja2Templates(directory="templates")
# app.mount("/static", StaticFiles(directory="static"), name="static")
global_df = pd.DataFrame()
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
    and embeds it using the embed and chunk text function in embedding
    '''
    global global_df
    contents = await pdfFile.read()
    file_like_object = BytesIO(contents) # BytesIO creates file like object 
    reader = PdfReader(file_like_object)
    pages = reader.pages
    text = ""
    for page in range(0,len(pages)):
        text += pages[page].extract_text() #extracts the whole pdf text one page at a time 
    clean_text = cleanpdf_text(text)
    text = embed_and_chunk_text(clean_text)    
    embedded_text = text['embds']
    chunk_text = text['chunk_text']
    df = pd.DataFrame({
        "embedded_text": [i["embedding"] for i in embedded_text],
        "text_chunks": chunk_text   
    })
    global_df = pd.concat([global_df,df]).reset_index(drop=True)
    # print(global_df)
    return global_df
@app.post('/similarity')
async def similarity(request:Request):
    global global_df
    prompt_template = '''You are an advanced AI model. Your task is to answer the question based on the PDF provided by the user
    . If there is no answer to the user's question, please say that there is no answer.'''

    '''finds similarity between the question and vectors of pdf'''
    question = await request.json()
    question = question['question']
    embed_content= genai.embed_content(
        model="models/embedding-001",
        content= question,
        task_type="retrieval_document",
        title="Embedding of pdf document")  
    # question_embedding.append(embed_content)
    print(global_df)
    print(embed_content)
    # global_df = get_global_df()
    print(global_df)    
    # if 'embedded_text' in global_df.columns:
    a = np.array(embed_content["embedding"]).reshape(1,-1)
    print(a.shape)
    b = np.array([np.array(embed) for embed in global_df['embedded_text']])
    print(b.shape)
    # print(a)
    # print(b)
    print(b)
    similarities = cosine_similarity(a, b)
    # else:
        # Handle the case where the expected column is not found
        # return JSONResponse(status_code=400, content={'error': 'Expected column not found in the DataFrame.'})

    #finding the cosine similarity between question embedding and each PDF text chunk 
    # similarities = []
    # for chunk in global_df['embedded_text']:
    #     cosine_similarity = cosine_similarity(question_embedding,chunk)
    # print(global_df.columns)
    # similarities = cosine_similarity(question_embedding,global_df['embedded_text']).tolist()
        # Find the top k most similar text chunks
    k = 1
    top_k_indices = similarities[0].argsort()[-k:][::-1]
    top_k_similarities = [similarities[0][i] for i in top_k_indices]
    top_k_text_chunks = [global_df['text_chunks'].iloc[i] for i in top_k_indices]

    # Return the top k most similar text chunks and their corresponding similarity scores
    result = [
        {'text_chunk': text_chunk, 'similarity': similarity}
        for text_chunk, similarity in zip(top_k_text_chunks, top_k_similarities)
    ]
    return JSONResponse(content=result)

model = genai.generate_text
if __name__ == '__main__':
    uvicorn.run(app,port=8000)