from langchain_text_splitters import CharacterTextSplitter 
from tqdm import tqdm
import google.generativeai as genai  
import os
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
import pandas as pd 
from sentence_transformers import SentenceTransformer
genai.configure(api_key=os.environ["API_KEY"])
# df = pd.DataFrame(columns=["chunk_text","embedding_vector"])
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 700,
    chunk_overlap = 300,
    length_function = len,
    separators=[
        "\n\n",
        "\n",
        " ",
        ".",
        ",",
        "\u200b",  # Zero-width space
        "\uff0c",  # Fullwidth comma
        "\u3001",  # Ideographic comma
        "\uff0e",  # Fullwidth full stop
        "\u3002",  # Ideographic full stop
        "",
    ],
    is_separator_regex=False
)
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
#Embedding pdf text 
def embed_text(pdfText:str):
    '''
    chunks the given text from the extracted pdf and embeds into vectors using embedding library
    parameter -> takes pdfText as input 
    Returns -> chunk text and embedding vector in df format 
    '''
    data = []
    text = text_splitter.create_documents([pdfText])
    chunk_text = [i.page_content for i in text]
    for text in tqdm(chunk_text):
        embedding = model.encode(text)
        data.append({'chunk_text': text, 'embedding': embedding})
    df = pd.DataFrame(data)
    return df

#Encdoe question function 
def encode_question(query):
    '''
        takes query as a input that is provided by the user in the UI  in the web and encodes it using sentence transfromers
        parameter -> question from the user
        returns -> embedding vector of the user
    '''
    embed_question = model.encode(query)
    return embed_question

#check similarity between question and text embedding vector
def get_similar_text(embed_question,embeds_pdf):
    '''
    compares the question vector embedding and pdftext embedding and finds the most similar answer to the question
    parameter: 
        embed_question-> embedding vector of question 
        embeds_pdf ->  embedding vector of pdf text
    returns:
        the most similar response from the pdf text after comparing question embedding and pdf embedding
    '''    
    


    