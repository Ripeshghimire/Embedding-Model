
from langchain_text_splitters import CharacterTextSplitter 
from tqdm import tqdm
import google.generativeai as genai  
import os
genai.configure(api_key=os.environ["API_KEY"])
def embed_and_chunk_text(text):
    '''Takes a input of the text that is given by the pdf after cleaning and embeds the given token'''
    text_splitter = CharacterTextSplitter(
        separator=".",
        chunk_size=1500,
        chunk_overlap=500,
        length_function=len,
        is_separator_regex=False,
    )
    text_for_embedding = text_splitter.create_documents([text])
    chunk_texts = [chunks.page_content for chunks in text_for_embedding]
    embds = []
    chunk_text = []
    for text in tqdm(chunk_texts):
        try:
            embed_content = genai.embed_content(
                model="models/embedding-001",
                content=text,
                task_type="retrieval_document",
                title="Embedding of pdf document"
            )
            chunk_text.append(text)
            embds.append(embed_content)
        except Exception as e:
            print(f"Error embedding chunk: {e}")
            continue

    if len(chunk_text) != len(embds):
        print(f"Warning: Number of chunks ({len(chunk_text)}) and embeddings ({len(embds)}) do not match.")

    result_dict = {
        "chunk_text": chunk_text,
        "embds": embds
    }
    return result_dict