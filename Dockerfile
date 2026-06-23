FROM ubuntu:22.04

RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-pillow \
    wget \
    gnupg \
    unzip \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Instalar Google Chrome
RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add - && \
    echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list && \
    apt-get update && \
    apt-get install -y google-chrome-stable && \
    rm -rf /var/lib/apt/lists/*

# Instalar ChromeDriver
RUN CHROMEDRIVER_VERSION=$(curl -s "https://chromedriver.chromium.org/download" | grep -oP 'ChromeDriver \K[0-9.]+' | head -1) && \
    wget -O /tmp/chromedriver.zip "https://edgedl.me/chromedriver-repository/linux64/chromedriver_linux64.zip" && \
    unzip /tmp/chromedriver.zip -d /usr/local/bin/ && \
    chmod +x /usr/local/bin/chromedriver && \
    rm /tmp/chromedriver.zip

WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir selenium==4.10.0 reportlab==4.0.4 python-dotenv==1.0.0

COPY print_page.py .
COPY app.py .
COPY config.json .

RUN mkdir -p /tmp/img /tmp/pdf

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

CMD ["python3", "app.py"]