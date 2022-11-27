import sys

import json
import spacy
import re
# from nltk.tokenize import word_tokenize
# from nltk.corpus import stopwords

from functools import reduce 

FILE_NAME = "tempres3.pdf"
USING_OCR = False

if (len(sys.argv) == 1):
    import PyPDF2 
    from PyPDF2 import PdfFileReader

elif (len(sys.argv) == 2):
    FILE_NAME = sys.argv[1]
    import PyPDF2

elif (len(sys.argv) == 3):
    FILE_NAME = sys.argv[1]
    USING_OCR = True
    try:
        from PIL import Image
    except ImportError:
        import Image

    import cv2
    import pytesseract
    import os
    import numpy as np
    import pandas as pd
    import re
    from pdf2image import convert_from_bytes

else :
    print("Usage: python main.py [filename] [ocr]")
    exit()




"""
This function will read the pdf file and convert it into text

params:
    file_name: name of the pdf file

return:
    text: text extracted from the pdf file
"""
def pdf_to_text(file_name) -> str:
    pdfFileObj = open(file_name, 'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    num_pages = pdfReader.numPages
    count = 0
    text = ""
    while count < num_pages:
        pageObj = pdfReader.getPage(count)
        count +=1
        text += pageObj.extractText()
    if text != "":
        text = text
    # else:
    #     text = textract.process(file=file_name, method='tesseract', language='eng')
    return text

"""
This function will convert the resume's text to json format

params:
    text: text extracted from the pdf file

return:
    json: json format of the resume
"""
def textToJson(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    json = {}

    """
    Extracts name of person. 

    Uses the logic that the first two proper nouns in the resume are the name of the person
    """
    for token in doc:
        print(token.text, token.pos_, token.dep_)
        if token.pos_ == 'PROPN':
            if doc[token.i + 1].pos_ == 'PROPN':
                json['name'] = token.text + ' ' + doc[token.i + 1].text
                break
    
    print("name: ", json['name'])
    
"""
Extract skills from technicalskills.json from the resume text

params:
    text: text extracted from the pdf file

return:
    skills: list of skills extracted from the resume
"""
def getSkills(text):
    # print("Starting getskills()")
    skills = [] 
    with open('technicalskills.json') as f:
        data = json.load(f)
        for skill, fullskill in data.items():
            if skill.lower() in text:
                if (fullskill not in skills):
                    skills.append(fullskill)
                    print(fullskill)
    # print("Finished getskills()")



def deskew(image):
    '''deskew the image'''
    gray = cv2.bitwise_not(image)
    temp_arr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    coords = np.column_stack(np.where(temp_arr > 0))
    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle
    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

def pdf_to_text_ocr(file_name):
    # code to convert pdf to text using OCR tesseract 

    # convert pdf into image
    pdf_file = convert_from_bytes(open(file_name, 'rb').read())

    texts = []
    for (i,page) in enumerate(pdf_file) :
        try:
            # transfer image of pdf_file into array
            page_arr = np.asarray(page)
            # transfer into grayscale
            page_arr_gray = cv2.cvtColor(page_arr,cv2.COLOR_BGR2GRAY)
            # deskew the page
            page_deskew = deskew(page_arr_gray)
            # extract string 
            text = pytesseract.image_to_string(page_deskew)
            texts.append(text)
            print(text)
        except:
            # if can't extract then give some notes into df
            print("kat gaya")
            continue
    

def getName(text):
    nlp = spacy.load('en_core_web_sm')
    doc = nlp(text)

    for ent in doc.ents:
        if ent.label_ == 'PERSON':
            return ent.text
    return "Not Found"

def getPhone(text):
    phone = re.search("\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4}", text)
    if phone:
        return phone.group(0)
    return "Not Found"

def getEmail(text):
    email = re.search(r'[\w\.-]+@[\w\.-]+', text)
    if email:
        return email.group(0)
    return "Not Found"

def getLinks():
    doc = PdfFileReader(open(FILE_NAME, "rb"))
    annots = [page.get('/Annots', []) for page in doc.pages]
    annots = reduce(lambda x, y: x + y, annots)
    links = [note.get('/A', {}).get('/URI') for note in annots]
    # print(links)
    return links



if __name__ == '__main__':
    text = ""
    if (USING_OCR):
        text = pdf_to_text_ocr(FILE_NAME)
    else:
        text = pdf_to_text(FILE_NAME)
    print(text)
    print("\n")

    name = getName(text)
    print("Name: ", name)

    phone = getPhone(text)
    print("Phone: ", phone)

    email = getEmail(text)
    print("Email: ", email)

    links = getLinks()
    print("Links: ", links)


    # textToJson(text)
    # getSkills(text.lower())
