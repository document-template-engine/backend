FROM python:3.9

RUN echo "deb http://deb.debian.org/debian bookworm main contrib" | tee /etc/apt/sources.list
RUN  apt-get update
RUN apt-get install -y --no-install-recommends libreoffice-writer
RUN apt-get install -y libreoffice-java-common
RUN apt-get install -y ttf-mscorefonts-installer

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt --no-cache-dir

COPY . .
CMD ["gunicorn", "--bind", "0.0.0.0:9000", "backend.wsgi"]
