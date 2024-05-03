#pdf reader 
from pypdf import PdfReader # type: ignore
import google.generativeai as genai
reader = PdfReader('Unit-2-Network Layer.pdf')
print(len(reader.pages))#counts the number of pages in the pdf 
page = reader.pages[0]
print(page.extract_text())
result = genai.embed_content(
    model= "models/embedding-001",
    content= "what is the meanni"
)
