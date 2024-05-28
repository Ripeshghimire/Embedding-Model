
#clean pdf function 
import re
def cleanpdf_text(text_pdf: str):
    '''cleans pdf text removing unnecessay symbols signs takes text of pdf as input and returns cleaned text as outpu '''
    text = re.sub('[^0-9a-zA-Z.\s]', ' ', text_pdf)  
    text = text.lower()
    text = ' '.join(text.split())  
    return text