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

@app.get('/',response_class=HTMLResponse)
async def root(request:Request):
    return templates.TemplateResponse(request=request,name= 'index.html')

