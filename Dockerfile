FROM python:3.11

RUN apt-get update
RUN apt-get install -y chromium-browser chromium-chromedriver
RUN rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY print_page.py .
COPY config.json .

RUN mkdir -p /tmp/img /tmp/pdf

ENV PYTHONUNBUFFERED=1

CMD python print_page.py