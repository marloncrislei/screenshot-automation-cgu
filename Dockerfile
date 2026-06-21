FROM selenium/standalone-chrome:latest

USER root

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY print_page.py .
COPY app.py .
COPY config.json .

RUN mkdir -p /tmp/img /tmp/pdf

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

CMD ["python3", "app.py"]