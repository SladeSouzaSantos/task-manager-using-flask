FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install system dependencies (if any) and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends gcc libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 1. Define o diretório de trabalho raiz do container
WORKDIR /app

# 2. Copia os requisitos primeiro (Aproveita o cache do Docker)
COPY requirements.txt ./

# 3. Instala as dependências do Python
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 4. Copia toda a estrutura do seu projeto local para dentro do /app
COPY . ./

# Expose the Flask default port
EXPOSE 5000

# 5. Entra na pasta correta ANTES de executar o comando final
WORKDIR /app/todo_project

# 6. Executa o aplicativo (Agora ele vai achar o run.py)
CMD ["python", "run.py"]