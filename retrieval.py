import uuid
from tqdm import tqdm
import google.generativeai as genai  
import os
from sentence_transformers import SentenceTransformer
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_text_splitters.base import Document
import numpy as np
import pandas as pd 
from sentence_transformers import SentenceTransformer
import chromadb
import warnings
warnings.filterwarnings('ignore')
genai.configure(api_key=os.environ["API_KEY"])
# df = pd.DataFrame(columns=["chunk_text","embedding_vector"])
chroma_client = chromadb.Client()
collection = chroma_client.create_collection('vector_collection')
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
def chunk_text(pdf_text:str):
    '''
    Chunks the text from the PDF and returns the chunked text.
    Parameters:
    pdf_text (str): Text from the PDF.
    '''
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=700,
        chunk_overlap=500,
        length_function=len,
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
    document = Document(page_content=pdf_text)
    texts = text_splitter.split_documents([document])
    chunked_text = [i.page_content for i in texts ]
    return chunked_text



#Embedding pdf text 
def embed_text(chunked_text: list):
    '''
    Embeds the chunked text that is chunked in {chunk_text} function.
    Parameters:
    chunked_text (list): Chunked text obtained from chunk_text function.
    Returns:
    list: Chunk embedding vectors from the chunk_text.
    '''
    ids = []
    embeddings = []
    for chunk in chunked_text:
        embds = model.encode(chunk)
        # Convert NumPy array to list
        embds_list = embds.tolist()
        embeddings.append(embds_list)
        ids.append(str(uuid.uuid4())) 
    # Assuming collection is defined and initialized earlier
    collection.add(
        embeddings=embeddings,  # Corrected the typo here whow are you ==
        documents=chunked_text,  # Passing the list of chunks as documents
        ids = ids
    )
    return embeddings

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
# def get_similar_text(embed_question):
#     '''
#     compares the question vector embedding and pdftext embedding and finds the most similar answer to the question
#     parameter: 
#         embed_question-> embedding vector of question 
#         embeds_pdf ->  embedding vector of pdf text
    # returns:
#         the most similar response from the pdf text after comparing question embedding and pdf embedding
#     '''    
#     results = collection2.query(
#         query_embeddings = embed_question,
#         n_results=1
#     )                                         
#     return results

    
    