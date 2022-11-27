FROM ubuntu:latest

RUN apt update
RUN apt install python3 -y
RUN apt install python3-pip -y

# OCR specific
RUN apt-get install tesseract-ocr -y
RUN apt-get install ffmpeg libsm6 libxext6  -y
RUN apt-get install poppler-utils -y


WORKDIR /usr/app/src

COPY main.py ./
COPY tempres3.pdf ./
COPY data_store ./
COPY requirements.txt ./

RUN pip install -r requirements.txt

CMD ["python3", "main.py"]