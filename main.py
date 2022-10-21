import PyPDF2 
import textract
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# write code to parse the pdf file
# write code to extract the text from the pdf file

filename = "///Users/avikam/Downloads/tempres.pdf"

pdfFileObj = open(filename,'rb')

pdfReader = PyPDF2.PdfFileReader(pdfFileObj)

num_pages = pdfReader.numPages
count = 0
text = ""

#The while loop will read each page.
while count < num_pages:
    pageObj = pdfReader.getPage(count)
    count +=1
    text += pageObj.extractText()

#This if statement exists to check if the above library returned words. It's done because PyPDF2 cannot read scanned files.
if text != "":
    print(text)
else:
    print("No text found")