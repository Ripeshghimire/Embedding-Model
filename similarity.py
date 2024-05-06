from sklearn.metrics.pairwise import cosine_similarity
from embedding import embed_and_chunk_text
def similariy(question,embedding):
    '''finding the similarity between question and embedding vector of pdf'''
    question = embed_and_chunk_text(question)
    cosine_similarity(question,embedding)

    
