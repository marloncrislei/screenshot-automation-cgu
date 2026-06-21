FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3.11 \
    python3-pip \
    python3-pillow \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir selenium==4.10.0 reportlab==4.0.4 python-dotenv==1.0.0

COPY print_page.py .
COPY config.json .

RUN mkdir -p /tmp/img /tmp/pdf

ENV PYTHONUNBUFFERED=1

CMD ["python3", "print_page.py"]