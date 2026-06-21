FROM selenium/standalone-chrome:latest

USER root

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --prefer-binary --no-cache-dir -r requirements.txt

COPY print_page.py .
COPY config.json .

RUN mkdir -p /tmp/img /tmp/pdf

ENV PYTHONUNBUFFERED=1

CMD ["python3", "print_page.py"]