FROM python:3.11-slim

# Instalar Chrome e dependências essenciais
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copiar arquivos
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY print_page.py .
COPY config.json .

# Criar diretórios temporários
RUN mkdir -p /tmp/img /tmp/pdf

ENV PYTHONUNBUFFERED=1

CMD ["python", "print_page.py"]